"""Rect helpers for keeping an output layout non-overlapping."""

from __future__ import annotations


def v_overlap(a: dict, b: dict) -> bool:
    return not (a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])


def h_overlap(a: dict, b: dict) -> bool:
    return not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"])


def overlaps(a: dict, b: dict) -> bool:
    return not (
        a["x"] + a["w"] <= b["x"]
        or b["x"] + b["w"] <= a["x"]
        or a["y"] + a["h"] <= b["y"]
        or b["y"] + b["h"] <= a["y"]
    )


def separate_overlaps(
    rects: list[dict], order: dict[str, int]
) -> list[tuple[str, int, int, str]]:
    moved: dict[str, tuple[int, int, str]] = {}
    for _ in range(len(rects) * len(rects) + 8):
        pair = None
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if overlaps(rects[i], rects[j]):
                    pair = (rects[i], rects[j])
                    break
            if pair:
                break
        if pair is None:
            break
        first, second = pair
        if order.get(second["name"], 0) >= order.get(first["name"], 0):
            mover, other = second, first
        else:
            mover, other = first, second

        candidates = [
            (other["x"] + other["w"], mover["y"]),
            (other["x"] - mover["w"], mover["y"]),
            (mover["x"], other["y"] + other["h"]),
            (mover["x"], other["y"] - mover["h"]),
        ]

        clear = []
        for nx, ny in candidates:
            probe = dict(mover, x=nx, y=ny)
            if not any(overlaps(probe, r) for r in rects if r is not mover):
                clear.append((abs(nx - mover["x"]) + abs(ny - mover["y"]), nx, ny))

        if clear:
            _, mover["x"], mover["y"] = min(clear)
        else:
            _, mover["x"], mover["y"] = min(
                (abs(nx - mover["x"]) + abs(ny - mover["y"]), nx, ny)
                for nx, ny in candidates
            )

        moved[mover["name"]] = (mover["x"], mover["y"], other["name"])
    return [(n, x, y, o) for n, (x, y, o) in moved.items()]
