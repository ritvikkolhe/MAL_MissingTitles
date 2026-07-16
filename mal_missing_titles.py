"""
MyAnimeList Missing Related Anime

Scans a user's MyAnimeList anime list and identifies related
anime entries that are not already present on the user's list,
while preserving Plan-To-Watch (PTW) entries for visibility.

Features:
- Franchise relationship discovery
    • Prequels
    • Sequels
    • Parent stories
    • Full stories
    • Side stories
    • Spin-offs

- Local HTML caching for fast repeated runs
- Episode count extraction
- Score extraction
- English title extraction
- Release year extraction
- Plan-To-Watch highlighting
- Unreleased anime detection
- Interactive HTML report
- Sortable columns
- Type filtering
- PTW filtering
- Unreleased filtering
- Direct MAL links

Output:
    missing_related_anime.html

Author: Ritvik Kolhe
"""

import os
import re
import time
import webbrowser
from pathlib import Path

import requests
from bs4 import BeautifulSoup, SoupStrainer
from tqdm import tqdm

CACHE_DIR = "cache"

CACHE_PATH = Path(CACHE_DIR)

os.makedirs(CACHE_DIR, exist_ok=True)

# ============================================================
# CONFIG
# ============================================================

REQUEST_DELAY = 0.1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/125.0 Safari/537.36"
}

MAIN_RELATIONS = {
    "prequel",
    "sequel",
    "parent story",
    "full story",
}

SECONDARY_RELATIONS = {
    "side story",
    "spin-off",
}

ALLOWED_RELATIONS = MAIN_RELATIONS | SECONDARY_RELATIONS

SESSION = requests.Session()

SESSION.headers.update(HEADERS)

ANIME_ID_RE = re.compile(r"/anime/(\d+)")

TYPE_RE = re.compile(r"\((.*?)\)")

YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

TYPE_NORMALIZATION = {
    "TV Special": "Special",
}


# ============================================================
# MAL LIST
# ============================================================


def get_user_list(username):
    all_entries = []
    offset = 0

    while True:
        url = (
            f"https://myanimelist.net/animelist/"
            f"{username}/load.json?offset={offset}&status=7"
        )

        response = SESSION.get(url, timeout=30)
        response.raise_for_status()

        batch = response.json()

        if not batch:
            break

        all_entries.extend(batch)

        offset += len(batch)

    return all_entries


# ============================================================
# HELPERS
# ============================================================


def extract_anime_id(url):
    match = ANIME_ID_RE.search(url)

    if match:
        return int(match.group(1))

    return None


# ============================================================
# ANIME SCRAPING
# ============================================================


def get_related_anime(anime_id):
    url = f"https://myanimelist.net/anime/{anime_id}"

    cache_hit = False

    try:

        cache_file = CACHE_PATH / f"{anime_id}.html"

        if cache_file.exists():

            with cache_file.open("r", encoding="utf-8") as f:

                html = f.read()

            cache_hit = True

        else:

            response = SESSION.get(url, timeout=30)

            response.raise_for_status()

            html = response.text

            with cache_file.open("w", encoding="utf-8") as f:

                f.write(html)

    except Exception as e:

        print(f"\nFailed {anime_id}: {e}")
        return [], cache_hit

    only_related = SoupStrainer(class_="related-entries")

    soup = BeautifulSoup(html, "html.parser", parse_only=only_related)

    results = []

    seen = set()

    # ------------------------
    # TILE ENTRIES
    # ------------------------

    for entry in soup.select("div.related-entries div.entries-tile div.entry"):

        relation_elem = entry.select_one("div.relation")

        anime_link = entry.select_one("div.title a[href*='/anime/']")

        if not relation_elem or not anime_link:
            continue

        relation_text = relation_elem.get_text(" ", strip=True)

        relation = relation_text.split("(")[0].strip()

        normalized_relation = relation.lower()

        if normalized_relation not in ALLOWED_RELATIONS:
            continue

        anime_type_match = TYPE_RE.search(relation_text)

        anime_type = anime_type_match.group(1) if anime_type_match else "Unknown"

        related_id = extract_anime_id(anime_link["href"])

        if related_id is None:
            continue

        key = (related_id, normalized_relation)

        if key in seen:
            continue

        seen.add(key)

        results.append(
            {
                "id": related_id,
                "title": anime_link.get_text(strip=True),
                "relation": normalized_relation,
                "type": anime_type,
            }
        )

    # ------------------------
    # TABLE ENTRIES
    # ------------------------

    rows = soup.select("div.related-entries table.entries-table tr")

    for row in rows:

        cells = row.find_all("td")

        if len(cells) < 2:
            continue

        relation = cells[0].get_text(strip=True).replace(":", "").strip()

        normalized_relation = relation.lower()

        if normalized_relation not in ALLOWED_RELATIONS:
            continue

        links = cells[1].select("a[href*='/anime/']")

        for link in links:

            related_id = extract_anime_id(link["href"])

            if related_id is None:
                continue

            key = (related_id, normalized_relation)

            if key in seen:
                continue

            seen.add(key)

            parent_text = link.parent.get_text(" ", strip=True)

            anime_type_match = TYPE_RE.search(parent_text)

            anime_type = anime_type_match.group(1) if anime_type_match else "Unknown"

            results.append(
                {
                    "id": related_id,
                    "title": link.get_text(strip=True),
                    "relation": normalized_relation,
                    "type": anime_type,
                }
            )

    return results, cache_hit


