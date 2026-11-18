"""Parallel driver for the GlobalSim JSON-lines worker."""
from __future__ import annotations

import json
import os
import subprocess
import threading
from typing import Iterable

from . import catalog as C


class EngineError(RuntimeError):
    pass


def check_engine():
    if not C.ENGINE_BIN.exists():
        raise EngineError(f"engine binary not found at {C.ENGINE_BIN}. Run ./setup.sh "
                          f"(or set UMASIM_ENGINE_BIN / UMASIM_ENGINE_DIR).")


def _worker(jobs: list[tuple], out: list, errors: list):
    """jobs: (slot, request, n_replies). Writes parsed replies into out[slot + k]."""
    try:
        proc = subprocess.Popen([str(C.ENGINE_BIN)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, bufsize=1 << 20)
    except OSError as e:
        errors.append(str(e))
        return

    def feed():
        try:
            for _, req, _ in jobs:
                proc.stdin.write(json.dumps(req, separators=(",", ":")).encode() + b"\n")
            proc.stdin.close()
        except BrokenPipeError:
            pass

    t = threading.Thread(target=feed, daemon=True)
    t.start()
    try:
        for slot, req, n in jobs:
            for k in range(n):
                line = proc.stdout.readline()
                if not line:
                    err = proc.stderr.read().decode(errors="replace")[-2000:]
                    raise EngineError(f"engine exited early (seed {req.get('seed')}): {err}")
                out[slot + k] = json.loads(line)
    except Exception as e:  # noqa: BLE001
        errors.append(repr(e))
        proc.kill()
    finally:
        t.join(timeout=5)
        proc.wait()


def run_requests(reqs: Iterable[dict], workers: int | None = None) -> list[dict]:
    """Run single-seed requests in parallel; returns replies in input order."""
    check_engine()
    reqs = list(reqs)
    workers = max(1, min(workers or os.cpu_count() or 1, len(reqs)))
    out: list = [None] * len(reqs)
    buckets = [[] for _ in range(workers)]
    chunk = -(-len(reqs) // workers)
    for i, r in enumerate(reqs):
        buckets[i // chunk].append((i, r, 1))
    errors: list = []
    threads = [threading.Thread(target=_worker, args=(b, out, errors)) for b in buckets if b]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise EngineError("; ".join(errors[:3]))
    return out


def run_seed_batch(template: dict, seeds: list[int], frames: bool = False, workers: int | None = None) -> list[dict]:
    """Fast path when only the seed changes between races (fixed gates)."""
    check_engine()
    workers = max(1, min(workers or os.cpu_count() or 1, len(seeds)))
    chunk = -(-len(seeds) // workers)
    out: list = [None] * len(seeds)
    buckets = []
    for w in range(workers):
        part = seeds[w * chunk:(w + 1) * chunk]
        if part:
            req = dict(template, seeds=part, threads=1, omitFrames=not frames)
            req.pop("seed", None)
            buckets.append([(w * chunk, req, len(part))])
    errors: list = []
    threads = [threading.Thread(target=_worker, args=(b, out, errors)) for b in buckets]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise EngineError("; ".join(errors[:3]))
    return out


def simulate(compiled, seeds: list[int], frames: bool = False, workers: int | None = None) -> list[dict]:
    if compiled.gates == "fixed":
        tmpl = compiled.request(seeds[0], frames)
        replies = run_seed_batch(tmpl, seeds, frames, workers)
    else:
        replies = run_requests((compiled.request(s, frames) for s in seeds), workers)
    for r in replies:
        if "error" in r:
            raise EngineError(r["error"])
    return replies
