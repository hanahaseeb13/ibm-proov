# log_util.py
# Timestamped logger for the KM-Waechter service.

import time

LOG_LINES: list[str] = []          # module-level buffer; flushed to disk by flush_log()
DEBUG = False


def log(message: str) -> None:
    """Append a timestamped entry to the in-memory log buffer and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a DEBUG-level message (only active when DEBUG is True)."""
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Write all buffered log lines to the given file path and clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
