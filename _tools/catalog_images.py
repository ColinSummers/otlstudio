#!/usr/bin/env python3
"""Catalog site images into a SQLite database with dimensions and perceptual hashes."""

import os
import sqlite3
import imagehash
from PIL import Image

SITE_ROOT = os.path.join(os.path.dirname(__file__), "..")

PROJECTS = {
    "198701": "Darrows Cottage",
    "199001": "Law Offices",
    "199002": "Dowling House",
    "199003": "Attorney Interior",
    "199004": "Landgraf Addition",
    "199005": "Farmhouse Renovation",
    "199006": "Second Sun Porch",
    "199007": "First Sun Porch",
    "199101": "Delicate Addition",
    "199102": "Stone Ridge Retirement Center",
    "199103": "Hackett House",
    "199104": "Yonke House",
    "199105": "A Cottage for Rita",
    "199106": "Observatory",
    "199107": "A Porch and Hammock Box",
    "199301": "Farmhouse Garage",
    "199501": "Bramlett Home",
    "199601": "The Slammer",
    "199801": "Bonhill (renovation)",
    "199901": "21 Place (renovation)",
    "200101": "Castle",
    "200102": "The Slammer: Filter Haus",
    "200103": "Chicago Row House",
    "200201": "Canyon",
    "200202": "Calico",
    "200203": "Canyon Deck",
    "200301": "Encino (major renovation)",
    "200302": "Topanga (minor renovation)",
    "200303": "Appleton",
    "200304": "Custer (log cabin home)",
    "200305": "Bookshelf",
    "200306": "Farmhouse Sauna",
    "200401": "The Slammer: Vintage Nudes Studio",
    "200402": "Bronson",
    "200403": "Pool Cabana in Encino",
    "200404": "The Slammer: Cellblock B",
    "200405": "The Slammer: Ranger Station",
    "200406": "Palm 30",
    "200407": "The Slammer: Crazy Grass",
    "200408": "The Slammer: Motor Court",
    "200409": "The Slammer: Entry Terrace",
    "200501": "Greenleaf (writer's room)",
    "200503": "Equinox Studio",
    "200504": "Manchester House",
    "200505": "The Slammer: Koi Pond",
    "200506": "Farmhouse Entry",
    "200507": "Forum Condo",
    "200508": "Los Alamos Hot Tub and Deck",
    "200601": "Loft 8R",
    "200602": "West House",
    "200603": "Palisades Office",
    "200604": "Meshoppen House",
}


def project_name_for(filename):
    """Extract project name from image filename like 19900101.jpg -> 'Law Offices'."""
    base = os.path.splitext(filename)[0].rstrip("t")  # strip thumbnail suffix
    project_id = base[:6]
    return PROJECTS.get(project_id, "")


def catalog():
    db_path = os.path.join(SITE_ROOT, "_tools", "images.db")
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS site_images")
    conn.execute("""
        CREATE TABLE site_images (
            path        TEXT PRIMARY KEY,
            filename    TEXT,
            project     TEXT,
            is_thumb    INTEGER,
            width       INTEGER,
            height      INTEGER,
            phash       TEXT
        )
    """)

    # Scan images/, images/big/, and media/
    dirs = [
        os.path.join(SITE_ROOT, "images"),
        os.path.join(SITE_ROOT, "images", "big"),
        os.path.join(SITE_ROOT, "media"),
    ]

    count = 0
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            fpath = os.path.join(d, fname)
            if not os.path.isfile(fpath):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png"):
                continue

            try:
                img = Image.open(fpath)
                w, h = img.size
                phash = str(imagehash.phash(img))
            except Exception as e:
                print(f"  SKIP {fpath}: {e}")
                continue

            rel_path = os.path.relpath(fpath, SITE_ROOT)
            is_thumb = 1 if fname.endswith("t.jpg") or fname.endswith("t.png") else 0
            project = project_name_for(fname)

            conn.execute(
                "INSERT OR REPLACE INTO site_images VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rel_path, fname, project, is_thumb, w, h, phash),
            )
            count += 1

    conn.commit()
    print(f"Cataloged {count} images into {db_path}")

    # Summary
    cur = conn.execute("SELECT COUNT(*) FROM site_images WHERE is_thumb = 0")
    full = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM site_images WHERE is_thumb = 1")
    thumbs = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(DISTINCT project) FROM site_images WHERE project != ''")
    projects = cur.fetchone()[0]
    print(f"  {full} full-size, {thumbs} thumbnails, {projects} projects")

    conn.close()


if __name__ == "__main__":
    catalog()
