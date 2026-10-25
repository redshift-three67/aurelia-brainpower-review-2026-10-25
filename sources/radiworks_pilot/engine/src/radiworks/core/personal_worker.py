"""File-free personal CPU worker with retained one-shot and job-stream modes."""
import json
import sys

from .personal_analysis import rank_personal_block, PersonalAnalysisError
from .experimental_matrix import MatrixError
from .personal_stream import (
    MAX_INPUT_BYTES,
    decode_input,
    encode_frame,
)


def execute(envelope, expected_hash):
    if type(envelope) is not dict or set(envelope) != {"input", "indices", "implementationHash"}:
        return {"error": "worker_protocol"}
    if envelope["implementationHash"] != expected_hash:
        return {"error": "implementation_changed"}
    if type(envelope["input"]) is not dict or envelope["input"].get("implementationHash") != expected_hash:
        return {"error": "implementation_changed"}
    try:
        return {"rows": rank_personal_block(envelope["input"], envelope["indices"])}
    except PersonalAnalysisError:
        return {"error": "worker_protocol"}
    except MatrixError:
        return {"error": "cpu_unavailable"}
    except Exception:
        return {"error": "worker_failed"}


def stream_frames(envelope, expected_hash, hash_reader):
    if type(envelope) is not dict or set(envelope) != {"input", "implementationHash"}:
        yield {"error": "worker_protocol"}
        return
    payload = envelope["input"]
    if type(payload) is not dict or envelope["implementationHash"] != expected_hash or payload.get("implementationHash") != expected_hash:
        yield {"error": "implementation_changed"}
        return
    rates = payload.get("rates")
    if type(rates) is not list or not rates:
        yield {"error": "worker_protocol"}
        return
    total = len(rates)
    for start in range(0, total, 21):
        try:
            if hash_reader() != expected_hash:
                yield {"error": "implementation_changed"}
                return
            end = min(start + 21, total)
            rows = rank_personal_block(payload, list(range(start, end)))
        except PersonalAnalysisError:
            yield {"error": "worker_protocol"}
            return
        except MatrixError:
            yield {"error": "cpu_unavailable"}
            return
        except Exception:
            yield {"error": "worker_failed"}
            return
        yield {"rows": rows}
    yield {"done": total}


def _oneshot_main():
    from .personal_controller import personal_implementation_hash

    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        result = {"error": "worker_protocol"} if len(raw) > MAX_INPUT_BYTES else execute(
            json.loads(raw), personal_implementation_hash()
        )
    except Exception:
        result = {"error": "worker_protocol"}
    sys.stdout.write(json.dumps(result, ensure_ascii=False, allow_nan=False))


def _stream_main():
    from .personal_controller import personal_implementation_hash

    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        envelope = decode_input(raw)
    except Exception:
        envelope = None
    if envelope is None:
        frames = ({"error": "worker_protocol"},)
    else:
        expected_hash = personal_implementation_hash()
        frames = stream_frames(envelope, expected_hash, personal_implementation_hash)
    for frame in frames:
        try:
            encoded = encode_frame(frame)
        except Exception:
            encoded = encode_frame({"error": "worker_protocol"})
        try:
            sys.stdout.buffer.write(encoded)
            sys.stdout.buffer.flush()
        except OSError:
            return


def main():
    if sys.argv[1:] == ["--job-stream"]:
        _stream_main()
    elif not sys.argv[1:]:
        _oneshot_main()
    else:
        sys.stdout.write(json.dumps({"error": "worker_protocol"}))


if __name__ == "__main__":
    main()

