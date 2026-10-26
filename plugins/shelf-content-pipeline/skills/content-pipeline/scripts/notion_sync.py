"""Notion sync for Content Pipeline (OPTIONAL).

Push developed/scheduled content ideas from the local database to a
Notion Content Pipeline database. Only needed if you want a team-visible
content calendar in Notion.

Functions:
    create_notion_database(parent_page_id) → database_id
    push_idea_to_notion(idea_dict) → notion_page_id
    update_notion_status(page_id, status, ...) → bool
    build_page_body(idea_dict) → list of Notion block objects

Setup:
    1. Create a Notion internal integration at https://www.notion.so/my-integrations
    2. Add NOTION_API_TOKEN and NOTION_PIPELINE_DB_ID to ~/.claude/.env
    3. Run: python3 ~/.claude/skills/content-pipeline/scripts/notion_sync.py --create-db PARENT_PAGE_ID

Usage:
    python3 notion_sync.py --create-db PAGE_ID    # One-time setup
    python3 notion_sync.py --test                  # Test connection
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / ".claude" / ".env")   # plugin convention
    load_dotenv(Path.cwd() / ".env")                  # a project .env also works
except ImportError:
    pass


def _get_headers():
    token = os.getenv("NOTION_API_TOKEN", "")
    if not token:
        raise ValueError(
            "Missing NOTION_API_TOKEN. Add it to ~/.claude/.env. "
            "Get one at https://www.notion.so/my-integrations"
        )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def _get_db_id():
    db_id = os.getenv("NOTION_PIPELINE_DB_ID", "")
    if not db_id:
        raise ValueError(
            "Missing NOTION_PIPELINE_DB_ID. Run: python3 notion_sync.py --create-db PAGE_ID"
        )
    return db_id


# --- Block helpers ---

def _txt(s, bold=False, italic=False, color="default"):
    return {
        "type": "text",
        "text": {"content": s},
        "annotations": {
            "bold": bold, "italic": italic, "strikethrough": False,
            "underline": False, "code": False, "color": color,
        },
    }

def _h2(s):
    return {"type": "heading_2", "heading_2": {"rich_text": [_txt(s)], "is_toggleable": False, "color": "gray_background"}}

def _bullet(s, bold=False):
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [_txt(s, bold=bold)]}}

def _para(s="", italic=False, color="default"):
    if not s:
        return {"type": "paragraph", "paragraph": {"rich_text": []}}
    return {"type": "paragraph", "paragraph": {"rich_text": [_txt(s, italic=italic, color=color)]}}

def _todo(s, checked=False):
    return {"type": "to_do", "to_do": {"rich_text": [_txt(s)], "checked": checked, "color": "default"}}

def _divider():
    return {"type": "divider", "divider": {}}


# --- Core functions ---

def create_notion_database(parent_page_id: str) -> str:
    """Create the Content Pipeline database in Notion. Returns the database ID."""
    headers = _get_headers()

    db_payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Content Pipeline"}}],
        "properties": {
            "Title": {"title": {}},
            "Channel": {"select": {"options": [
                {"name": "youtube", "color": "red"},
                {"name": "linkedin", "color": "blue"},
                {"name": "newsletter", "color": "green"},
                {"name": "podcast", "color": "purple"},
            ]}},
            "Format": {"select": {"options": [
                {"name": "long_form", "color": "default"},
                {"name": "tutorial", "color": "blue"},
                {"name": "short_form", "color": "yellow"},
                {"name": "post", "color": "green"},
                {"name": "article", "color": "purple"},
                {"name": "carousel", "color": "orange"},
                {"name": "vlog", "color": "pink"},
            ]}},
            "Production Status": {"select": {"options": [
                {"name": "Stub", "color": "default"},
                {"name": "Developed", "color": "blue"},
                {"name": "Scheduled", "color": "yellow"},
                {"name": "Filmed", "color": "orange"},
                {"name": "Editing", "color": "purple"},
                {"name": "Published", "color": "green"},
            ]}},
            "Film By": {"date": {}},
            "Publish Date": {"date": {}},
            "Edit Days": {"number": {}},
            "Priority": {"number": {}},
            "Audience": {"select": {}},
            "Offer": {"select": {}},
            "Funnel": {"select": {"options": [
                {"name": "awareness", "color": "blue"},
                {"name": "consideration", "color": "yellow"},
                {"name": "conversion", "color": "green"},
            ]}},
            "Content Pillar": {"select": {}},
            "Hook": {"rich_text": {}},
            "Authority Angle": {"rich_text": {}},
            "DB ID": {"number": {}},
        },
    }

    resp = requests.post("https://api.notion.com/v1/databases", headers=headers, json=db_payload)
    if resp.status_code not in (200, 201):
        print(f"Failed to create database ({resp.status_code}): {resp.text[:500]}")
        sys.exit(1)

    db_id = resp.json()["id"]
    print(f"Database created! ID: {db_id}")
    print("\nAdd this to ~/.claude/.env:")
    print(f"NOTION_PIPELINE_DB_ID={db_id}")
    return db_id


def push_idea_to_notion(idea: dict) -> str | None:
    """Push a content idea to the Notion Content Pipeline database.

    Returns Notion page_id if successful, None if failed.
    """
    headers = _get_headers()
    db_id = _get_db_id()

    props = {
        "Title": {"title": [{"text": {"content": idea.get("title", "Untitled")}}]},
        "DB ID": {"number": idea["id"]},
    }

    # Optional select properties
    for field, prop in [
        ("channel", "Channel"),
        ("format_type", "Format"),
        ("audience_segment", "Audience"),
        ("offer_alignment", "Offer"),
        ("funnel_position", "Funnel"),
        ("content_pillar", "Content Pillar"),
    ]:
        if idea.get(field):
            props[prop] = {"select": {"name": idea[field]}}

    if idea.get("production_status"):
        props["Production Status"] = {"select": {"name": _map_status(idea["production_status"])}}

    # Optional dates
    if idea.get("film_by_date"):
        props["Film By"] = {"date": {"start": idea["film_by_date"]}}
    if idea.get("publish_date"):
        props["Publish Date"] = {"date": {"start": idea["publish_date"]}}

    # Optional numbers
    if idea.get("edit_turnaround_days"):
        props["Edit Days"] = {"number": idea["edit_turnaround_days"]}
    if idea.get("priority_score"):
        props["Priority"] = {"number": idea["priority_score"]}

    # Optional text
    if idea.get("hook"):
        props["Hook"] = {"rich_text": [{"text": {"content": str(idea["hook"])[:2000]}}]}
    if idea.get("authority_angle"):
        props["Authority Angle"] = {"rich_text": [{"text": {"content": str(idea["authority_angle"])[:2000]}}]}

    page_payload = {"parent": {"database_id": db_id}, "properties": props}
    resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=page_payload)
    time.sleep(0.4)

    if resp.status_code not in (200, 201):
        print(f"Notion push failed ({resp.status_code}): {resp.text[:300]}")
        return None

    page_id = resp.json()["id"]

    # Append body blocks for developed ideas
    if idea.get("production_status") in ("developed", "scheduled", "filmed"):
        body_blocks = build_page_body(idea)
        if body_blocks:
            requests.patch(
                f"https://api.notion.com/v1/blocks/{page_id}/children",
                headers=headers,
                json={"children": body_blocks[:100]},
            )
            time.sleep(0.4)

    return page_id


def update_notion_status(page_id: str, status: str, film_by: str | None = None, publish_date: str | None = None) -> bool:
    """Update a Notion page's production status and optional dates."""
    headers = _get_headers()
    props = {"Production Status": {"select": {"name": _map_status(status)}}}
    if film_by:
        props["Film By"] = {"date": {"start": film_by}}
    if publish_date:
        props["Publish Date"] = {"date": {"start": publish_date}}

    resp = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"properties": props},
    )
    time.sleep(0.4)
    return resp.status_code == 200


