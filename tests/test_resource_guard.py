import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("guard", ROOT / "scripts/run_guarded.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def test_memory_unit_conversion(tmp_path):
    info = tmp_path / "meminfo"
    info.write_text("MemTotal: 16000000 kB\nMemAvailable: 3145728 kB\n")
    assert guard.available_bytes(info) == 3 * 1024**3


def test_guard_refuses_launch_below_reserve(monkeypatch):
    monkeypatch.setattr(guard, "available_bytes", lambda: 2 * 1024**3)
    monkeypatch.setattr(
        guard.subprocess, "Popen", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("must not start"))
    )
    assert guard.run(["unused"]) == 75


def test_guard_child_observes_cpu_priority_and_no_gpu():
    command = [
        sys.executable,
        str(ROOT / "scripts/run_guarded.py"),
        "--cpus",
        "1",
        "--",
        sys.executable,
        "-c",
        'import os; assert len(os.sched_getaffinity(0)) == 1; assert os.getpriority(os.PRIO_PROCESS, 0) >= 15; assert os.environ["CUDA_VISIBLE_DEVICES"] == ""; assert os.environ["OMP_NUM_THREADS"] == "1"',
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr


def test_guard_stops_own_child_on_low_memory(monkeypatch):
    readings = iter([4 * 1024**3, 2 * 1024**3])
    monkeypatch.setattr(guard, "available_bytes", lambda: next(readings))
    monkeypatch.setattr(guard.os, "sched_setaffinity", lambda *_: None)
    monkeypatch.setattr(guard.os, "setpriority", lambda *_: None)
    stopped = []
    child = type("Child", (), {"poll": lambda _: None})()
    monkeypatch.setattr(guard.subprocess, "Popen", lambda *a, **kw: child)
    monkeypatch.setattr(guard, "stop_group", lambda p: stopped.append(p))
    assert guard.run(["unused"]) == 75
    assert stopped == [child]
