"""Access Wikidata via the API."""

import json
import os
from typing import Any

import requests

api_url = "https://www.wikidata.org/w/api.php"

EntityType = dict[str, Any]


def retrieve_item(qid: str) -> EntityType:
    """Retrieve Wikidata item in JSON format."""
    params: dict[str, str | int] = {
        "format": "json",
        "formatversion": 2,
        "action": "wbgetentities",
        "ids": qid,
    }

    json_data = requests.get(api_url, params=params).json()
    entity: EntityType = json_data["entities"][qid]

    return entity


def get_item(qid: str, refresh: bool = False) -> EntityType:
    """Get item, use cache if available."""
    filename = f"item/{qid}.json"

    if not refresh and os.path.exists(filename):
        entity: EntityType = json.load(open(filename))
        return entity

    entity = retrieve_item(qid)
    with open(filename, "w") as out:
        json.dump(entity, out, indent=2)

    return entity


def get_contribs(
    username: str, ucstart: str, uccontinue: str | None = None
) -> dict[str, Any]:
    """Download contributions for given user."""
    params: dict[str, str | int] = {
        "format": "json",
        "formatversion": 2,
        "action": "query",
        "list": "usercontribs",
        "ucuser": username,
        "uclimit": "max",
        "ucstart": ucstart,
        "ucdir": "newer",
        "ucprop": "title|timestamp|comment",
    }

    if uccontinue is not None:
        params["uccontinue"] = uccontinue

    r = requests.get(api_url, params=params)
    json_data: dict[str, Any] = r.json()
    return json_data


def item_label(qid: str, language: str = "en") -> str | None:
    """Label for item, download item if not already cached."""
    entity = get_item(qid)
    return entity["labels"]["en"]["value"] if "en" in entity["labels"] else None


def get_statement_qids(entity: EntityType, pid: str) -> list[str]:
    """Get linked statements."""
    return [
        v["mainsnak"]["datavalue"]["value"]["id"] for v in entity["claims"].get(pid, [])
    ]
