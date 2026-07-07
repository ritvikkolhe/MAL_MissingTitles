# MyAnimeList Missing Related Anime

Find missing entries in your anime franchises by scanning your MyAnimeList and generating an interactive HTML report.

## Overview

This tool analyzes the anime on your MyAnimeList and discovers related entries that are not currently watched while still preserving **Plan To Watch (PTW)** entries for visibility.

The goal is to answer questions like:

- Did I miss a sequel?
- Is there a side story I never added?
- Am I missing an OVA, movie, or spin-off from a franchise?
- Which franchise entries are already in my PTW list?

The script generates a sortable and filterable HTML report showing all missing related anime along with useful metadata such as:

- English title
- Type
- Episode count
- Release year
- MAL score
- PTW status
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
- PTW highlighting
- PTW hide/show toggle
- Direct MAL links
- Score sorting

### Smart PTW Handling

PTW entries are:

- Included in the report
- Visually highlighted
- Not used as traversal roots

This allows you to see existing PTW entries while preventing franchise expansion through anime you have not actually watched.

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
cd mal-missing-related-anime
```

### Install Dependencies

```bash
pip install requests beautifulsoup4 tqdm
```

---

## Usage

Run:

```bash
python main.py
```

Enter your MyAnimeList username:

```text
Enter MyAnimeList username: MyUsername
```

Example:

```text
Loaded 823 entries
Scanning: 100%|██████████|
Loading episode counts...
```

After completion:

```text
==================================================
Scanned: 823
Missing: 147
Report saved as:
missing_related_anime.html
==================================================
```

The report will automatically open in your browser.

---

## How It Works

### Step 1

Download your public anime list:

```text
https://myanimelist.net/animelist/<username>/load.json
```

### Step 2

For every non-PTW anime:

- Download MAL page
- Extract related anime
- Filter allowed relationship types

### Step 3

Remove entries already watched.

PTW entries remain visible.

### Step 4

Gather metadata:

- Episodes
- Release year
- English title
- Score

### Step 5

Generate interactive HTML report.

---

## Caching

All downloaded pages are stored inside:

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

Delete the folder anytime to force a full refresh.

---

## Relationship Rules

Included:

```text
Prequel
Sequel
Parent Story
Full Story
Side Story
Spin-Off
```

Ignored:

```text
Adaptation
Character
Summary
Alternative Version
Alternative Setting
Other
```

This keeps recommendations focused and relevant.

---

## Output File

Generated report:

```text
missing_related_anime.html
```

Contains:

- Sortable table
- Type filtering
- PTW highlighting
- MAL score display
- Unknown badges for unreleased entries

---

## Dependencies

- requests
- beautifulsoup4
- tqdm

---

## Disclaimer

This project is an unofficial utility and is not affiliated with MyAnimeList.

Please be respectful of MyAnimeList resources and avoid unnecessarily deleting the cache between runs.

---

## Author

**Ritvik Kolhe**