def build_page_body(idea: dict) -> list:
    """Build Notion page body blocks for a developed content idea."""
    blocks = []

    desc = idea.get("description") or idea.get("notes") or ""
    if desc:
        blocks.append(_para(str(desc)[:2000], italic=True, color="gray"))
        blocks.append(_para())

    # Strategic positioning
    blocks.append(_h2("Strategic Positioning"))
    for field, label in [
        ("audience_segment", "Audience"),
        ("funnel_position", "Funnel"),
        ("offer_alignment", "Offer"),
        ("content_pillar", "Pillar"),
        ("authority_angle", "Authority"),
        ("cta_path", "CTA"),
    ]:
        val = idea.get(field)
        if val:
            blocks.append(_bullet(f"{label}: {str(val)[:500]}", bold=(field == "audience_segment")))
    blocks.append(_para())

    # Title options
    title_options = _parse_json(idea.get("title_options"))
    if title_options:
        blocks.append(_h2("Title Options"))
        for i, t in enumerate(title_options):
            text = t.get("text", str(t)) if isinstance(t, dict) else str(t)
            elements = t.get("elements", []) if isinstance(t, dict) else []
            suffix = f" [{', '.join(elements)}]" if elements else ""
            blocks.append(_bullet(f"{text}{suffix}", bold=(i == 0)))
        blocks.append(_para())

    # Thumbnail concepts
    thumb_concepts = _parse_json(idea.get("thumbnail_concepts"))
    if thumb_concepts:
        blocks.append(_h2("Thumbnail Concepts"))
        for t in thumb_concepts:
            if isinstance(t, dict):
                parts = []
                for key in ("emotion", "text_overlay", "visual", "type"):
                    if t.get(key):
                        parts.append(f"{key.replace('_', ' ').title()}: {t[key]}")
                blocks.append(_bullet(" | ".join(parts) if parts else str(t)))
            else:
                blocks.append(_bullet(str(t)))
        blocks.append(_para())

    # Hook
    if idea.get("hook"):
        blocks.append(_h2("Hook"))
        blocks.append(_para(str(idea["hook"])[:2000]))
        blocks.append(_para())

    # Production checklist
    blocks.append(_divider())
    blocks.append(_h2("Production Checklist"))
    for t in [
        "Content date confirmed",
        "Raw content created",
        "Editing/review assigned",
        "Thumbnail/visual assigned",
        "Review complete",
        "Published",
        "Links and description added",
    ]:
        blocks.append(_todo(t))

    return blocks