def get_anime_metadata(anime_id):
    cache_file = CACHE_PATH / f"{anime_id}.html"

    found_episodes = False
    found_year = False

    try:

        if cache_file.exists():

            with cache_file.open("r", encoding="utf-8") as f:
                html = f.read()

        else:

            url = f"https://myanimelist.net/anime/{anime_id}"

            response = SESSION.get(url, timeout=30)

            response.raise_for_status()

            html = response.text

            with cache_file.open("w", encoding="utf-8") as f:
                f.write(html)

        soup = BeautifulSoup(html, "html.parser")

        episodes = "?"
        score = "?"
        english_title = None
        year = "?"

        score_elem = soup.select_one("div.score-label")

        if score_elem:

            score_text = score_elem.get_text(strip=True)

            if score_text not in {"", "N/A", "?"}:
                score = score_text

        english = soup.find(class_="title-english")

        if english:
            title = english.get_text(strip=True)
            if title:
                english_title = title

        for span in soup.find_all("span", class_="dark_text"):

            label = span.get_text(strip=True)

            if label == "Episodes:":

                episodes = (
                    span.parent.get_text(" ", strip=True)
                    .replace("Episodes:", "")
                    .strip()
                )

                found_episodes = True

            elif label == "Aired:":

                aired_text = span.parent.get_text(" ", strip=True)

                if "Not available" in aired_text:

                    year = "?"

                else:

                    years = YEAR_RE.findall(aired_text)

                    if years:
                        year = int(years[0])

                        found_year = True

            if found_episodes and found_year:
                break

        return {
            "episodes": episodes,
            "english_title": english_title,
            "year": year,
            "score": score,
        }

    except Exception as e:

        print(f"METADATA ERROR {anime_id}: " f"{type(e).__name__}: {e}")

        return {"episodes": "?", "english_title": None, "year": "?", "score": "?"}


# ============================================================
# HTML REPORT
# ============================================================


def generate_html_report(missing):
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MAL Missing Anime Report</title>

<style>

body {{
    font-family: Segoe UI, Arial, sans-serif;
    margin: 30px;
    background: #f4f6f9;
}}

h1 {{
    margin-bottom: 8px;
}}

.subtitle {{
    color: #666;
    margin-bottom: 25px;
}}

.controls {{
    background: white;
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,.08);
}}

.title-column {{
    width: 50%;
}}

.title-main {{
    font-weight: 600;
    overflow-wrap: break-word;
}}

.title-sub {{
    font-size: 12px;
    color: #666;
    margin-top: 3px;
    overflow-wrap: break-word;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,.08);
    table-layout: fixed;
}}

thead {{
    position: sticky;
    top: 0;
}}

th {{
    background: #111827;
    color: white;
    padding: 12px;
    cursor: pointer;
    font-weight: 600;
}}

td {{
    padding: 10px 12px;
    border-bottom: 1px solid #eee;
}}

tr:hover {{
    background: #f8fafc;
}}

.ptw {{
    background: #ecfdf5;
}}

.center {{
    text-align: center;
}}

.ptw .title-main::after {{
    content: " ✓ PTW";
    color: #059669;
    font-size: 12px;
    font-weight: bold;
}}

.badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: bold;
    background: #e5e7eb;
}}

.not-added {{
    background: #fef2f2;
}}

.tv {{
    background: #dbeafe;
}}

.movie {{
    background: #fef3c7;
}}

