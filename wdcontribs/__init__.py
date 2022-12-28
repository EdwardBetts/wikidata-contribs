import json
import re
from typing import Iterable

from . import api


def most_recent_timestamp(filename: str) -> str:
    """Get timestamp from last line of file."""
    for line in open(filename):
        pass

    start: str = json.loads(line)["timestamp"]
    return start


def iter_merge_contribs(filename: str) -> Iterable[api.EntityType]:
    re_merge_from = re.compile(r"/\* wbmergeitems-from:0\|\|(Q\d+) \*/")

    for line in open(filename):
        if "wbmergeitems-from" not in line:
            continue

        cur = json.loads(line)
        qid = cur["title"]

        m = re_merge_from.match(cur["comment"])
        assert m

        entity = api.get_item(qid)
        yield entity