def _map_status(status: str) -> str:
    return {
        "stub": "Stub", "developed": "Developed", "scheduled": "Scheduled",
        "filmed": "Filmed", "editing": "Editing", "published": "Published",
    }.get(status, "Stub")


def _parse_json(val):
    if val is None:
        return None
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return None


if __name__ == "__main__":
    if "--create-db" in sys.argv:
        idx = sys.argv.index("--create-db")
        if idx + 1 >= len(sys.argv):
            print("Usage: python3 notion_sync.py --create-db PARENT_PAGE_ID")
            print("\nThe PARENT_PAGE_ID is the Notion page where the database will be created.")
            print("Find it in the page URL: notion.so/Your-Page-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            sys.exit(1)
        parent_id = sys.argv[idx + 1]
        create_notion_database(parent_id)
    elif "--test" in sys.argv:
        headers = _get_headers()
        db_id = _get_db_id()
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=headers,
            json={"page_size": 1},
        )
        if resp.status_code == 200:
            total = resp.json().get("results", [])
            print(f"Notion connection OK! Database has entries.")
        else:
            print(f"Notion connection failed ({resp.status_code}): {resp.text[:300]}")
    else:
        print("Notion sync module loaded.")
        print("  --create-db PAGE_ID  Create the Content Pipeline database")
        print("  --test               Test Notion connection")
