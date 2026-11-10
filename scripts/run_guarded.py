"""Run a local check at low priority, with bounded CPU and a RAM reserve.

Linux-only process guard. It stops its own process group, never unrelated jobs.
Usage: python scripts/run_guarded.py --cpus 2 --reserve-gib 3 -- python -m pytest -q
"""

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def available_bytes(path=Path("/proc/meminfo")):
    for line in path.read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable is unavailable; refusing to launch without the RAM guard.")


def stop_group(process):
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def run(command, cpus=2, reserve_gib=3, interval=0.5):
    if not sys.platform.startswith("linux"):
        raise RuntimeError("This resource guard currently requires Linux.")
    reserve = int(reserve_gib * 1024**3)
    if available_bytes() < reserve:
        print("RAM reserve is already below the limit; job not started.", file=sys.stderr)
        return 75
    affinity = sorted(os.sched_getaffinity(0))[:cpus]
    os.sched_setaffinity(0, affinity)
    os.setpriority(os.PRIO_PROCESS, 0, max(os.getpriority(os.PRIO_PROCESS, 0), 15))
    env = dict(os.environ)
    for name in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
        env[name] = str(len(affinity))
    env["CUDA_VISIBLE_DEVICES"] = ""
    env["GRADIO_ANALYTICS_ENABLED"] = "False"
    env.pop("PYTHONPATH", None)
    process = subprocess.Popen(command, env=env, start_new_session=True)
    try:
        while process.poll() is None:
            if available_bytes() < reserve:
                print("RAM reserve fell below the limit; stopping this job only.", file=sys.stderr)
                stop_group(process)
                return 75
            time.sleep(interval)
        return process.returncode
    except BaseException:
        stop_group(process)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpus", type=int, default=2)
    parser.add_argument("--reserve-gib", type=float, default=3)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not 1 <= args.cpus <= 4:
        parser.error("--cpus must be between 1 and 4")
    if args.reserve_gib < 3:
        parser.error("--reserve-gib cannot be below 3")
    if not command:
        parser.error("provide a command after --")
    return run(command, args.cpus, args.reserve_gib)


if __name__ == "__main__":
    raise SystemExit(main())
