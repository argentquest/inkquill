"""
Seed the tag_taxonomy_entries table from multiple sources:
  - Hand-curated data (always available, runs first)
  - O*NET Occupation Data CSV (optional, if file path provided)
  - MusicBrainz REST API (optional, requires network)
  - Wikidata SPARQL (optional, requires network)

Usage:
    python -m app.scripts.seed_tag_taxonomy
    python -m app.scripts.seed_tag_taxonomy --onet path/to/Occupation_Data.txt
    python -m app.scripts.seed_tag_taxonomy --skip-musicbrainz --skip-wikidata
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Hand-curated data
# ---------------------------------------------------------------------------

CURATED: dict[str, list[tuple[str, str]]] = {
    # (category, label)
    "hobbies": [
        ("Outdoor & Nature", "Gardening"),
        ("Outdoor & Nature", "Bird watching"),
        ("Outdoor & Nature", "Fishing"),
        ("Outdoor & Nature", "Golf"),
        ("Outdoor & Nature", "Walking"),
        ("Outdoor & Nature", "Hiking"),
        ("Outdoor & Nature", "Swimming"),
        ("Outdoor & Nature", "Camping"),
        ("Arts & Crafts", "Knitting"),
        ("Arts & Crafts", "Crocheting"),
        ("Arts & Crafts", "Quilting"),
        ("Arts & Crafts", "Sewing"),
        ("Arts & Crafts", "Painting"),
        ("Arts & Crafts", "Drawing"),
        ("Arts & Crafts", "Woodworking"),
        ("Arts & Crafts", "Pottery"),
        ("Arts & Crafts", "Photography"),
        ("Arts & Crafts", "Scrapbooking"),
        ("Arts & Crafts", "Flower arranging"),
        ("Games & Puzzles", "Crossword puzzles"),
        ("Games & Puzzles", "Jigsaw puzzles"),
        ("Games & Puzzles", "Card games"),
        ("Games & Puzzles", "Dominoes"),
        ("Games & Puzzles", "Chess"),
        ("Games & Puzzles", "Checkers"),
        ("Games & Puzzles", "Board games"),
        ("Games & Puzzles", "Bingo"),
        ("Faith & Community", "Church attendance"),
        ("Faith & Community", "Bible study"),
        ("Faith & Community", "Volunteering"),
        ("Faith & Community", "Choir"),
        ("Faith & Community", "Prayer group"),
        ("Faith & Community", "Community service"),
        ("Music & Dancing", "Singing"),
        ("Music & Dancing", "Dancing"),
        ("Music & Dancing", "Playing piano"),
        ("Music & Dancing", "Playing guitar"),
        ("Music & Dancing", "Listening to music"),
        ("Music & Dancing", "Square dancing"),
        ("Reading & Learning", "Reading books"),
        ("Reading & Learning", "Reading the Bible"),
        ("Reading & Learning", "Listening to audiobooks"),
        ("Reading & Learning", "Visiting the library"),
        ("Reading & Learning", "Poetry"),
        ("Cooking & Home", "Baking"),
        ("Cooking & Home", "Cooking"),
        ("Cooking & Home", "Canning & preserving"),
        ("Cooking & Home", "Home decorating"),
        ("Collecting", "Stamp collecting"),
        ("Collecting", "Coin collecting"),
        ("Collecting", "Antiques"),
        ("Collecting", "Model trains"),
    ],
    "favoriteActivities": [
        ("Gentle Movement", "Chair yoga"),
        ("Gentle Movement", "Gentle stretching"),
        ("Gentle Movement", "Walking"),
        ("Gentle Movement", "Swimming"),
        ("Gentle Movement", "Tai chi"),
        ("Gentle Movement", "Water aerobics"),
        ("Social & Games", "Bingo"),
        ("Social & Games", "Card games"),
        ("Social & Games", "Group singing"),
        ("Social & Games", "Trivia games"),
        ("Social & Games", "Board games"),
        ("Social & Games", "Dominoes"),
        ("Creative", "Coloring"),
        ("Creative", "Arts and crafts"),
        ("Creative", "Journaling"),
        ("Creative", "Scrapbooking"),
        ("Creative", "Drawing"),
        ("Creative", "Knitting or crocheting"),
        ("Entertainment", "Watching TV"),
        ("Entertainment", "Watching movies"),
        ("Entertainment", "Listening to music"),
        ("Entertainment", "Reading aloud"),
        ("Entertainment", "Audiobooks"),
        ("Outdoors", "Porch sitting"),
        ("Outdoors", "Bird feeding"),
        ("Outdoors", "Garden walk"),
        ("Outdoors", "Nature walk"),
        ("Outdoors", "Feeding ducks"),
        ("Spiritual", "Prayer"),
        ("Spiritual", "Devotional reading"),
        ("Spiritual", "Hymn singing"),
        ("Spiritual", "Church service"),
    ],
    "lifeRoles": [
        ("Family", "Mother"),
        ("Family", "Father"),
        ("Family", "Grandmother"),
        ("Family", "Grandfather"),
        ("Family", "Homemaker"),
        ("Family", "Caregiver"),
        ("Family", "Stay-at-home parent"),
        ("Education", "Teacher"),
        ("Education", "Principal"),
        ("Education", "Librarian"),
        ("Education", "Professor"),
        ("Education", "School counselor"),
        ("Healthcare", "Nurse"),
        ("Healthcare", "Doctor"),
        ("Healthcare", "Pharmacist"),
        ("Healthcare", "Midwife"),
        ("Healthcare", "Dentist"),
        ("Healthcare", "Nursing home aide"),
        ("Trades & Labor", "Farmer"),
        ("Trades & Labor", "Carpenter"),
        ("Trades & Labor", "Mechanic"),
        ("Trades & Labor", "Plumber"),
        ("Trades & Labor", "Electrician"),
        ("Trades & Labor", "Factory worker"),
        ("Trades & Labor", "Coal miner"),
        ("Business & Office", "Business owner"),
        ("Business & Office", "Secretary"),
        ("Business & Office", "Accountant"),
        ("Business & Office", "Bank teller"),
        ("Business & Office", "Office manager"),
        ("Business & Office", "Sales clerk"),
        ("Community & Faith", "Pastor"),
        ("Community & Faith", "Deacon"),
        ("Community & Faith", "Volunteer"),
        ("Community & Faith", "Scout leader"),
        ("Community & Faith", "Coach"),
        ("Community & Faith", "Civil servant"),
        ("Military & Service", "Army veteran"),
        ("Military & Service", "Navy veteran"),
        ("Military & Service", "Police officer"),
        ("Military & Service", "Firefighter"),
        ("Agriculture", "Rancher"),
        ("Agriculture", "Dairy farmer"),
        ("Agriculture", "Crop farmer"),
    ],
    "pets": [
        ("Pets", "Cat"),
        ("Pets", "Dog"),
        ("Pets", "Bird"),
        ("Pets", "Fish"),
        ("Pets", "Rabbit"),
        ("Pets", "Turtle"),
        ("Pets", "Hamster"),
        ("Pets", "Canary"),
        ("Pets", "Parakeet"),
        ("Pets", "No pets"),
    ],
    "favouriteFoods": [
        ("Home Cooking", "Mashed potatoes"),
        ("Home Cooking", "Pot roast"),
        ("Home Cooking", "Fried chicken"),
        ("Home Cooking", "Chicken soup"),
        ("Home Cooking", "Meatloaf"),
        ("Home Cooking", "Ham and beans"),
        ("Home Cooking", "Pork chops"),
        ("Home Cooking", "Beef stew"),
        ("Home Cooking", "Chicken and dumplings"),
        ("Home Cooking", "Liver and onions"),
        ("Baked Goods", "Apple pie"),
        ("Baked Goods", "Cornbread"),
        ("Baked Goods", "Biscuits and gravy"),
        ("Baked Goods", "Peach cobbler"),
        ("Baked Goods", "Banana bread"),
        ("Baked Goods", "Pound cake"),
        ("Baked Goods", "Cinnamon rolls"),
        ("Comfort Sweets", "Ice cream"),
        ("Comfort Sweets", "Chocolate cake"),
        ("Comfort Sweets", "Rice pudding"),
        ("Comfort Sweets", "Banana pudding"),
        ("Comfort Sweets", "Pecan pie"),
        ("Comfort Sweets", "Bread pudding"),
        ("Southern & Regional", "Collard greens"),
        ("Southern & Regional", "Black-eyed peas"),
        ("Southern & Regional", "Grits"),
        ("Southern & Regional", "Sweet tea"),
        ("Southern & Regional", "Cornbread dressing"),
        ("Southern & Regional", "Deviled eggs"),
        ("Southern & Regional", "Macaroni and cheese"),
        ("Southern & Regional", "Green bean casserole"),
        ("Breakfast", "Bacon and eggs"),
        ("Breakfast", "Pancakes"),
        ("Breakfast", "Oatmeal"),
        ("Breakfast", "Waffles"),
        ("Breakfast", "Cream of wheat"),
    ],
    "favouriteTvShows": [
        ("Classic Comedy", "I Love Lucy"),
        ("Classic Comedy", "The Andy Griffith Show"),
        ("Classic Comedy", "The Dick Van Dyke Show"),
        ("Classic Comedy", "Gilligan's Island"),
        ("Classic Comedy", "Green Acres"),
        ("Classic Comedy", "Hogan's Heroes"),
        ("Classic Comedy", "Bewitched"),
        ("Classic Comedy", "The Beverly Hillbillies"),
        ("Classic Comedy", "Get Smart"),
        ("Classic Comedy", "Mork & Mindy"),
        ("Classic Comedy", "All in the Family"),
        ("Variety & Music", "The Lawrence Welk Show"),
        ("Variety & Music", "The Ed Sullivan Show"),
        ("Variety & Music", "Hee Haw"),
        ("Variety & Music", "The Carol Burnett Show"),
        ("Variety & Music", "The Johnny Carson Show"),
        ("Variety & Music", "The Bob Hope Show"),
        ("Drama & Western", "Gunsmoke"),
        ("Drama & Western", "Bonanza"),
        ("Drama & Western", "Little House on the Prairie"),
        ("Drama & Western", "Dallas"),
        ("Drama & Western", "The Waltons"),
        ("Drama & Western", "Highway to Heaven"),
        ("Drama & Western", "Touched by an Angel"),
        ("Drama & Western", "Murder, She Wrote"),
        ("Game Shows", "Wheel of Fortune"),
        ("Game Shows", "The Price is Right"),
        ("Game Shows", "Jeopardy!"),
        ("Game Shows", "Let's Make a Deal"),
        ("Game Shows", "Family Feud"),
        ("Game Shows", "What's My Line?"),
        ("News & Documentary", "60 Minutes"),
        ("News & Documentary", "National Geographic"),
        ("News & Documentary", "PBS NewsHour"),
        ("Soap Operas", "General Hospital"),
        ("Soap Operas", "Days of Our Lives"),
        ("Soap Operas", "The Young and the Restless"),
        ("Soap Operas", "As the World Turns"),
    ],
    "favoriteSingers": [
        ("Classic Country", "Patsy Cline"),
        ("Classic Country", "Johnny Cash"),
        ("Classic Country", "Dolly Parton"),
        ("Classic Country", "Loretta Lynn"),
        ("Classic Country", "Willie Nelson"),
        ("Classic Country", "Hank Williams"),
        ("Classic Country", "Tammy Wynette"),
        ("Classic Country", "Glen Campbell"),
        ("Classic Country", "Kenny Rogers"),
        ("Classic Country", "Charlie Pride"),
        ("Classic Country", "Merle Haggard"),
        ("Classic Country", "George Jones"),
        ("Classic Pop", "Frank Sinatra"),
        ("Classic Pop", "Doris Day"),
        ("Classic Pop", "Perry Como"),
        ("Classic Pop", "Dean Martin"),
        ("Classic Pop", "Nat King Cole"),
        ("Classic Pop", "Perry Como"),
        ("Classic Pop", "Andy Williams"),
        ("Classic Pop", "Tony Bennett"),
        ("Classic Pop", "Rosemary Clooney"),
        ("Gospel", "Mahalia Jackson"),
        ("Gospel", "Bill Gaither"),
        ("Gospel", "George Beverly Shea"),
        ("Gospel", "Tennessee Ernie Ford"),
        ("Gospel", "Elvis Presley (gospel)"),
        ("Gospel", "The Oak Ridge Boys"),
        ("Rock & Roll", "Elvis Presley"),
        ("Rock & Roll", "Buddy Holly"),
        ("Rock & Roll", "Chuck Berry"),
        ("Rock & Roll", "Jerry Lee Lewis"),
        ("Rock & Roll", "Fats Domino"),
        ("Big Band & Jazz", "Ella Fitzgerald"),
        ("Big Band & Jazz", "Louis Armstrong"),
        ("Big Band & Jazz", "Glenn Miller"),
        ("Big Band & Jazz", "Benny Goodman"),
        ("Big Band & Jazz", "Bing Crosby"),
        ("Big Band & Jazz", "Dinah Shore"),
        ("Big Band & Jazz", "Peggy Lee"),
        ("Big Band & Jazz", "Patti Page"),
        ("Folk & Bluegrass", "John Denver"),
        ("Folk & Bluegrass", "Jim Reeves"),
        ("Folk & Bluegrass", "Roy Acuff"),
        ("Folk & Bluegrass", "Bill Monroe"),
        ("Soul & R&B", "Aretha Franklin"),
        ("Soul & R&B", "Ray Charles"),
        ("Soul & R&B", "Sam Cooke"),
    ],
}


# ---------------------------------------------------------------------------
# O*NET importer (reads downloaded CSV)
# ---------------------------------------------------------------------------

def _load_onet(filepath: str) -> list[tuple[str, str, str]]:
    """Parse O*NET Occupation Data CSV and return (field_key, category, label) rows."""
    import csv

    # Mapping of O*NET major group codes to our categories
    # O*NET SOC codes: first 2 digits = major group
    major_group_to_category = {
        "11": "Business & Office",   # Management
        "13": "Business & Office",   # Business & Financial
        "15": "Business & Office",   # Computer & Math
        "17": "Trades & Labor",      # Architecture & Engineering
        "19": "Education",           # Life/Physical/Social Science
        "21": "Community & Faith",   # Community & Social Service
        "23": "Business & Office",   # Legal
        "25": "Education",           # Educational Instruction
        "27": "Arts & Crafts",       # Arts, Design, Media
        "29": "Healthcare",          # Healthcare Practitioners
        "31": "Healthcare",          # Healthcare Support
        "33": "Military & Service",  # Protective Service
        "35": "Business & Office",   # Food Prep
        "37": "Trades & Labor",      # Building/Grounds Maintenance
        "39": "Community & Faith",   # Personal Care & Service
        "41": "Business & Office",   # Sales
        "43": "Business & Office",   # Office Support
        "45": "Agriculture",         # Farming, Fishing, Forestry
        "47": "Trades & Labor",      # Construction
        "49": "Trades & Labor",      # Installation & Repair
        "51": "Trades & Labor",      # Production
        "53": "Trades & Labor",      # Transportation
        "55": "Military & Service",  # Military
    }

    rows = []
    try:
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                title = row.get("Title", "").strip()
                code = row.get("O*NET-SOC Code", row.get("Code", "")).strip()
                if not title or not code:
                    continue
                major = code[:2]
                category = major_group_to_category.get(major, "Other")
                rows.append(("lifeRoles", category, title))
    except Exception as exc:
        print(f"  Warning: could not parse O*NET file: {exc}", file=sys.stderr)
    return rows


# ---------------------------------------------------------------------------
# MusicBrainz importer
# ---------------------------------------------------------------------------

def _fetch_musicbrainz() -> list[tuple[str, str, str]]:
    """Query MusicBrainz for senior-era artists. Returns (field_key, category, label) rows."""
    import urllib.request
    import json as _json

    genre_to_category = {
        "country": "Classic Country",
        "traditional country": "Classic Country",
        "bluegrass": "Folk & Bluegrass",
        "folk": "Folk & Bluegrass",
        "gospel": "Gospel",
        "christian": "Gospel",
        "pop": "Classic Pop",
        "traditional pop": "Classic Pop",
        "easy listening": "Classic Pop",
        "jazz": "Big Band & Jazz",
        "big band": "Big Band & Jazz",
        "swing": "Big Band & Jazz",
        "blues": "Soul & R&B",
        "soul": "Soul & R&B",
        "rhythm and blues": "Soul & R&B",
        "rock and roll": "Rock & Roll",
        "rockabilly": "Rock & Roll",
    }

    seen: set[str] = set()
    rows: list[tuple[str, str, str]] = []

    # Already in curated — collect existing names to avoid dupes
    for _, label in CURATED.get("favoriteSingers", []):
        seen.add(label.lower())

    queries = [
        "tag:country AND type:person",
        "tag:gospel AND type:person",
        "tag:jazz AND type:person",
        "tag:big+band AND type:person",
        "tag:traditional+pop AND type:person",
        "tag:soul AND type:person",
        "tag:rockabilly AND type:person",
    ]

    for query in queries:
        try:
            url = f"https://musicbrainz.org/ws/2/artist?query={query}&fmt=json&limit=25"
            req = urllib.request.Request(url, headers={"User-Agent": "InkQuillTagSeed/1.0 (care@inkquill.app)"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = _json.loads(resp.read())
            time.sleep(1.1)  # MusicBrainz rate limit: 1 req/sec

            for artist in data.get("artists", []):
                name = artist.get("name", "").strip()
                if not name or name.lower() in seen:
                    continue
                # Estimate era from life-span
                begin = (artist.get("life-span") or {}).get("begin", "") or ""
                begin_year = int(begin[:4]) if begin and begin[:4].isdigit() else None
                if begin_year and begin_year > 1960:
                    continue  # Too recent for senior era

                # Pick category from tags
                tags = [t.get("name", "").lower() for t in (artist.get("tags") or [])]
                category = "Classic Pop"
                for tag in tags:
                    if tag in genre_to_category:
                        category = genre_to_category[tag]
                        break

                seen.add(name.lower())
                rows.append(("favoriteSingers", category, name))
        except Exception as exc:
            print(f"  MusicBrainz query failed ({query}): {exc}", file=sys.stderr)

    return rows


# ---------------------------------------------------------------------------
# Wikidata SPARQL importer
# ---------------------------------------------------------------------------

def _fetch_wikidata() -> list[tuple[str, str, str]]:
    """Query Wikidata SPARQL for hobbies, TV shows, foods. Returns (field_key, category, label)."""
    import urllib.request
    import urllib.parse
    import json as _json

    endpoint = "https://query.wikidata.org/sparql"
    headers = {"User-Agent": "InkQuillTagSeed/1.0 (care@inkquill.app)", "Accept": "application/json"}

    queries = [
        # US TV series, 1950–1985
        (
            "favouriteTvShows",
            "Classic TV",
            """
            SELECT DISTINCT ?label WHERE {
              ?item wdt:P31 wd:Q5398426 .
              ?item wdt:P495 wd:Q30 .
              ?item wdt:P577 ?date .
              FILTER(YEAR(?date) >= 1950 && YEAR(?date) <= 1985)
              ?item rdfs:label ?label .
              FILTER(LANG(?label) = "en")
            } LIMIT 150
            """,
        ),
        # Common hobbies
        (
            "hobbies",
            "Popular Hobbies",
            """
            SELECT DISTINCT ?label WHERE {
              ?item wdt:P31 wd:Q55498524 .
              ?item rdfs:label ?label .
              FILTER(LANG(?label) = "en")
            } LIMIT 80
            """,
        ),
        # Traditional American foods
        (
            "favouriteFoods",
            "American Classics",
            """
            SELECT DISTINCT ?label WHERE {
              ?item wdt:P31/wdt:P279* wd:Q2095 .
              ?item wdt:P17 wd:Q30 .
              ?item rdfs:label ?label .
              FILTER(LANG(?label) = "en")
              FILTER(STRLEN(?label) < 40)
            } LIMIT 80
            """,
        ),
    ]

    rows: list[tuple[str, str, str]] = []
    existing: dict[str, set[str]] = {fk: {l.lower() for _, l in items} for fk, items in CURATED.items()}

    for field_key, category, sparql in queries:
        try:
            encoded = urllib.parse.urlencode({"query": sparql, "format": "json"})
            url = f"{endpoint}?{encoded}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = _json.loads(resp.read())
            time.sleep(1.0)

            field_seen = existing.get(field_key, set())
            for binding in data.get("results", {}).get("bindings", []):
                label = binding.get("label", {}).get("value", "").strip()
                if not label or label.lower() in field_seen or len(label) > 50:
                    continue
                field_seen.add(label.lower())
                rows.append((field_key, category, label))
        except Exception as exc:
            print(f"  Wikidata query failed ({field_key}): {exc}", file=sys.stderr)

    return rows


# ---------------------------------------------------------------------------
# Database seeding
# ---------------------------------------------------------------------------

async def _seed(onet_path: str | None, skip_musicbrainz: bool, skip_wikidata: bool) -> None:
    import os
    import sys

    # Add repo root to path
    repo_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(repo_root))

    from app.db.database import async_session_local
    from app.models.care_circle import TagTaxonomyEntry

    print("Collecting entries from curated data...")
    all_entries: list[tuple[str, str, str, str]] = []  # (field_key, category, label, source)

    for field_key, items in CURATED.items():
        for category, label in items:
            all_entries.append((field_key, category, label, "curated"))

    if onet_path:
        print(f"Loading O*NET data from {onet_path}...")
        onet_rows = _load_onet(onet_path)
        print(f"  Found {len(onet_rows)} O*NET occupation entries")
        for fk, cat, label in onet_rows:
            all_entries.append((fk, cat, label, "onet"))

    if not skip_musicbrainz:
        print("Fetching MusicBrainz artists (this may take ~30s due to rate limiting)...")
        mb_rows = _fetch_musicbrainz()
        print(f"  Found {len(mb_rows)} MusicBrainz entries")
        for fk, cat, label in mb_rows:
            all_entries.append((fk, cat, label, "musicbrainz"))

    if not skip_wikidata:
        print("Fetching Wikidata entries (hobbies, TV shows, foods)...")
        wd_rows = _fetch_wikidata()
        print(f"  Found {len(wd_rows)} Wikidata entries")
        for fk, cat, label in wd_rows:
            all_entries.append((fk, cat, label, "wikidata"))

    # Deduplicate within the batch: keep first occurrence per (field_key, label)
    seen: set[tuple[str, str]] = set()
    deduped: list[tuple[str, str, str, str]] = []
    for entry in all_entries:
        key = (entry[0], entry[2])  # (field_key, label)
        if key not in seen:
            seen.add(key)
            deduped.append(entry)

    print(f"\nSeeding {len(deduped)} unique entries into database...")

    from sqlalchemy.dialects.postgresql import insert as pg_insert

    async with async_session_local() as db:
        rows = [
            {
                "field_key": field_key,
                "category": category,
                "label": label,
                "sort_order": sort_order,
                "source": source,
                "is_active": True,
            }
            for sort_order, (field_key, category, label, source) in enumerate(deduped)
        ]

        stmt = pg_insert(TagTaxonomyEntry).values(rows)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_tag_taxonomy_field_label")
        result = await db.execute(stmt)
        await db.commit()

    inserted = result.rowcount if result.rowcount >= 0 else len(rows)
    print(f"Done. Rows processed: {len(rows)}, Inserted (approx): {inserted}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed tag taxonomy entries")
    parser.add_argument("--onet", metavar="PATH", help="Path to O*NET Occupation_Data.txt")
    parser.add_argument("--skip-musicbrainz", action="store_true", help="Skip MusicBrainz API")
    parser.add_argument("--skip-wikidata", action="store_true", help="Skip Wikidata SPARQL")
    args = parser.parse_args()

    asyncio.run(_seed(
        onet_path=args.onet,
        skip_musicbrainz=args.skip_musicbrainz,
        skip_wikidata=args.skip_wikidata,
    ))


if __name__ == "__main__":
    main()
