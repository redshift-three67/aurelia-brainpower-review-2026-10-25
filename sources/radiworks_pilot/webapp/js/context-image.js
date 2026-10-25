const MAX_INPUT_BYTES = 5_000_000;
const MAX_OUTPUT_BYTES = 5_000_000;
const MAX_SIDE = 4096;
const MAX_PIXELS = 16_000_000;
const MAX_NORMALIZED_SIDE = 1024;
const FOCUS_IMAGE_ERROR_NAME = 'FocusImageError';

const ERRORS = Object.freeze({
  invalidFile: 'Bitte wählen Sie eine gültige Bilddatei aus.',
  tooLarge: 'Die Bilddatei ist größer als die erlaubten 5 MB.',
  unsupported: 'Dieser Bildtyp wird nicht unterstützt.',
  mismatch: 'Der deklarierte Dateityp passt nicht zum Bildinhalt.',
  invalidImage: 'Das Bild ist beschädigt oder kann nicht gelesen werden.',
  dimensions: 'Die Bildabmessungen überschreiten die erlaubte Grenze.',
  animated: 'Animierte Bilder werden nicht unterstützt.',
  outputTooLarge: 'Das aufbereitete Bild ist größer als die erlaubten 5 MB.',
});

function fail(message) {
  const error = new Error(message);
  error.name = FOCUS_IMAGE_ERROR_NAME;
  throw error;
}

function failInvalidImage() {
  fail(ERRORS.invalidImage);
}

function viewOf(bytes) {
  return new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
}

function fourCC(bytes, offset) {
  return String.fromCharCode(bytes[offset], bytes[offset + 1], bytes[offset + 2], bytes[offset + 3]);
}

function assertDimensions(width, height) {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0) {
    failInvalidImage();
  }
  if (width > MAX_SIDE || height > MAX_SIDE || width * height > MAX_PIXELS) {
    fail(ERRORS.dimensions);
  }
  return { width, height };
}

function sniffMimeType(bytes) {
  if (bytes.length >= 8
    && bytes[0] === 137 && bytes[1] === 80 && bytes[2] === 78 && bytes[3] === 71
    && bytes[4] === 13 && bytes[5] === 10 && bytes[6] === 26 && bytes[7] === 10) {
    return 'image/png';
  }
  if (bytes.length >= 2 && bytes[0] === 0xff && bytes[1] === 0xd8) return 'image/jpeg';
  if (bytes.length >= 12 && fourCC(bytes, 0) === 'RIFF' && fourCC(bytes, 8) === 'WEBP') {
    return 'image/webp';
  }
  return null;
}

function parsePngDimensions(bytes) {
  if (bytes.length < 33) failInvalidImage();
  const view = viewOf(bytes);
  if (view.getUint32(8, false) !== 13 || fourCC(bytes, 12) !== 'IHDR') failInvalidImage();
  const dimensions = assertDimensions(view.getUint32(16, false), view.getUint32(20, false));

  let offset = 8;
  let sawData = false;
  let sawEnd = false;
  while (offset < bytes.length) {
    if (offset + 12 > bytes.length) failInvalidImage();
    const length = view.getUint32(offset, false);
    if (length > bytes.length - offset - 12) failInvalidImage();
    const type = fourCC(bytes, offset + 4);
    if (type === 'acTL' || type === 'fcTL' || type === 'fdAT') fail(ERRORS.animated);
    if (type === 'IDAT') sawData = true;
    if (type === 'IEND') {
      if (length !== 0) failInvalidImage();
      sawEnd = true;
      offset += 12;
      break;
    }
    offset += length + 12;
  }
  if (!sawData || !sawEnd || offset !== bytes.length) failInvalidImage();
  return dimensions;
}

const JPEG_SOF_MARKERS = new Set([
  0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
  0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf,
]);

