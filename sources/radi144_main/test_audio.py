import winsound
import math
import struct
import time

def generate_sine_wave(frequency, duration=1.0, sample_rate=44100, amplitude=0.5):
    n_samples = int(sample_rate * duration)
    # Generate wav header
    # RIFF chunk
    header = b'RIFF'
    header += struct.pack('<I', 36 + n_samples * 2) # ChunkSize
    header += b'WAVE'
    # fmt chunk
    header += b'fmt '
    header += struct.pack('<I', 16) # Subchunk1Size (16 for PCM)
    header += struct.pack('<H', 1) # AudioFormat (1 for PCM)
    header += struct.pack('<H', 1) # NumChannels (1 for Mono)
    header += struct.pack('<I', sample_rate) # SampleRate
    header += struct.pack('<I', sample_rate * 2) # ByteRate (SampleRate * NumChannels * BitsPerSample/8)
    header += struct.pack('<H', 2) # BlockAlign (NumChannels * BitsPerSample/8)
    header += struct.pack('<H', 16) # BitsPerSample
    # data chunk
    header += b'data'
    header += struct.pack('<I', n_samples * 2) # Subchunk2Size

    data = bytearray()
    for i in range(n_samples):
        t = float(i) / sample_rate
        value = int(amplitude * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
        data.extend(struct.pack('<h', value))
    
    return header + data

print("Testing winsound.Beep (Current Implementation)...")
try:
    for _ in range(5):
        winsound.Beep(440, 200)
except KeyboardInterrupt:
    pass

print("Testing winsound.PlaySound with generated WAV (Proposed)...")
wav_data = generate_sine_wave(440, duration=1.0) # 1 sec loop buffer

# SND_MEMORY = 0x0004
# SND_LOOP = 0x0008
# SND_ASYNC = 0x0001
# SND_PURGE = 0x0040

flags = winsound.SND_MEMORY | winsound.SND_LOOP | winsound.SND_ASYNC

winsound.PlaySound(bytes(wav_data), flags)
time.sleep(3)
winsound.PlaySound(None, 0) # Stop
print("Done.")
