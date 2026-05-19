"""
Aggregate save.ligma into a compact JSON for the portfolio visualization.

For every (gender, age-bucket) combination we count, for each voxel
in an 8x8x8 RGB grid:
  - offered   : how often a color in that voxel was shown
  - round1    : how often a color in that voxel survived round 1 (4 -> 1)
  - round2    : how often it survived round 2 (16 -> 4)
  - final     : how often it was the very last pick

A weighted "love" score is then computed per voxel:
  love = (round1 + 2 * round2 + 4 * final) / max(1, offered)

The script also extracts overall favourite / least-favourite hex colours
and a few session-level stats. The output lands in
main/projects_data/2020-colour-polygraph/preferences.json.
"""

import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "code", "save.ligma")
OUT = os.path.join(HERE, "..", "preferences.json")

GRID = 8
SHIFT = 8 - 3  # quantize 0..255 -> 0..7

AGE_BUCKETS = [
    ("kids",     6,  9),
    ("preteen", 10, 12),
    ("early",   13, 15),
    ("late",    16, 18),
    ("young",   19, 25),
    ("adult",   26, 68),
]

GENDERS = ["g", "j"]


def voxel(rgb):
    r, g, b = rgb
    return (r >> SHIFT, g >> SHIFT, b >> SHIFT)


def vkey(vx):
    return vx[0] * GRID * GRID + vx[1] * GRID + vx[2]


def hex_of(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def age_bucket_for(age):
    for name, lo, hi in AGE_BUCKETS:
        if lo <= age <= hi:
            return name
    return None


def is_valid(row):
    try:
        if row[5] not in ("g", "j"):
            return False
        age = int(row[3])
        if not (5 <= age <= 68):
            return False
        if row[8] == "no data":
            return False
        if len(row[8]) < 4:
            return False
        if len(row[8][0]) < 64 or len(row[8][1]) < 16 or len(row[8][2]) < 4:
            return False
        if len(row[7]) < 2:
            return False
        if int(row[7][-1]) < 15000:
            return False
        return True
    except Exception:
        return False


def empty_bucket():
    return {
        "offered": Counter(),
        "round1":  Counter(),
        "round2":  Counter(),
        "final":   Counter(),
        "n":       0,
        "mood":    0,
    }


def main():
    with open(SOURCE, "r", encoding="utf-8") as fh:
        rows = json.load(fh)

    print(f"loaded {len(rows)} raw rows")

    buckets = {}
    for g in GENDERS:
        for name, _, _ in AGE_BUCKETS:
            buckets[(g, name)] = empty_bucket()

    overall_final = Counter()
    overall_offered = Counter()
    overall_picked = Counter()
    voxel_offered = Counter()
    voxel_round1 = Counter()
    voxel_round2 = Counter()
    voxel_final = Counter()
    used = 0

    for row in rows:
        if not is_valid(row):
            continue
        gender = row[5]
        age = int(row[3])
        ab = age_bucket_for(age)
        if ab is None:
            continue

        offered_arr = row[8][0]
        round1_arr  = row[8][1]
        round2_arr  = row[8][2]
        final_rgb   = row[8][3]

        b = buckets[(gender, ab)]
        b["n"] += 1
        b["mood"] += int(row[4]) if str(row[4]).lstrip("-").isdigit() else 0

        round1_set = {tuple(c) for c in round1_arr}
        round2_set = {tuple(c) for c in round2_arr}
        final_tuple = tuple(final_rgb)

        for c in offered_arr:
            tc = tuple(c)
            v = vkey(voxel(tc))
            b["offered"][v] += 1
            voxel_offered[v] += 1
            overall_offered[hex_of(tc)] += 1
            if tc in round1_set:
                b["round1"][v] += 1
                voxel_round1[v] += 1
                overall_picked[hex_of(tc)] += 1
            if tc in round2_set:
                b["round2"][v] += 1
                voxel_round2[v] += 1
            if tc == final_tuple:
                b["final"][v] += 1
                voxel_final[v] += 1
                overall_final[hex_of(tc)] += 1

        used += 1

    print(f"used {used} valid rows")

    out_buckets = {}
    for (gender, age_name), b in buckets.items():
        n = b["n"]
        love = {}
        for v, off in b["offered"].items():
            score = b["round1"].get(v, 0) + 2 * b["round2"].get(v, 0) + 4 * b["final"].get(v, 0)
            ratio = score / off
            if ratio > 0:
                love[v] = round(ratio, 4)
        key = f"{gender}_{age_name}"
        out_buckets[key] = {
            "n": n,
            "mood_mean": round((b["mood"] / n) if n else 0, 2),
            "love": love,
        }

    voxel_rows = []
    for v, off in voxel_offered.items():
        if off < 200:
            continue
        r1 = voxel_round1.get(v, 0)
        r2 = voxel_round2.get(v, 0)
        fn = voxel_final.get(v, 0)
        love = (r1 + 2 * r2 + 4 * fn) / off
        reject_ratio = r1 / off
        r = ((v // (GRID * GRID)) & 7)
        g = ((v // GRID) & 7)
        b = (v & 7)
        center = ((r * 32) + 16, (g * 32) + 16, (b * 32) + 16)
        voxel_rows.append((hex_of(center), love, reject_ratio, off, r1, fn))

    voxel_rows.sort(key=lambda x: x[1], reverse=True)
    fav_list = [
        {"hex": h, "ratio": round(love, 4), "offered": off, "finals": fn}
        for h, love, _, off, _, fn in voxel_rows[:12]
    ]

    voxel_rows.sort(key=lambda x: x[2])
    least_list = [
        {"hex": h, "ratio": round(rej, 4), "offered": off, "picked": r1}
        for h, _, rej, off, r1, _ in voxel_rows[:12]
    ]

    age_dist = Counter()
    gender_dist = Counter()
    mood_total = 0
    mood_n = 0
    for row in rows:
        if not is_valid(row):
            continue
        age_dist[int(row[3])] += 1
        gender_dist[row[5]] += 1
        if str(row[4]).lstrip("-").isdigit():
            mood_total += int(row[4])
            mood_n += 1

    out = {
        "grid": GRID,
        "age_buckets": [
            {"name": n, "lo": lo, "hi": hi}
            for n, lo, hi in AGE_BUCKETS
        ],
        "buckets": out_buckets,
        "favourites": fav_list,
        "least_favourites": least_list,
        "stats": {
            "total_valid": used,
            "raw_rows": len(rows),
            "gender": dict(gender_dist),
            "age_hist": dict(sorted(age_dist.items())),
            "mood_mean": round(mood_total / max(1, mood_n), 2),
        },
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))

    size_kb = os.path.getsize(OUT) / 1024
    print(f"wrote {OUT} ({size_kb:.1f} kB)")


if __name__ == "__main__":
    main()
