"""Keep ownership until the owned CPU child is confirmed finished."""
import time


def reap_owned_process(process):
    if process is None:
        return
    failure = None
    try:
        if process.poll() is not None:
            return
    except OSError as exc:
        failure = exc  # Unknown state still requires confirmed process exit.
    try:
        process.kill()
    except OSError as exc:
        if failure is None:
            failure = exc
    try:
        # Drain pipes even if termination failed; waiting alone can deadlock stdout.
        process.communicate()
    except OSError as exc:
        if failure is None:
            failure = exc
    while True:
        try:
            process.wait()
            break
        except OSError as exc:
            if failure is None:
                failure = exc
            time.sleep(0.1)  # Never release the runtime lease on an unconfirmed child.
    if failure is not None:
        raise RuntimeError('Owned CPU cleanup failed after confirmed process exit') from failure
