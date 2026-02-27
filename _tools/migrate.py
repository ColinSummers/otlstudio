#!/usr/bin/env python3
"""Migrate OTL Studio from PHP/MySQL to static HTML/CSS."""

import os
import re
import glob as globmod
import shutil

# Paths
OLD_SITE = "/Users/colin/Sites/cloudflare/old_otlstudio"
NEW_SITE = "/Users/colin/Sites/cloudflare/otlstudio"
CAPTIONS_DIR = os.path.join(OLD_SITE, "captions")
IMAGES_DIR = os.path.join(NEW_SITE, "images")

# ============================================================
# PROJECT DATABASE (scraped from live site)
# ============================================================

PROJECTS = {
    "198701": {"name": "Darrows Cottage", "city": "Lakewood", "state": "PA"},
    "199001": {"name": "Law Offices", "city": "Weehawken", "state": "NJ"},
    "199002": {"name": "Dowling House", "city": "Talladega", "state": "AL"},
    "199003": {"name": "Attorney Interior", "city": "Weehawken", "state": "NJ"},
    "199004": {"name": "Landgraf Addition", "city": "Ararat Township", "state": "PA"},
    "199005": {"name": "Farmhouse Renovation", "city": "Jackson", "state": "PA"},
    "199006": {"name": "Second Sun Porch", "city": "Starruca", "state": "PA"},
    "199007": {"name": "First Sun Porch", "city": "Thompson", "state": "PA"},
    "199101": {"name": "Delicate Addition", "city": "Point Judith", "state": "RI"},
    "199102": {"name": "Stone Ridge Retirement Center", "city": "Jackson Township", "state": "PA"},
    "199103": {"name": "Hackett House", "city": "Thompson", "state": "PA"},
    "199104": {"name": "Yonke House", "city": "Burnwood", "state": "PA"},
    "199105": {"name": "A Cottage for Rita", "city": "Jackson", "state": "PA"},
    "199106": {"name": "Observatory", "city": "Basking Ridge", "state": "NJ"},
    "199107": {"name": "A Porch and Hammock Box", "city": "Irvington", "state": "NY"},
    "199301": {"name": "Farmhouse Garage", "city": "Thompson", "state": "PA"},
    "199501": {"name": "Bramlett Home", "city": "Las Vegas", "state": "NV"},
    "199601": {"name": "The Slammer", "city": "Las Vegas", "state": "NV"},
    "199801": {"name": "Bonhill (renovation)", "city": "Brentwood", "state": "CA"},
    "199901": {"name": "21 Place (renovation)", "city": "Santa Monica", "state": "CA"},
    "200101": {"name": "Castle", "city": "Henderson", "state": "NV"},
    "200102": {"name": "The Slammer: Filter Haus", "city": "Las Vegas", "state": "NV"},
    "200103": {"name": "Chicago Row House", "city": "Chicago", "state": "IL"},
    "200201": {"name": "Canyon", "city": "Beverly Hills", "state": "CA"},
    "200202": {"name": "Calico", "city": "Calico", "state": "NV"},
    "200203": {"name": "Canyon Deck", "city": "Beverly Hills", "state": "CA"},
    "200301": {"name": "Encino (major renovation)", "city": "Encino", "state": "CA"},
    "200302": {"name": "Topanga (minor renovation)", "city": "Topanga", "state": "CA"},
    "200303": {"name": "Appleton", "city": "Venice", "state": "CA"},
    "200304": {"name": "Custer (log cabin home)", "city": "Custer", "state": "SD"},
    "200305": {"name": "Bookshelf", "city": "Pacific Palisades", "state": "CA"},
    "200306": {"name": "Farmhouse Sauna", "city": "Thompson", "state": "PA"},
    "200401": {"name": "The Slammer: Vintage Nudes Studio", "city": "Las Vegas", "state": "NV"},
    "200402": {"name": "Bronson", "city": "Los Angeles", "state": "CA"},
    "200403": {"name": "Pool Cabana in Encino", "city": "Encino", "state": "CA"},
    "200404": {"name": "The Slammer: Cellblock B", "city": "Las Vegas", "state": "NV"},
    "200405": {"name": "The Slammer: Ranger Station", "city": "Las Vegas", "state": "NV"},
    "200406": {"name": "Palm 30", "city": "Twenty-nine Palms", "state": "CA"},
    "200407": {"name": "The Slammer: Crazy Grass", "city": "Las Vegas", "state": "NV"},
    "200408": {"name": "The Slammer: Motor Court", "city": "Las Vegas", "state": "NV"},
    "200409": {"name": "The Slammer: Entry Terrace", "city": "Las Vegas", "state": "NV"},
    "200501": {"name": "Greenleaf (writer's room)", "city": "Sherman Oaks", "state": "CA"},
    "200503": {"name": "Equinox Studio", "city": "Manchester", "state": "VT"},
    "200504": {"name": "Manchester House", "city": "Manchester Center", "state": "VT"},
    "200505": {"name": "The Slammer: Koi Pond", "city": "Las Vegas", "state": "NV"},
    "200506": {"name": "Farmhouse Entry", "city": "Thompson", "state": "PA"},
    "200507": {"name": "Forum Condo", "city": "Scranton", "state": "PA"},
    "200508": {"name": "Los Alamos Hot Tub and Deck", "city": "Los Alamos", "state": "CA"},
    "200601": {"name": "Loft 8R", "city": "New York", "state": "NY"},
    "200602": {"name": "West House", "city": "Pacific Palisades", "state": "CA"},
    "200603": {"name": "Palisades Office", "city": "Pacific Palisades", "state": "CA"},
    "200604": {"name": "Meshoppen House", "city": "Meshoppen", "state": "PA"},
}

# Sorted project IDs (for next-project navigation)
SORTED_IDS = sorted(PROJECTS.keys())

# Project IDs that have PHP files
PROJECT_FILES = sorted([
    f.replace(".php", "") for f in os.listdir(os.path.join(OLD_SITE, "projects"))
    if f.endswith(".php") and f != "index.php"
])


# ============================================================
# HELPERS
# ============================================================

def read_caption(image_id):
    """Read caption text for an image ID (e.g., '19900101')."""
    path = os.path.join(CAPTIONS_DIR, f"{image_id}.txt")
    if os.path.exists(path):
        return open(path).read().strip()
    return ""


def get_project_images(project_id):
    """Get sorted list of image IDs for a project (non-thumbnail)."""
    pattern = os.path.join(IMAGES_DIR, f"{project_id}??.jpg")
    files = globmod.glob(pattern)
    # Filter out thumbnails (ending in t.jpg before the number)
    images = []
    for f in files:
        basename = os.path.basename(f).replace(".jpg", "")
        # Skip thumbnails: they end with 't' before .jpg
        if not basename.endswith("t"):
            images.append(basename)
    return sorted(images)