.ova {{
    background: #ede9fe;
}}

.ona {{
    background: #cffafe;
}}

.special {{
    background: #f3f4f6;
}}

.upcoming-badge {{
    background: #f59e0b;
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: bold;
    font-size: 12px;
}}

.unknown-year-badge {{
    background: #6b7280;
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: bold;
    font-size: 12px;
}}

.unknown-score-badge {{
    background: #6b7280;
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: bold;
    font-size: 12px;
}}

.mal-button {{
    background: #2e51a2;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    display: inline-block;
    font-size: 12px;
    font-weight: bold;
    transition: background .15s ease;
}}

.mal-button:hover {{
    background: #1f3f87;
}}

a {{
    text-decoration: none;
}}

</style>

<script>

function applyFilters() {{

    const hidePTW =
        document.getElementById(
            "hidePTW"
        ).checked;
        
    const hideUpcoming =
        document.getElementById(
            "hideUpcoming"
        ).checked;

    const selectedType =
        document.getElementById(
            "typeFilter"
        ).value;

    const rows =
        document.querySelectorAll(
            "#animeTable tbody tr"
        );

    rows.forEach(row => {{

        const isPTW =
            row.dataset.ptw === "true";
            
        const isUpcoming =
            row.dataset.upcoming === "true";

        const rowType =
            row.dataset.type;

        const ptwPass =
            !hidePTW || !isPTW;
            
        const upcomingPass =
            !hideUpcoming || !isUpcoming;

        const typePass =
            selectedType === ""
            || rowType === selectedType;

        row.style.display =
            ptwPass &&
            upcomingPass &&
            typePass
                ? ""
                : "none";

    }});
}}

function sortTable(n) {{

    const table =
        document.getElementById(
            "animeTable"
        );

    const tbody =
        table.querySelector("tbody");

    const rows =
        Array.from(
            tbody.rows
        );

    const asc =
    table.dataset.column != n ||
    table.dataset.sort !== "asc";

    rows.sort((a, b) => {{

        const x =
            a.cells[n]
             .innerText
             .trim();

        const y =
            b.cells[n]
             .innerText
             .trim();

        const numX = parseFloat(x);
        const numY = parseFloat(y);

        if (!isNaN(numX) && !isNaN(numY)) {{
            return asc
                ? numX - numY
                : numY - numX;
        }}

        return asc
            ? x.localeCompare(y)
            : y.localeCompare(x);

    }});

    rows.forEach(
    row => tbody.appendChild(row)
    );
    
    table.dataset.column = n;
    table.dataset.sort =
        asc ? "asc" : "desc";
    
    applyFilters();
}}

window.onload = function () {{
    applyFilters();
}};

</script>

</head>

<body>

<h1>🎬 MAL Missing Anime</h1>

<div class="controls">

<label>
<input
    type="checkbox"
    id="hidePTW"
    onchange="applyFilters()">
Hide Planned to Watch
</label>

&nbsp;&nbsp;&nbsp;

<label>
<input
    type="checkbox"
    id="hideUpcoming"
    checked
    onchange="applyFilters()">
Hide Not Yet Released
</label>

&nbsp;&nbsp;&nbsp;

<select
    id="typeFilter"
    onchange="applyFilters()">

<option value="">
All Types
</option>

<option value="TV">
TV
</option>

<option value="Movie">
Movie
</option>

<option value="OVA">
OVA
</option>

<option value="ONA">
ONA
</option>

<option value="Special">
Special
</option>

</select>

</div>

<table id="animeTable">

<thead>
<tr>

<th class="title-column" onclick="sortTable(0)">
Title ↕
</th>

<th class="center" onclick="sortTable(1)">
Type ↕
</th>


<th class="center" onclick="sortTable(2)">
Episodes ↕
</th>


<th class="center" onclick="sortTable(3)">
Year ↕
</th>

<th class="center" onclick="sortTable(4)">
Score ↕
</th>


<th class="center">
MAL
</th>

</tr>
</thead>

<tbody>
"""

    for anime_id, data in sorted(
            missing.items(),
            key=lambda x: (
                    (
                            float(x[1].get("episodes", 0))
                            if str(x[1].get("episodes", "?")).replace(".", "").isdigit()
                            else 0
                    ),
                    -(
                            float(x[1].get("score", 0))
                            if str(x[1].get("score", "?")).replace(".", "").isdigit()
                            else 0
                    ),
                    -(
                            float(x[1].get("year", 0))
                            if str(x[1].get("year", "?")).replace(".", "").isdigit()
                            else 0
                    ),
            ),
    ):
        row_class = "ptw" if data["planned"] else "not-added"

        anime_type = data["type"].lower().replace(" ", "")

        episode_display = (
            '<span class="upcoming-badge">Upcoming</span>'
            if data.get("upcoming")
            else data.get("episodes", "?")
        )

        year_display = (
            '<span class="unknown-year-badge">Unknown</span>'
            if data.get("year") == "?"
            else data.get("year")
        )

        score_display = (
            '<span class="unknown-score-badge">Unknown</span>'
            if data.get("score") == "?"
            else data.get("score")
        )

        html += f"""

<tr
class="{row_class}"
data-type="{data['type']}"
data-ptw="{str(data['planned']).lower()}"
data-upcoming="{str(data.get('upcoming', False)).lower()}">

<td>

<div class="title-main">
{data['english_title']}
</div>

<div class="title-sub">
{data['title']}
</div>

</td>

<td class="center">
<span class="badge {anime_type}">
{data['type']}
</span>
</td>

<td class="center">
{episode_display}
</td>

<td class="center">
{year_display}
</td>

<td class="center">
{score_display}
</td>

<td class="center">
<a href="{data['url']}" target="_blank">
<span class="mal-button">
Open
</span>
</a>
</td>

</tr>
"""

    html += """
</tbody>
</table>

</body>
</html>
"""

    report_path = Path("missing_related_anime.html")

    report_path.write_text(html, encoding="utf-8")

    try:
        webbrowser.open(report_path.resolve().as_uri())
    except Exception:
        pass


# ============================================================
# MAIN
# ============================================================


def main():
    username = input("Enter MyAnimeList username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    try:
        anime_list = get_user_list(username)

    except Exception as e:
        print(f"Failed to load MAL list for '{username}'.")
        print(e)
        return

    print(f"Loaded {len(anime_list)} entries")

    planned_ids = {anime["anime_id"] for anime in anime_list if anime["status"] == 6}

    source_ids = {
        anime["anime_id"]
        for anime in anime_list
        if anime["status"] in {1, 2}  # Watching + Completed
    }

    existing_ids = {
        anime["anime_id"]
        for anime in anime_list
        if anime["status"] in {1, 2, 3, 4}  # Watching, Completed, On Hold, Dropped
    }

    known_titles = {anime["anime_id"]: anime["anime_title"] for anime in anime_list}

    missing = {}

    progress = tqdm(source_ids, desc="Scanning", unit=" anime", dynamic_ncols=True)

    for i, anime_id in enumerate(progress, start=1):

        current_title = str(known_titles.get(anime_id, anime_id))

        if i % 10 == 0:
            progress.set_postfix_str(current_title[:60])

        relations, cache_hit = get_related_anime(anime_id)

        for relation in relations:

            related_id = relation["id"]

            if related_id in existing_ids:
                continue

            anime_type = TYPE_NORMALIZATION.get(relation["type"], relation["type"])

            if related_id not in missing:
                missing[related_id] = {
                    "title": relation["title"],
                    "relation": relation["relation"],
                    "type": anime_type,
                    "episodes": "?",
                    "planned": related_id in planned_ids,
                    "url": f"https://myanimelist.net/anime/{related_id}",
                }

        if not cache_hit:
            time.sleep(REQUEST_DELAY)

    print()
    print("Loading metadata...")

    episode_progress = tqdm(
        missing.items(), desc="Scanning", unit=" anime", dynamic_ncols=True
    )

    for i, (anime_id, data) in enumerate(episode_progress, start=1):
        meta = get_anime_metadata(anime_id)

        data["episodes"] = meta["episodes"]

        data["upcoming"] = str(meta["score"]).strip().lower() in {"?", "unknown", "n/a"}

        data["english_title"] = (
            meta["english_title"] if meta["english_title"] else data["title"]
        )

        data["year"] = meta["year"]

        data["score"] = meta["score"]

        if i % 10 == 0:
            episode_progress.set_postfix_str(data["title"][:50])

    generate_html_report(missing)

    print()
    print("=" * 50)
    print(f"Scanned: {len(source_ids)}")
    print(f"Missing: {len(missing)}")
    print("Report saved as:")
    print("missing_related_anime.html")
    print("=" * 50)


if __name__ == "__main__":
    main()
