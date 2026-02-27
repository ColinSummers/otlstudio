#!/usr/bin/env python3
"""Search candidate folders for larger versions of site images using perceptual hashing."""

import os
import sqlite3
import sys
import imagehash
from PIL import Image

SITE_ROOT = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(os.path.dirname(__file__), "images.db")

# Maximum hamming distance to consider a match
THRESHOLD = 12


def scan_candidates(search_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []

    conn = sqlite3.connect(DB_PATH)

    # Create candidates table
    conn.execute("DROP TABLE IF EXISTS candidates")
    conn.execute("""
        CREATE TABLE candidates (
            path        TEXT PRIMARY KEY,
            filename    TEXT,
            width       INTEGER,
            height      INTEGER,
            phash       TEXT
        )
    """)

    # Scan candidate directory
    extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
    count = 0
    skipped = 0
    for root, dirs, files in os.walk(search_dir):
        # Skip excluded directories
        skip = False
        for ex in exclude_dirs:
            if root.startswith(ex):
                skip = True
                break
        if skip:
            continue

        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in extensions:
                continue
            fpath = os.path.join(root, fname)
            try:
                img = Image.open(fpath)
                img.load()
                w, h = img.size
                phash = str(imagehash.phash(img))
            except Exception:
                skipped += 1
                continue

            conn.execute(
                "INSERT OR REPLACE INTO candidates VALUES (?, ?, ?, ?, ?)",
                (fpath, fname, w, h, phash),
            )
            count += 1
            if count % 200 == 0:
                print(f"  Scanned {count} images...")
                conn.commit()

    conn.commit()
    print(f"Scanned {count} candidate images ({skipped} skipped)")

    # Find matches: site images (non-thumb, not in big/) matched against larger candidates
    site_rows = conn.execute(
        "SELECT path, project, width, height, phash FROM site_images "
        "WHERE is_thumb = 0 AND path NOT LIKE 'images/big/%' AND path NOT LIKE 'media/%'"
    ).fetchall()

    cand_rows = conn.execute(
        "SELECT path, width, height, phash FROM candidates"
    ).fetchall()

    # Convert candidate hashes for comparison
    cand_hashes = []
    for cpath, cw, ch, cphash in cand_rows:
        cand_hashes.append((cpath, cw, ch, imagehash.hex_to_hash(cphash)))

    print(f"Comparing {len(site_rows)} site images against {len(cand_hashes)} candidates...")

    # Create matches table
    conn.execute("DROP TABLE IF EXISTS matches")
    conn.execute("""
        CREATE TABLE matches (
            site_path       TEXT,
            site_project    TEXT,
            site_width      INTEGER,
            site_height     INTEGER,
            candidate_path  TEXT,
            cand_width      INTEGER,
            cand_height     INTEGER,
            hamming         INTEGER
        )
    """)

    match_count = 0
    for i, (spath, project, sw, sh, sphash_hex) in enumerate(site_rows):
        shash = imagehash.hex_to_hash(sphash_hex)
        site_pixels = sw * sh
        for cpath, cw, ch, chash in cand_hashes:
            dist = shash - chash
            cand_pixels = cw * ch
            if dist <= THRESHOLD and cand_pixels > site_pixels:
                conn.execute(
                    "INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (spath, project, sw, sh, cpath, cw, ch, dist),
                )
                match_count += 1
        if (i + 1) % 50 == 0:
            print(f"  Compared {i + 1}/{len(site_rows)} site images, {match_count} matches so far...")

    conn.commit()

    # Report
    print(f"\nFound {match_count} matches (candidate larger than site image, hamming <= {THRESHOLD})")
    print()

    rows = conn.execute("""
        SELECT site_path, site_project,
               site_width || 'x' || site_height AS site_size,
               cand_width || 'x' || cand_height AS cand_size,
               hamming, candidate_path
        FROM matches
        ORDER BY hamming, site_path
    """).fetchall()

    if rows:
        print(f"{'Site Image':<28} {'Project':<35} {'Site Size':<12} {'Candidate Size':<15} {'Dist':<5} Candidate Path")
        print("-" * 160)
        for site_path, project, ssize, csize, dist, cpath in rows:
            short_cpath = cpath.replace(search_dir, "...")
            print(f"{site_path:<28} {project:<35} {ssize:<12} {csize:<15} {dist:<5} {short_cpath}")

    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 find_bigger.py <search_directory> [--exclude dir1 dir2 ...]")
        sys.exit(1)

    search_dir = sys.argv[1]
    exclude_dirs = []
    if "--exclude" in sys.argv:
        idx = sys.argv.index("--exclude")
        exclude_dirs = sys.argv[idx + 1:]

    scan_candidates(search_dir, exclude_dirs)