def expand_image_num(project_id, num_str):
    """Expand a photo number to a full image ID. e.g., '4' -> '19900104'."""
    num_str = num_str.strip()
    if len(num_str) < 2:
        num_str = f"0{num_str}"
    return f"{project_id}{num_str}"


def get_image_src(image_id):
    """Get the best available image source path (prefer big/ version)."""
    big_path = os.path.join(IMAGES_DIR, "big", f"{image_id}.jpg")
    if os.path.exists(big_path):
        return f"../images/big/{image_id}.jpg"
    return f"../images/{image_id}.jpg"


def get_thumb_src(image_id):
    """Get thumbnail source path."""
    thumb_path = os.path.join(IMAGES_DIR, f"{image_id}t.jpg")
    if os.path.exists(thumb_path):
        return f"../images/{image_id}t.jpg"
    return f"../images/{image_id}.jpg"


def next_project(project_id):
    """Get the next project ID in sequence (wraps around)."""
    if project_id not in PROJECT_FILES:
        return PROJECT_FILES[0]
    idx = PROJECT_FILES.index(project_id)
    return PROJECT_FILES[(idx + 1) % len(PROJECT_FILES)]


def html_escape(text):
    """Basic HTML entity escaping."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ============================================================
# HTML TEMPLATE
# ============================================================

def html_template(title, content, section="", depth=0):
    """Wrap content in the site HTML template."""
    rel = "../" * depth if depth > 0 else ""

    nav_items = [
        ("Mission", f"{rel}mission.html", "mission"),
        ("Projects", f"{rel}projects.html", "projects"),
        ("About", f"{rel}about.html", "about"),
        ("Contact", f"{rel}contact.html", "contact"),
        ("Code", f"{rel}code/index.html", "code"),
    ]

    nav_html = ""
    for label, href, key in nav_items:
        active = ' class="active"' if key == section else ""
        nav_html += f'        <li{active}><a href="{href}">{label}</a></li>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | Outside The Lines Studio</title>
  <meta name="author" content="Colin Summers, Robert Whitehead" />
  <link rel="stylesheet" href="{rel}style.css" />
</head>
<body>
  <nav class="navbar">
    <div class="navbar-inner">
      <a class="navbar-brand" href="{rel}index.html"><img src="{rel}_Media/otl_logo.jpg" alt="" class="navbar-logo" /> Outside The Lines Studio</a>
      <input type="checkbox" id="nav-toggle" class="nav-toggle" />
      <label for="nav-toggle" class="nav-toggle-label"><span></span></label>
      <ul class="nav-links">
{nav_html}      </ul>
    </div>
  </nav>
  <main>
{content}
  </main>
  <footer class="site-footer">
    <p>&copy; Outside The Lines Studio</p>
    <p class="tagline">Design Consultation &middot; Friday Harbor, Washington</p>
  </footer>
</body>
</html>
"""


# ============================================================
# GALLERY GENERATION
# ============================================================

def generate_gallery(project_id, images):
    """Generate the gallery grid + lightbox HTML for a project's images."""
    if not images:
        return ""

    grid_html = '<div class="gallery-section">\n<h2>Gallery</h2>\n<div class="gallery-grid">\n'
    lightbox_html = ""

    for i, img_id in enumerate(images):
        caption = read_caption(img_id)
        alt = caption[:80] if caption else f"{PROJECTS.get(project_id, {}).get('name', '')} photograph"
        thumb_src = get_thumb_src(img_id)
        full_src = get_image_src(img_id)

        # Grid thumbnail
        grid_html += f'  <a href="#img-{img_id}"><img src="{thumb_src}" alt="{alt}" loading="lazy" /></a>\n'

        # Lightbox
        prev_link = ""
        next_link = ""
        if i > 0:
            prev_link = f'  <a class="lightbox-prev" href="#img-{images[i-1]}">&lsaquo;</a>\n'
        if i < len(images) - 1:
            next_link = f'  <a class="lightbox-next" href="#img-{images[i+1]}">&rsaquo;</a>\n'

        caption_html = ""
        if caption:
            caption_html = f'  <div class="lightbox-caption">{caption}</div>\n'

        lightbox_html += f"""<div class="lightbox" id="img-{img_id}">
  <a class="lightbox-backdrop" href="#_"></a>
  <div class="lightbox-content">
    <a class="lightbox-close" href="#_">&times;</a>
{prev_link}    <img src="{full_src}" alt="{alt}" />
{next_link}{caption_html}  </div>
</div>
"""

    grid_html += '</div>\n</div>\n'
    return grid_html + lightbox_html


# ============================================================
# PHP CONVERSION
# ============================================================