function parseJpegDimensions(bytes) {
  if (bytes.length < 4 || bytes[0] !== 0xff || bytes[1] !== 0xd8) failInvalidImage();
  const view = viewOf(bytes);
  let offset = 2;
  while (offset < bytes.length) {
    if (bytes[offset] !== 0xff) failInvalidImage();
    while (offset < bytes.length && bytes[offset] === 0xff) offset += 1;
    if (offset >= bytes.length) failInvalidImage();
    const marker = bytes[offset];
    offset += 1;
    if (marker === 0x00) failInvalidImage();
    if (marker === 0xd9 || marker === 0xda) break;
    if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd8)) continue;
    if (offset + 2 > bytes.length) failInvalidImage();
    const segmentLength = view.getUint16(offset, false);
    if (segmentLength < 2 || segmentLength > bytes.length - offset) failInvalidImage();
    if (JPEG_SOF_MARKERS.has(marker)) {
      if (segmentLength < 8) failInvalidImage();
      return assertDimensions(view.getUint16(offset + 3, false), view.getUint16(offset + 5, false));
    }
    offset += segmentLength;
  }
  failInvalidImage();
}

function parseWebpDimensions(bytes) {
  if (bytes.length < 30 || fourCC(bytes, 0) !== 'RIFF' || fourCC(bytes, 8) !== 'WEBP') failInvalidImage();
  const view = viewOf(bytes);
  const riffEnd = view.getUint32(4, true) + 8;
  if (riffEnd !== bytes.length || riffEnd < 12) failInvalidImage();
  let offset = 12;
  let canvasDimensions = null;
  let bitstreamDimensions = null;
  let bitstreamChunks = 0;
  let animated = false;
  while (offset < riffEnd) {
    if (offset + 8 > riffEnd) failInvalidImage();
    const type = fourCC(bytes, offset);
    const length = view.getUint32(offset + 4, true);
    const payload = offset + 8;
    if (length > riffEnd - payload) failInvalidImage();
    if (type === 'ANIM' || type === 'ANMF') animated = true;
    if (type === 'VP8X') {
      if (offset !== 12 || canvasDimensions || length < 10) failInvalidImage();
      if (bytes[payload] & 0x02) animated = true;
      const width = 1 + bytes[payload + 4] + (bytes[payload + 5] << 8) + (bytes[payload + 6] << 16);
      const height = 1 + bytes[payload + 7] + (bytes[payload + 8] << 8) + (bytes[payload + 9] << 16);
      canvasDimensions = assertDimensions(width, height);
    } else if (type === 'VP8L') {
      bitstreamChunks += 1;
      if (bitstreamChunks > 1 || length < 5 || bytes[payload] !== 0x2f) failInvalidImage();
      const width = 1 + ((bytes[payload + 2] & 0x3f) << 8) + bytes[payload + 1];
      const height = 1 + ((bytes[payload + 4] & 0x0f) << 10)
        + (bytes[payload + 3] << 2) + ((bytes[payload + 2] & 0xc0) >> 6);
      bitstreamDimensions = assertDimensions(width, height);
    } else if (type === 'VP8 ') {
      bitstreamChunks += 1;
      if (bitstreamChunks > 1 || length < 10 || bytes[payload + 3] !== 0x9d
        || bytes[payload + 4] !== 0x01 || bytes[payload + 5] !== 0x2a) failInvalidImage();
      bitstreamDimensions = assertDimensions(
        view.getUint16(payload + 6, true) & 0x3fff,
        view.getUint16(payload + 8, true) & 0x3fff,
      );
    }
    offset = payload + length + (length & 1);
    if (offset > riffEnd) failInvalidImage();
  }
  if (offset !== riffEnd) failInvalidImage();
  if (animated) fail(ERRORS.animated);
  if (bitstreamChunks !== 1 || !bitstreamDimensions) failInvalidImage();
  if (canvasDimensions && (canvasDimensions.width !== bitstreamDimensions.width
    || canvasDimensions.height !== bitstreamDimensions.height)) failInvalidImage();
  return canvasDimensions || bitstreamDimensions;
}

