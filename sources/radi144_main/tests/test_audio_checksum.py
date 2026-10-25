import struct
import numpy as np


def generate_test_wave(frequency=440.0, duration=1.0, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    audio = 0.1 * np.sin(2 * np.pi * frequency * t)
    audio_int16 = (audio * 32767).astype(np.int16)
    header = (
        b'RIFF'
        + struct.pack('<I', 36 + n_samples * 2)
        + b'WAVEfmt '
        + struct.pack('<I', 16)
        + struct.pack('<H', 1)
        + struct.pack('<H', 1)
        + struct.pack('<I', sample_rate)
        + struct.pack('<I', sample_rate * 2)
        + struct.pack('<H', 2)
        + struct.pack('<H', 16)
        + b'data'
        + struct.pack('<I', n_samples * 2)
    )
    return header + audio_int16.tobytes()


def test_wav_header_integrity():
    wav_bytes = generate_test_wave()
    assert wav_bytes[:4] == b'RIFF'
    size = struct.unpack('<I', wav_bytes[4:8])[0]
    # file size should be total bytes - 8
    assert size + 8 == len(wav_bytes)
    assert wav_bytes[8:12] == b'WAVE'