def convert_php_content(text, project_id=None):
    """Convert PHP function calls in content to static HTML."""

    # Remove PHP include lines
    text = re.sub(
        r'<\?php\s+include\s*\([^)]+\)\s*;?\s*\?>',
        '', text, flags=re.IGNORECASE
    )

    # Remove HTML comments with project names (<!-- The Slammer -->)
    text = re.sub(r'<!--[^>]*-->', '', text)

    # Convert photoTop + projectHeading (handled separately in project pages)
    text = re.sub(
        r'<\?php\s+echo\s*\(\s*photo(?:Top|Side)\s*\([^)]+\)\s*\.\s*project[Hh]eading\s*\(\s*\)\s*\)\s*;?\s*\?>',
        '%%PROJECT_HEADING%%', text
    )

    # Convert standalone projectHeading
    text = re.sub(
        r'<\?php\s+echo\s*\(\s*project[Hh]eading\s*\(\s*\)\s*\)\s*;?\s*\?>',
        '%%PROJECT_HEADING%%', text
    )

    # Convert photoTop (standalone, without projectHeading)
    def replace_photo_top(m):
        args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
        if not project_id:
            return ""
        imgs = [expand_image_num(project_id, a) for a in args if a]
        if not imgs:
            return ""
        hero_src = get_image_src(imgs[0])
        html = f'<div class="project-hero"><img src="{hero_src}" alt="" /></div>\n'
        return html

    text = re.sub(
        r'<\?php\s+echo\s*\(\s*photoTop\s*\(([^)]+)\)\s*\)\s*;?\s*\?>',
        replace_photo_top, text, flags=re.IGNORECASE
    )

    # Convert photoSide (standalone)
    def replace_photo_side(m):
        args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
        if not project_id:
            return ""
        imgs = [expand_image_num(project_id, a) for a in args if a]
        if not imgs:
            return ""
        main_src = get_image_src(imgs[0])
        html = f'<div class="photo-side">\n<div class="photo-side-main"><img src="{main_src}" alt="" /></div>\n'
        if len(imgs) > 1:
            html += '<div class="photo-side-thumbs">\n'
            for img in imgs[1:]:
                html += f'<img src="{get_thumb_src(img)}" alt="" />\n'
            html += '</div>\n'
        html += '</div>\n'
        return html

    text = re.sub(
        r'<\?php\s+echo\s*\(\s*photoSide\s*\(([^)]+)\)\s*\)\s*;?\s*\?>',
        replace_photo_side, text, flags=re.IGNORECASE
    )

    # Convert photoBar
    def replace_photo_bar(m):
        args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
        if not project_id:
            return ""
        imgs = [expand_image_num(project_id, a) for a in args if a]
        if not imgs:
            return ""
        html = '<div class="photo-bar">\n'
        for img in imgs:
            html += f'<img src="{get_thumb_src(img)}" alt="" />\n'
        html += '</div>\n'
        return html

    text = re.sub(
        r'<\?php\s+echo\s*\(?photo[Bb]ar\s*\(([^)]+)\)\s*\)?\s*;?\s*\?>',
        replace_photo_bar, text, flags=re.IGNORECASE
    )

    # Convert projectlink
    def replace_projectlink(m):
        pid = m.group(1).strip()
        name = m.group(2)
        if name:
            name = name.strip().strip('"').strip("'")
        else:
            name = PROJECTS.get(pid, {}).get("name", pid)
        return f'<a href="../projects/{pid}.html">{name}</a>'

    # projectlink with name argument
    text = re.sub(
        r'<\?php\s+echo\s*\(\s*projectlink\s*\(\s*(\d+)\s*,\s*"([^"]*?)"\s*\)\s*\)\s*;?\s*\?>',
        replace_projectlink, text, flags=re.IGNORECASE
    )
    # projectlink without name
    text = re.sub(
        r'<\?php\s+echo\s*\(\s*projectlink\s*\(\s*(\d+)\s*\)\s*\)\s*;?\s*\?>',
        lambda m: replace_projectlink(type('M', (), {'group': lambda s, n: m.group(n) if n <= 1 else None})()), text, flags=re.IGNORECASE
    )

    # Convert projectList (used on Slammer page)
    def replace_project_list(m):
        where_clause = m.group(1)
        # Parse the IN clause for project IDs
        ids = re.findall(r"'(\d+)'", where_clause)
        html = '<table class="project-list">\n<tr><th>Project</th><th>Location</th></tr>\n'
        for pid in ids:
            proj = PROJECTS.get(pid, {})
            name = proj.get("name", pid)
            city = proj.get("city", "")
            state = proj.get("state", "")
            has_page = pid in PROJECT_FILES
            if has_page:
                link = f'<a href="../projects/{pid}.html">{name}</a>'
            else:
                link = f'{name} ({pid})'
            html += f'<tr><td>{link}</td><td>{city}, {state}</td></tr>\n'
        html += '</table>\n'
        return html

    text = re.sub(
        r'<\?php\s+echo\s*\(\s*projectList\s*\(\s*"([^"]+)"\s*\)\s*\)\s*;?\s*\?>',
        replace_project_list, text, flags=re.IGNORECASE
    )

    # Remove any remaining PHP tags
    text = re.sub(r'<\?php[^?]*\?>', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Fix relative image paths (for non-project pages)
    text = text.replace('src=images/', 'src="_Media/')
    text = text.replace('src="images/', 'src="_Media/')
    text = text.replace('src=/images/', 'src="images/')
    text = text.replace('src="/images/', 'src="images/')

    # Fix gallery.php links to lightbox anchors
    text = re.sub(
        r'<a href=["\']?(?:http://otlstudio\.com)?/gallery\.php\?image=(\w+)["\']?>',
        lambda m: f'<a href="#img-{m.group(1)}">',
        text
    )

    # Fix absolute /projects/ links
    text = re.sub(r'href=/projects/(\d+)\.html">', r'href="\1.html">', text)

    # Fix old-style links
    text = text.replace('href=/projects.php', 'href="projects.html"')
    text = text.replace('href=/mission.php', 'href="mission.html"')
    text = text.replace('href=/about.php', 'href="about.html"')
    text = text.replace('href=/contact.php', 'href="contact.html"')
    text = text.replace('href=/journal.php', 'href="journal.html"')
    text = text.replace('href=/code/', 'href="code/index.html"')
    text = text.replace('href=/mission/generating.php', 'href="mission/generating.html"')
    text = text.replace('href=/mission/plan.php', 'href="mission/plan.html"')
    text = text.replace('.php"', '.html"')
    text = text.replace(".php>", '.html">')

    return text.strip()


# ============================================================
# PROJECT PAGE GENERATION
# ============================================================

def convert_project_page(project_id):
    """Convert a project PHP file to static HTML."""
    php_path = os.path.join(OLD_SITE, "projects", f"{project_id}.php")
    if not os.path.exists(php_path):
        return

    proj = PROJECTS.get(project_id, {})
    name = proj.get("name", project_id)
    city = proj.get("city", "")
    state = proj.get("state", "")
    year = project_id[:4]

    # Read and convert PHP content
    raw = open(php_path, encoding="latin-1").read()

    # Extract the photo numbers from the first photoTop/photoSide call
    hero_match = re.search(r'photo(?:Top|Side)\s*\(([^)]+)\)', raw)
    hero_img = None
    if hero_match:
        args = [a.strip() for a in hero_match.group(1).split(",")]
        if args and args[0]:
            hero_img = expand_image_num(project_id, args[0])

    content = convert_php_content(raw, project_id)

    # Replace the PROJECT_HEADING placeholder
    heading_html = f"""<div class="project-header">
      <h1>{name}</h1>
      <p class="project-location">{city}, {state}</p>
      <p class="project-dates">{year}</p>
    </div>"""

    if hero_img:
        hero_src = get_image_src(hero_img)
        heading_html += f'\n    <div class="project-hero"><img src="{hero_src}" alt="{name}" /></div>'

    content = content.replace("%%PROJECT_HEADING%%", heading_html)

    # Fix image paths for project pages (depth=1)
    content = content.replace('src="_Media/', 'src="../_Media/')

    # Fix gallery link to lightbox
    content = re.sub(
        r'<a href=["\']?/gallery\.php\?image=(\d+)["\']?>gallery</a>',
        lambda m: '<a href="#img-' + m.group(1) + '">gallery</a>',
        content
    )
    content = re.sub(
        r'<a href=["\']?http://otlstudio\.com/gallery\.php\?image=\w+["\']?>',
        '', content
    )

    # Fix project links for depth=1
    content = content.replace('href="../projects/', 'href="')

    # Generate the gallery section
    images = get_project_images(project_id)
    gallery_html = generate_gallery(project_id, images)

    # Next project navigation
    next_id = next_project(project_id)
    next_name = PROJECTS.get(next_id, {}).get("name", next_id)
    nav_html = f"""    <div class="project-nav">
      <a href="../projects.html">All Projects</a>
      <a href="{next_id}.html">Next: {next_name} &rarr;</a>
    </div>"""

    full_content = f"    {content}\n{gallery_html}\n{nav_html}"

    html = html_template(name, full_content, "projects", depth=1)
    out_path = os.path.join(NEW_SITE, "projects", f"{project_id}.html")
    open(out_path, "w").write(html)
    print(f"  {project_id}.html - {name} ({len(images)} images)")


# ============================================================
# CONTENT PAGE GENERATION
# ============================================================

def convert_content_page(php_filename, output_filename, section, title, depth=0):
    """Convert a content PHP file to static HTML."""
    php_path = os.path.join(OLD_SITE, php_filename)
    if not os.path.exists(php_path):
        print(f"  WARNING: {php_filename} not found")
        return

    raw = open(php_path, encoding="latin-1").read()
    content = convert_php_content(raw)

    # Fix relative paths based on depth
    if depth > 0:
        content = content.replace('href="mission.html"', f'href="../mission.html"')
        content = content.replace('href="projects.html"', f'href="../projects.html"')
        content = content.replace('href="about.html"', f'href="../about.html"')
        content = content.replace('href="contact.html"', f'href="../contact.html"')
        content = content.replace('href="journal.html"', f'href="../journal.html"')
        content = content.replace('href="code/index.html"', f'href="../code/index.html"')
        content = content.replace('href="mission/generating.html"', f'href="generating.html"')
        content = content.replace('href="mission/plan.html"', f'href="plan.html"')
        content = content.replace('src="_Media/', f'src="../_Media/')
        content = content.replace('src="images/', f'src="../images/')

    full_content = f"    {content}"
    html = html_template(title, full_content, section, depth=depth)
    out_path = os.path.join(NEW_SITE, output_filename)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w").write(html)
    print(f"  {output_filename}")


# ============================================================
# HOMEPAGE
# ============================================================

def generate_homepage():
    """Generate index.html."""
    content = """    <div class="home-intro">
      <p class="studio-name">Outside The Lines Studio</p>
      <p>
      After twenty years of designing together, we've taken a moment to
      make an online presence and a portfolio for potential clients to
      peruse. Up until now our marketing efforts consisted of the few
      business cards we would hand out; all of our projects arrive in our
      studio via word-of-mouth.
      </p>
      <p>
      We have designed
      <a href="code/index.html">web sites</a>,
      furniture, rooms, gardens, and
      assisted with architect-client interaction on houses (the
      studio includes an architect licensed in Pennsylvania and California). We
      have been involved in the design of several residences and a
      couple commercial projects in quite a few different states.
      The <a href="projects.html">Projects page</a> is a portfolio-in-progress.
      </p>
      <p>
      The <a href="mission.html">Mission page</a>
      will tell you what we are hoping to accomplish. We occasionally
      update the <a href="journal.html">Journal</a>
      with notes and photographs about recent projects, before they
      are added to the portfolio of projects.
      <a href="about.html">About</a> will tell you who we are and
      <a href="contact.html">Contact</a> will tell you how to get ahold of us.
      </p>
      <p class="tagline">Design Consultation &middot; Friday Harbor, Washington</p>
    </div>"""

    html = html_template("Home", content, "", depth=0)
    out_path = os.path.join(NEW_SITE, "index.html")
    open(out_path, "w").write(html)
    print("  index.html")


# ============================================================
# PROJECTS INDEX PAGE
# ============================================================

def generate_projects_index():
    """Generate projects.html with portfolio grid and full project list."""

    # Featured projects from portfolio.php (the 3x3 grid)
    featured = [
        ("20010108", "200101"),
        ("19910506", "199105"),
        ("20050405", "200504"),
        ("20030601", "200306"),
        ("20040605", "200406"),
        ("19910304", "199103"),
        ("20040213", "200402"),
        ("19910103", "199101"),
        ("20040907", "200409"),
    ]

    grid_html = '<div class="portfolio-grid">\n'
    for img_id, proj_id in featured:
        thumb_src = f"images/{img_id}t.jpg"
        name = PROJECTS.get(proj_id, {}).get("name", proj_id)
        grid_html += f'  <a href="projects/{proj_id}.html"><img src="{thumb_src}" alt="{name}" loading="lazy" /></a>\n'
    grid_html += '</div>\n'

    intro_html = """    <p>
    There are too many ways to explore a portfolio of work to
    present only one. Click on any image above to go to that project, or
    browse the complete list below.
    </p>
    <p>
    Our studio has designed projects across the country: in
    Pennsylvania, New York, Rhode Island, New Jersey, Alabama,
    Nevada, California, South Dakota, Illinois, and Vermont.
    </p>"""

    # Full project list table
    table_html = '\n    <table class="project-list">\n<tr><th>Project</th><th>Location</th><th>Year</th></tr>\n'
    for pid in sorted(PROJECTS.keys()):
        proj = PROJECTS[pid]
        name = proj["name"]
        city = proj["city"]
        state = proj["state"]
        year = pid[:4]
        has_page = pid in PROJECT_FILES
        if has_page:
            link = f'<a href="projects/{pid}.html">{name}</a>'
        else:
            link = name
        table_html += f'<tr><td>{link}</td><td>{city}, {state}</td><td class="year">{year}</td></tr>\n'
    table_html += '</table>\n'

    # Timeline section
    timeline_html = """
    <h2>Timeline</h2>
    <p>The following is a timeline of our partnership.</p>
    <table class="timeline">
    <tr><td class="year-cell">1965</td><td>Robert Whitehead born in Susquehanna, PA.</td></tr>
    <tr><td class="year-cell">1966</td><td>Colin Summers born in Red Bank, NJ.</td></tr>
    <tr><td class="year-cell">1983</td><td>Robert graduates from high school, he attends college math classes for a year before starting Cornell.</td></tr>
    <tr><td class="year-cell">1984</td><td>Colin graduates from Stuyvesant.<br>We meet in Ithaca, NY when we matriculate to a college of architecture.</td></tr>
    <tr><td class="year-cell">1987</td><td>We design our <a href="projects/198701.html">first built project</a> together.</td></tr>
    <tr><td class="year-cell">1988</td><td>Other undergraduates get their degrees. Ours is a five-year program to get a Bachelors of Architecture.</td></tr>
    <tr><td class="year-cell">1989</td><td>Classmates get their BArch&rsquo;s, but we&rsquo;ve each taken a year off.</td></tr>
    <tr><td class="year-cell">1990</td><td>Cornell awards Robert his Bachelor of Architecture.<br>We form Whitehead &amp; Co. in Jackson, Pennsylvania.</td></tr>
    <tr><td class="year-cell">1991</td><td>We build our <a href="projects/199105.html">first house</a> as W&amp;Co.</td></tr>
    <tr><td class="year-cell">1992</td><td>Colin moves to New York City. There are fewer architecture opportunities than he had hoped.</td></tr>
    <tr><td class="year-cell">1994</td><td>Colin moves to Las Vegas and starts designing <a href="projects/199601.html">The Slammer</a>.<br>Cornell relinquishes Colin&rsquo;s Bachelor of Architecture.</td></tr>
    <tr><td class="year-cell">1995</td><td>Construction starts on <a href="projects/199601.html">The Slammer</a>.</td></tr>
    <tr><td class="year-cell">1996</td><td>Colin moves to Los Angeles, CA.</td></tr>
    <tr><td class="year-cell">2001</td><td>Colin accepts the commission for <a href="projects/200101.html">The Castle</a>. It is immediately clear that it is a huge, and daunting, task.<br>Robert flies out for a four day weekend and we design <a href="projects/200202.html">the Calico House</a> together.</td></tr>
    <tr><td class="year-cell">2002</td><td>Robert moves to Santa Monica in May.<br>The partnership allows for a couple simultaneous projects, including two in Los Angeles, CA.<br>Robert starts studying for the architectural licensing exam.</td></tr>
    <tr><td class="year-cell">2003</td><td><a href="projects/200101.html">The Castle</a> continues its slow journey through permitting.<br>We take another few small jobs in Los Angeles to have work that doesn&rsquo;t require a commute on Southwest.</td></tr>
    <tr><td class="year-cell">2004</td><td>One of the small jobs in Los Angeles turns into a large job.<br>We design two more additions to <a href="projects/199601.html">The Slammer</a>.</td></tr>
    <tr><td class="year-cell">2005</td><td>We start trying to get a little more local work, and even put up a web site.<br>Colin gets licensed as a private pilot so our commute to Las Vegas is easier.</td></tr>
    <tr><td class="year-cell">2006</td><td>The client moves into <a href="projects/200101.html">The Castle</a>, <a href="projects/200404.html">Cellblock B</a> opens, and we finish a job in New York City.<br>Robert is licensed as an architect in Pennsylvania.<br>Colin gets his instrument rating, so we can commute through any clouds on the way to Las Vegas.</td></tr>
    </table>
"""

    content = f"    {grid_html}\n{intro_html}\n{table_html}\n{timeline_html}"
    html = html_template("Projects", content, "projects", depth=0)
    out_path = os.path.join(NEW_SITE, "projects.html")
    open(out_path, "w").write(html)
    print("  projects.html")


# ============================================================
# MISSION PAGE
# ============================================================

def generate_mission():
    """Generate mission.html with styled quotes."""
    content = """    <div class="quote">
      Everyone we have built for, they have a dream of a house, but they
      don't know how to express it. Expressing that dream for them is
      the challenge we have found worth our commitment.
      <span class="attribution">Colin Summers 1998</span>
    </div>

    <p>
    We look at each design problem as an encapsulated set of
    constraints, and initially we are focused on exploring them.
    Primary among these is the site, which is difficult to change and
    unique to each project. The site will help dictate a
    <a href="mission/generating.html">generating geometry</a>.
    </p>

    <div class="quote">
      You employ stone, wood and concrete, and with these materials
      you build houses and palaces; that is construction. Ingenuity is at
      work. But suddenly you touch my heart, you do me good, I am
      happy and I say: &lsquo;This is beautiful.&rsquo; That is
      architecture. Art enters in.
      <span class="attribution">Le Corbusier 1927</span>
    </div>

    <p>
    That quote is probably on more architecture web sites and
    brochures than any other. It is the lofty goal of most practicing
    architects: reaching beyond merely satisfying their clients barest
    needs, and even expressed desires, and creating something
    expressive, something which carries and communicates some
    meaning.
    </p>
    <p>
    We have been fortunate that we have rarely been forced to
    accept commisions which didn't interest us. Mercenary work is
    mind-numbing. On the other hand, if the project is interesting it
    doesn't matter how difficult the work it, we never tire of it.
    </p>
    <p>
    The generating geometry, mentioned above, sometimes leads to a
    bit of <a href="mission/plan.html">plan fixation</a>.
    </p>

    <div class="quote">
      The career issues Steven Ehrlich has faced for nearly twenty
      years in Southern California are those that confront all
      architects of good faith and strong ambition &mdash; the
      anxiety of influence, the dilemma of synthesis, the search for
      identity, and the emergence of a voice.
      <span class="attribution">Joseph Giovannini 1998, Introduction to Steve Erlich's monograph</span>
    </div>

    <p>
    Yes. In spades: anxiety, dilemma, search and emergence. Although
    that last one seems to be a tiny scratching still, a still too-tentative
    reaching for something that <em>could</em> be; mostly we find
    ourselves pre-occupied with the first three.
    </p>"""

    html = html_template("Mission", content, "mission", depth=0)
    out_path = os.path.join(NEW_SITE, "mission.html")
    open(out_path, "w").write(html)
    print("  mission.html")


# ============================================================
# ABOUT PAGE
# ============================================================

def generate_about():
    """Generate about.html."""
    content = """    <div class="about-section">
      <img src="_Media/early.jpg" alt="Colin and Robert" class="float-right" />
      <p>
      <strong>Outside The Lines Studio</strong> is a partnership. We started designing
      and building together in 1987, two years after we met at
      <a href="http://cornell.edu">Cornell University's</a>
      <a href="http://www.aap.cornell.edu">College of Architecture, Art and Planning</a>.
      </p>
      <p>
      Our first design company was called Whitehead &amp; Co. and we built a number of
      projects ourselves. For several years we followed separate paths and then
      reunited in Los Angeles, CA to start Outside The Lines Studio.
      </p>
    </div>

    <div class="about-section">
      <img src="_Media/cts.jpg" alt="Colin Summers" class="float-left" />
      <p>
      <strong>Colin Summers</strong> attended Stuyvesant High School before pursuing
      his Bachelors of Architecture. He grew up in New York City's
      Greenwich Village and spent summers in the north woods of Canada.
      He programs computers (and built a little
      <a href="code/index.html">dot com</a>) as a hobby. He lives in Santa Monica
      with his wife and their two sons.
      </p>
    </div>

    <div class="about-section">
      <img src="_Media/rtw.jpg" alt="Robert Whitehead" class="float-right" />
      <p>
      <strong>Robert Whitehead</strong> was the valedictorian of Blue Ridge High
      School in north eastern Pennsylvania. He grew up building
      houses with his father, a contractor. After securing his
      bachelors of architecture from Cornell, and building
      residential projects for two years as one half of Whitehead &amp;
      Co. he worked for several traditional architecture firms. Just
      before returning to work with his first partner, he was
      employed at
      <a href="http://hillier.com/home">The Hillier Group</a>, the third largest architectural
      firm in the country. In August 2006 Robert was licensed as an architect in
      the state of Pennsylvania. He is a member of the
      <a href="http://aia.org">American Institute of Architects</a>.
      </p>
    </div>"""

    html = html_template("About", content, "about", depth=0)
    out_path = os.path.join(NEW_SITE, "about.html")
    open(out_path, "w").write(html)
    print("  about.html")


# ============================================================
# JOURNAL PAGE
# ============================================================

def generate_journal():
    """Generate journal.html."""
    content = """    <h1>Journal</h1>

    <h3>February 2009</h3>
    <p>
    With the slowing of the economy and the decreasing likelihood of
    interesting commissions arriving in the studio, Robert headed
    back to the east coast to work at
    <a href="http://www.hillier.com/">RMJM Architects</a> on
    several large school projects in the New York City school district.
    (RMJM bought Hillier, where Robert had worked before.)
    </p>
    <p>
    Colin remains in Santa Monica, working on smaller projects and
    wishing putting those projects into the website were a little
    less tedious.
    </p>

    <hr />

    <h3>January 2007</h3>
    <p>
    It's been more than a year since we put up the web site and we
    have yet to add the sort of content we expected to. The web
    seems so shiny and seductive at first, but then we return to
    yellow trace and nice soft pencils and remember how much we love
    to sketch things.
    </p>
    <p>
    Sketching is more fun than writing HTML. In 2007 we will strive
    to get some updates onto the web site, because 2006 was a good
    year for photographs.
    </p>
    <p>
    In December of 2006 the owner moved into
    <a href="projects/200101.html">The Castle</a>.
    The project is not complete, but he was so enthusiastic when we
    finished the master wing that he had to move in. He was camping
    on the floor for a little while, but so excited that it didn't
    seem to matter.
    </p>
    <p>
    In November of 2006 the family wing of
    <a href="projects/199601.html">The Slammer</a>
    (<a href="projects/200404.html">Cellblock B</a>)
    was finally opened for use. It was instantly filled with toddler toys
    and the noise and chaos of family life, exactly as we hoped it would be.
    </p>
    <p>
    In September of 2006 Robert was licensed in Pennsylvania and
    started the process to get licensed in California.
    </p>"""

    html = html_template("Journal", content, "journal", depth=0)
    out_path = os.path.join(NEW_SITE, "journal.html")
    open(out_path, "w").write(html)
    print("  journal.html")


# ============================================================
# CONTACT PAGE
# ============================================================

def generate_contact():
    """Generate contact.html."""
    content = """    <h1>Contact</h1>
    <p>The best way to reach us is email:</p>
    <img src="_Media/contact.jpg" alt="Contact information" style="max-width: 280px;" />"""

    html = html_template("Contact", content, "contact", depth=0)
    out_path = os.path.join(NEW_SITE, "contact.html")
    open(out_path, "w").write(html)
    print("  contact.html")


# ============================================================
# CODE SECTION
# ============================================================

def generate_code_index():
    """Generate code/index.html."""
    content = """    <p>
    There is another kind of architecture, the architecture of information
    technology. The same sort of design decisions which work in real world
    design have similar implications in the virtual world.
    </p>
    <p>
    Colin has been programming computers since before he could drive (legally).
    When he does this work he often partners with
    <a href="http://deancameron.com">Dean Cameron</a> who is a whiz at the
    CSS style sheet fiddling.
    </p>
    <p>
    These are the significant projects over the last couple decades which
    Colin has been involved in as a system architect. All of them are
    projects he started on his own, and in the past decade he would bring
    Dean in to help with the details of how it looked to the outside world.
    </p>

    <table class="code-table">
    <tr><th>Year</th><th>Projects</th><th>Technology</th></tr>
    <tr>
      <td>2009</td>
      <td>
        <a href="http://bruce.mightycheese.com">Bruce Kapson Gallery</a><br />
        Revision of <a href="http://pattonandco.com">Patton &amp; Co.</a><br />
        Headbook
      </td>
      <td>Ruby on Rails, web scraping, AJAX</td>
    </tr>
    <tr>
      <td>2008</td>
      <td>
        <a href="http://school.mightycheese.com">Purple Form</a><br />
        <a href="http://pattonandco.com">Patton &amp; Co.</a><br />
        <a href="http://closebunch.com">closebunch.com</a> development starts
      </td>
      <td>Ruby on Rails, data import, light AJAX</td>
    </tr>
    <tr>
      <td>2005</td>
      <td><a href="../index.html">Outside The Lines Studio Site</a></td>
      <td>PHP, MySQL, CSS</td>
    </tr>
    <tr>
      <td>2004</td>
      <td>
        A software, technology and business model
        <a href="http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&amp;Sect2=HITOFF&amp;d=PALL&amp;p=1&amp;u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&amp;r=1&amp;f=G&amp;l=50&amp;s1=6,816,884.PN.&amp;OS=PN/6,816,884&amp;RS=PN/6,816,884">patent</a>
        is awarded to Colin Summers for the tightcircle technology.
      </td>
      <td></td>
    </tr>
    <tr>
      <td>1999</td>
      <td><a href="tightcircle.html">tightcircle.com</a> development starts</td>
      <td>tcl, Oracle SQL, Linux, HTML</td>
    </tr>
    <tr>
      <td>1997</td>
      <td><a href="jungle.html">The Jungle</a>, the rewrite</td>
      <td>HyperTalk, AppleScript, Emailer</td>
    </tr>
    <tr>
      <td>1987</td>
      <td><a href="jungle.html">The Jungle</a></td>
      <td>Turbo Pascal, MS-DOS, compiled batch scripts and modem scripts</td>
    </tr>
    <tr>
      <td>1982</td>
      <td>Invoicing Program</td>
      <td>MicroSoft BASIC</td>
    </tr>
    </table>

    <p>Colin's <a href="ColinSummers.pdf">resume for computer work</a>.</p>"""

    html = html_template("Code", content, "about", depth=1)
    out_path = os.path.join(NEW_SITE, "code", "index.html")
    open(out_path, "w").write(html)
    print("  code/index.html")


def generate_code_jungle():
    """Generate code/jungle.html."""
    content = """    <img src="../_Media/getkilled.jpg" alt="The Jungle" style="float: right; max-width: 200px; margin-left: 1.5rem;" />

    <p>
    In March 1987 Colin created The Jungle, an electronic community for
    Penn &amp; Teller. It was a electronic mail center, handling private
    messages as well as public discussion messages. He wrote it in
    Turbo Pascal 3.0, and ran it on an IBM PC XT/286. The Jungle replaced the
    electronic mail program that was included with PC Remote, software
    published by DCA, the makers of CrossTalk.
    </p>
    <p>
    Over time an offline reader was added to the package, and in the early
    nineties the public discussion messages were set up to be digested and
    sent out to some participants in regular Internet mail. When it became
    clear that there were better mail clients and mail solutions, the
    Jungle's original software was shut down, and the public discussion
    ran briefly on some C++ code. That was short lived. It broke too much
    and Colin wasn't involved enough in the architecture of the solution.
    </p>
    <p>
    So Colin created the entire system again, this time with Claris
    Emailer, Apple's own HyperCard, and a couple of little AppleScripts
    that connected the two. It has handled tens of thousands of messages
    in the current configuration, which has run since 1997
    with few changes. It runs on an Apple iMac, a fruit-colored one
    from the old days, running the MacOS version 8.1. It is fed
    bandwidth by FIOS in a little room off a garage.
    </p>
    <p>
    The total code for the HyperCard portion of the solution is less than
    100k of HyperTalk scripts. HyperTalk is a beautiful message-centric
    object-oriented language.
    </p>
    <p>
    Eventually the idea of The Jungle went public with
    <a href="tightcircle.html">tightcircle</a>, technology which resulted
    in a
    <a href="http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&amp;Sect2=HITOFF&amp;d=PALL&amp;p=1&amp;u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&amp;r=1&amp;f=G&amp;l=50&amp;s1=6,816,884.PN.&amp;OS=PN/6,816,884&amp;RS=PN/6,816,884">a patent</a>
    being issued to Colin.
    </p>"""

    html = html_template("The Jungle", content, "about", depth=1)
    out_path = os.path.join(NEW_SITE, "code", "jungle.html")
    open(out_path, "w").write(html)
    print("  code/jungle.html")


def generate_code_tightcircle():
    """Generate code/tightcircle.html."""
    content = """    <img src="../_Media/tc.png" alt="tightcircle" style="float: right; max-width: 200px; margin-left: 1.5rem;" />

    <p>
    In 1999 Colin started work with <a href="http://deancameron.com">Dean</a>
    to bring the technology of <a href="jungle.html">The Jungle</a> to a
    wider audience.
    </p>
    <p>
    In less than three months the web service was up and running. After
    several years of suspense, the technology, software and business
    model received
    <a href="http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&amp;Sect2=HITOFF&amp;d=PALL&amp;p=1&amp;u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&amp;r=1&amp;f=G&amp;l=50&amp;s1=6,816,884.PN.&amp;OS=PN/6,816,884&amp;RS=PN/6,816,884">a patent</a>
    from the United States Patent Office.
    </p>
    <p>
    It went through various re-designs, but the operation of the site
    remained very consistent over the six years it was in operation. In
    the last few years it went to a subscription model and it actually
    ran in the black, a rare condition in the dot-com era. Although there
    was a peak of over twenty thousand registered users, in the end
    there were about four hundred active tightcircles and five thousand users.
    </p>
    <p>
    The tightcircle technology would eventually be re-launched as the
    <a href="http://closebunch.com">closebunch.com</a> web service, which is
    cleverly crafted by Colin to evade the very patent he was awarded.
    </p>
    <p>
    One of the pages explained to new visitors what a tightcircle was:
    </p>

    <div class="quote">
    If you like email, you are going to love tightcircle.
    <p>
    A tightcircle is a place where a group of people can stay in touch
    online. Ongoing, online contact. It is like a conference call in email.
    </p>
    <p>
    Even if you have just started using email, you can use tightcircle. It
    is so simple.
    </p>
    <p>
    Just like regular email correspondence, each member can send messages
    into the tightcircle whenever they please. If you're a night owl and you
    normally check email at 3am, you can send messages while Aunt Valda
    is sleeping. Then, when she's up with the sun, she can reply, and the
    whole conversation is captured in the digest Cousin Sam reads when he
    gets to work at 9am.
    </p>
    <p>
    A tightcircle is a group conversation that takes place in email. Better
    than a simple correspondence, the conversation can include more than two
    people at a time. This doesn't happen real time, like an online chat or
    instant message session, but in email, which you can collect, read and
    reply to at your convenience. Because email messages from the various
    members are grouped together into one digest, there is a feeling of
    continuity, community and a conversational thread.
    </p>
    <p>
    Just get a group together &mdash; whether it's your college buddies, your
    siblings, your work mates, or your bridge club. Anyone who is on a
    computer and has access to email can be in a tightcircle that you
    create.
    </p>
    <p>
    You can create as many tightcircles as you want.
    </p>
    <p>
    The beauty of a tightcircle is that it is as easy as sending an email
    message, only instead of going to one person, it is read by every member
    of the tightcircle. Those messages are collected, digested, sent out at
    regular intervals by the secret tightcircle mechanism, and voila! the
    digests arrive in your inbox as email.
    </p>
    <p>
    You can even tell the tightcircle how often you want digests delivered.
    Some people check email three times a day, while others are lucky to
    log-on once a week. Just set the frequency and your digests will roll in
    as often or seldom as you like.
    </p>
    </div>"""

    html = html_template("tightcircle", content, "about", depth=1)
    out_path = os.path.join(NEW_SITE, "code", "tightcircle.html")
    open(out_path, "w").write(html)
    print("  code/tightcircle.html")


# ============================================================
# MISSION SUB-PAGES
# ============================================================

def generate_mission_generating():
    """Generate mission/generating.html."""
    content = """    <h1>A Generating Geometry</h1>
    <p>
    Le Corbusier claimed that all the great buildings could be
    reconstructed from their plans. (He was thinking mostly of his own
    buildings, but he often used a few classic Greek temples for examples.)
    You can ascertain the proportioning system that the architects were
    employing, and so you can figure out the height of the spaces from the
    plan. You know the materials from the footprint (a block of marble
    looks like <em>this</em>, a steel column is like <em>that</em>), and
    you know how how much weight a specific material can hold so you can
    start to figure out what sort of loads were carried by this plan. He
    might have been exaggerating to make a point, but his point was that if
    the design was very honest, the volumes (and therefore the building
    itself) would be contained in information in the plan.
    </p>
    <p>
    That seems correct, appropriate, and a good goal for a building's
    design.
    </p>
    <p>
    So we start from the plan. We usually already have some sectional
    ideas, some ideas about space, spatial vignettes we are interested in,
    and ideas about the programmatic requirements of the building, but the
    plan is where we start putting our ideas together, connecting them.
    </p>
    <p>
    Frank Lloyd Wright felt that the site was where the inspiration lay, so
    <em>he</em> started by first looking at sections through the site and
    features of the site that were in plan. We saw a sketch for the last
    Wright house that he was involved in (just before his death) when we
    were at the Wright archives in Scottsdale. It was a topographical
    map and he had just sketched some circles with a soft pencil in loopy
    configurations following a ridge that was apparent in the topography.
    So that was where he started: soft shapes (circles) march in plan along
    a topographical feature (ridge) on the site. He took ill the next day
    and died in a week or so, but his disciples faithfully followed that
    little sketch and created another Wright house.
    </p>
    <p>
    Back to the plan: so if you are looking at the plan, and you start
    laying down some ideas about the sequence of spaces (our own obsession
    is often connected to sequence and rhythm), where do you start? Mies
    liked a grid. Corbusier liked some orthogonal lines that he called
    regulating lines: often a grid, but often an irregular one with a
    rhythm like a-b-a-b-c (Mies was stricter about his grids: a-a-a-a-a).
    </p>
    <p>
    Usually, the site is more interesting than simply an orthogonal grid.
    The movement of the sun is of particular importance to us (it is the
    light that creates the experience of the forms built), and so are the
    relation of prominent landmarks to the site. So, for instance, the
    Strip is twenty-eight degrees east of north from the Slammer's site.
    Coincidentally (or perhaps not) the original house was oriented in
    that direction. So the rest of
    <a href="../projects/199601.html">The Slammer</a>
    meanders south (to get away from the road, to watch the mountains, to
    form the courtyard) and while it does so, it steps through those
    twenty-eight degrees back towards the north south grid (important to
    the site because it is how the Vegas basin has been etched by the BLM),
    making a set of seven degree steps. Those same steps allow the building
    to bend a little this way and that to make the courtyard both a little
    more intimate and a little more animated than it would be otherwise,
    and to present a little more imposing face to visitors (a little more
    aggressive stance in plan). Because that set of rotations starts to
    affect the cubic volumes we were creating for the programmatic spaces
    of the house, the house has some more drama, some more movement, than
    it would otherwise.
    </p>
    <p>
    The idea which informs those design decisions is <em>a generating
    geometry.</em> If you saw some of the earliest drawings for the Slammer
    you would see idealized plans of the courtyard and driveway, sweeping
    arcs of circles that represented "public" and "private" faces
    (experiences) of the building. As the generating geometry is added to
    the mix, and starts to be expressed in the built form, it works off
    these ideals and that tension creates some of the drama that you feel
    at The Slammer and in
    <a href="../projects.html">our other work</a>.
    </p>"""

    html = html_template("A Generating Geometry", content, "mission", depth=1)
    out_path = os.path.join(NEW_SITE, "mission", "generating.html")
    open(out_path, "w").write(html)
    print("  mission/generating.html")


def generate_mission_plan():
    """Generate mission/plan.html."""
    content = """    <h1>Plan Obsession</h1>
    <p>
    Unless there has been some accident or misfortune, you have two eyes in
    your head, set on a line perpendicular to gravity, a certain distance
    apart. They allow you to perceive depth. We have worked for the
    smallest giant (someone 6'6" or taller is technically a giant), but
    most people experience architecture for a pretty narrow range of
    heights.
    </p>
    <p>
    If you stand at a point at the entry to a courtyard and if we draw an
    arc fifty feet out from that point and place ten columns along that
    arc, you will stop right at that point. Your primordial brain will tell
    you that all the columns are equidistant and, we're not sure why, you
    pause to reflect on this little pattern recognition trick.
    </p>
    <p>
    You look out the window while doing dishes in the little sink in
    <a href="../projects/199601.html">The Slammer</a>
    kitchen and the edges of the big red structural fins all line up and
    point right at the center of the door from the garage. You remember how
    you walked in last night, right through that door. Somehow, this etches
    something (a plan, an experience, a sequence, a collection of episodes)
    in your mind. It happens in a flash. You are helpless, it happens in an
    instant and probably has something to do with keeping track of
    migrating herds that you needed to hunt on the plains a while back.
    </p>
    <p>
    Place. Path. Distance.
    </p>
    <p>
    We can record, or dictate, a vast amount of it and orchestrate a
    stunning amount just in a plan. That's where we can see the
    largest portion of the building at a single time. Most importantly (to
    us), we can see sequences, episodes as someone will move
    through the spaces. You will see this, you turn, that's a center
    (click), you turn, it's dark here and light over there (click), and you
    are drawn along, or stopped, or your perception is strobed as you
    walk along the catwalk and you glance at the sun on the
    mountains in the morning.
    </p>
    <p>
    All that is in the plan.
    </p>
    <p>
    So it is easy to become obsessed with the plan. And dangerous,
    because in the end the building is an object, a series of faces, a set
    of volumes, a collection of verticals and horizontals which might
    not come across exactly the same in plan as they do in model, or
    in a tiny thumbnail perspective.
    </p>
    <p>
    So we discuss constantly how to stay out of the plan, how to keep
    swapping back and forth from the plan to little sections, looking at
    what else was seen, up and down, rather than just on the hypnotic
    horizontal plain from a single (albeit moving) point. The computer
    has been a huge improvement in facilitating this early in the
    process.
    </p>"""

    html = html_template("Plan Obsession", content, "mission", depth=1)
    out_path = os.path.join(NEW_SITE, "mission", "plan.html")
    open(out_path, "w").write(html)
    print("  mission/plan.html")


# ============================================================
# MAIN
# ============================================================

def main():
    print("OTL Studio Migration")
    print("=" * 50)

    print("\nGenerating content pages...")
    generate_homepage()
    generate_mission()
    generate_mission_generating()
    generate_mission_plan()
    generate_about()
    generate_journal()
    generate_contact()
    generate_projects_index()
    generate_code_index()
    generate_code_jungle()
    generate_code_tightcircle()

    print(f"\nGenerating {len(PROJECT_FILES)} project pages...")
    for pid in PROJECT_FILES:
        convert_project_page(pid)

    print(f"\nDone! Generated files in {NEW_SITE}")


if __name__ == "__main__":
    main()