function parseDimensions(bytes, mimeType) {
  if (mimeType === 'image/png') return parsePngDimensions(bytes);
  if (mimeType === 'image/jpeg') return parseJpegDimensions(bytes);
  return parseWebpDimensions(bytes);
}

function toBase64(bytes) {
  let binary = '';
  const chunkSize = 0x8000;
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
  }
  return btoa(binary);
}

async function toPngBlob(canvas) {
  return new Promise((resolve, reject) => {
    try {
      canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error('Canvas export failed')), 'image/png');
    } catch (error) {
      reject(error);
    }
  });
}

function sha256Hex(bytes) {
  return crypto.subtle.digest('SHA-256', bytes).then((digest) => (
    Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('')
  ));
}

export async function prepareFocusImage(file) {
  if (!file || typeof file.arrayBuffer !== 'function' || !Number.isSafeInteger(file.size) || file.size <= 0) {
    fail(ERRORS.invalidFile);
  }
  if (file.size > MAX_INPUT_BYTES) fail(ERRORS.tooLarge);

  const declaredType = typeof file.type === 'string' ? file.type.toLowerCase() : '';
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(declaredType)) fail(ERRORS.unsupported);

  let inputBytes;
  try {
    inputBytes = new Uint8Array(await file.arrayBuffer());
  } catch {
    fail(ERRORS.invalidImage);
  }
  if (inputBytes.byteLength !== file.size || inputBytes.byteLength > MAX_INPUT_BYTES) fail(ERRORS.invalidImage);

  const detectedType = sniffMimeType(inputBytes);
  if (detectedType !== declaredType) fail(ERRORS.mismatch);
  const sourceDimensions = parseDimensions(inputBytes, declaredType);
  if (sourceDimensions.width * sourceDimensions.height > MAX_PIXELS) fail(ERRORS.dimensions);

  let bitmap;
  let canvas;
  try {
    try {
      bitmap = await createImageBitmap(file);
    } catch {
      fail(ERRORS.invalidImage);
    }
    if (!bitmap || !bitmap.width || !bitmap.height) fail(ERRORS.invalidImage);
    assertDimensions(bitmap.width, bitmap.height);

    const scale = Math.min(1, MAX_NORMALIZED_SIDE / Math.max(bitmap.width, bitmap.height));
    const width = Math.max(1, Math.round(bitmap.width * scale));
    const height = Math.max(1, Math.round(bitmap.height * scale));
    canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    if (!context) fail(ERRORS.invalidImage);
    context.drawImage(bitmap, 0, 0, width, height);

    let pngBlob;
    try {
      pngBlob = await toPngBlob(canvas);
    } catch {
      fail(ERRORS.invalidImage);
    }
    if (pngBlob.type !== 'image/png') fail(ERRORS.invalidImage);
    if (pngBlob.size > MAX_OUTPUT_BYTES) fail(ERRORS.outputTooLarge);

    let outputBytes;
    try {
      outputBytes = new Uint8Array(await pngBlob.arrayBuffer());
    } catch {
      fail(ERRORS.invalidImage);
    }
    if (outputBytes.byteLength !== pngBlob.size || outputBytes.byteLength > MAX_OUTPUT_BYTES) {
      fail(ERRORS.outputTooLarge);
    }

    let sha256;
    try {
      sha256 = await sha256Hex(outputBytes);
    } catch {
      fail(ERRORS.invalidImage);
    }
    const pngBase64 = toBase64(outputBytes);
    return {
      pngBase64,
      image: { sha256, mediaType: 'image/png', byteLength: outputBytes.byteLength },
      previewUrl: 'data:image/png;base64,' + pngBase64,
    };
  } catch (error) {
    if (error?.name === FOCUS_IMAGE_ERROR_NAME) throw error;
    fail(ERRORS.invalidImage);
  } finally {
    try { bitmap?.close(); } catch { /* Browser bitmap resources should still be released. */ }
    if (canvas) {
      canvas.width = 0;
      canvas.height = 0;
    }
  }
}
