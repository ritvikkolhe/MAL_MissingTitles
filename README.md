# MyAnimeList Missing Related Anime

Find missing entries in your anime franchises by scanning your MyAnimeList and generating an interactive HTML report.

## Overview

This tool analyzes your MyAnimeList anime list and discovers franchise entries that are related to anime you are currently watching or have completed, but are not already present on your list.

The goal is to answer questions like:

- Did I miss a sequel?
- Is there a side story I never added?
- Am I missing an OVA, movie, or spin-off from a franchise?
- Which franchise entries are already in my Plan To Watch list?
- Which unreleased franchise entries have already been announced?

The script generates a sortable and filterable HTML report containing useful metadata such as:

- English title
- Anime type
- Episode count
- Release year
- MAL score
- Plan To Watch status
- Direct MAL link

---

## Features

### Franchise Discovery

Scans the following relationship types:

- Prequel
- Sequel
- Parent Story
- Full Story
- Side Story
- Spin-Off

### Metadata Extraction

For every discovered anime:

- English title
- Episode count
- Release year
- MyAnimeList score

### Interactive HTML Report

Includes:

- Sortable columns
- Type filtering
- Plan To Watch highlighting
- Hide Plan To Watch toggle
- Hide unreleased anime toggle
- Direct MAL links
- Score display
- Release year display

### Smart List Handling

The script scans only:

- Watching
- Completed

The following statuses are excluded from scanning:

- Plan To Watch
- On Hold
- Dropped

Anime already present in any of these statuses are not recommended again.

### Plan To Watch Support

Plan To Watch entries are:

- Included in the report
- Visually highlighted
- Not used as traversal roots

This allows you to see existing PTW entries while preventing franchise expansion through anime you have not actually watched.

### Unreleased Anime Detection

Upcoming anime with incomplete MAL metadata are automatically identified and can be hidden from the report using the built-in filter.

### Local Caching

Downloaded anime pages are stored locally.

Benefits:

- Faster reruns
- Fewer requests to MAL
- Reduced chance of rate limiting

---

## Installation

### Clone Repository

```bash
git clone https://github.com/<username>/MAL_MissingTitles.git
cd MAL_MissingTitles
```

### Install Dependencies

```bash
pip install requests beautifulsoup4 tqdm
```

---

## Usage

Run:

```bash
python mal_watch_priority.py
```

Enter your MyAnimeList username:

```text
Enter MyAnimeList username: MyUsername
```

Example:

```text
Loaded 823 entries
Scanning...
Loading metadata...
```

After completion:

```text
==================================================
Scanned: 623
Missing: 147
Report saved as:
missing_related_anime.html
==================================================
```

The report will automatically open in your default browser.

---

## How It Works

### Step 1

Download your public anime list:

```text
https://myanimelist.net/animelist/<username>/load.json
```

### Step 2

For every anime marked as Watching or Completed:

- Download MAL page
- Extract related anime
- Filter allowed relationship types

### Step 3

Exclude entries already present on your list:

- Watching
- Completed
- On Hold
- Dropped

Plan To Watch entries remain visible and highlighted.

### Step 4

Gather metadata:

- Episodes
- Release year
- English title
- MAL score

### Step 5

Generate an interactive HTML report.

---

## Caching

All downloaded anime pages are stored inside:

```text
cache/
```

Example:

```text
cache/
├── 1.html
├── 20.html
├── 15417.html
└── ...
```

Delete the folder at any time to force a complete refresh.

---

## Relationship Rules

### Included

```text
Prequel
Sequel
Parent Story
Full Story
Side Story
Spin-Off
```

### Ignored

```text
Adaptation
Character
Summary
Alternative Version
Alternative Setting
Other
```

This keeps recommendations focused on actual franchise viewing order and related entries.

---

## Report Features

The generated report supports:

- Sortable columns
- Type filtering
- Hide Plan To Watch entries
- Hide unreleased entries
- Plan To Watch highlighting
- Episode counts
- Release years
- MAL scores
- Direct MAL links

---

## Output File

Generated report:

```text
missing_related_anime.html
```

---

## Dependencies

- requests
- beautifulsoup4
- tqdm

---

## Limitations

This project relies on publicly available MyAnimeList data and page structure.

Results may be affected by:

- Changes to MAL page layouts
- Missing entries in MAL's `load.json` endpoint
- Incomplete metadata on MAL
- Hidden or unavailable anime entries

---

## Disclaimer

This project is an unofficial utility and is not affiliated with MyAnimeList.

Please be respectful of MyAnimeList resources and avoid unnecessarily deleting the cache between runs.

---

## Author

**Ritvik Kolhe**
