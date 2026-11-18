"""Small, dependency-light statistics helpers."""
from __future__ import annotations

import math

import numpy as np

Z95 = 1.959964


def wilson(k: float, n: int, z: float = Z95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def p_two_sided(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2))


def mean_ci(x) -> dict:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n == 0:
        return {"mean": None, "lo": None, "hi": None, "n": 0}
    m = float(x.mean())
    se = float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else 0.0
    return {"mean": m, "lo": m - Z95 * se, "hi": m + Z95 * se, "n": n}


def paired_diff(a, b) -> dict:
    """Mean of (b - a) over matched seeds with a 95% CI and two-sided p (normal approx)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = b - a
    n = len(d)
    m = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    if se == 0:
        p = 1.0 if m == 0 else 0.0
    else:
        p = p_two_sided(m / se)
    return {"diff": m, "lo": m - Z95 * se, "hi": m + Z95 * se, "p": p, "n": n}


def two_prop(k1: int, n1: int, k2: int, n2: int) -> dict:
    """Unpaired difference p2 - p1."""
    if min(n1, n2) == 0:
        return {"diff": None, "lo": None, "hi": None, "p": None}
    p1, p2 = k1 / n1, k2 / n2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    pp = (k1 + k2) / (n1 + n2)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    p = p_two_sided((p2 - p1) / se0) if se0 > 0 else 1.0
    return {"diff": p2 - p1, "lo": p2 - p1 - Z95 * se, "hi": p2 - p1 + Z95 * se, "p": p}


def holm(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values (same order as input)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj
