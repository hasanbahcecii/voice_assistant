"""Compatibility timing helper using a monotonic clock."""

from time import perf_counter


class Timer:
    def __init__(self, name):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"{self.name}: {perf_counter() - self.start_time:.3f} seconds")
