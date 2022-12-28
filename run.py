#!/usr/bin/python3

"""Filter user contributions for merges and show top occupations."""

import collections
import configparser
import json
import os

import click

import wdcontribs

config = configparser.ConfigParser()

config.read("config")

contribs_filename = config["contribs"]["filename"]


@click.group()
def cli() -> None:
    """Click command line group."""
    pass


@cli.command()
def download_contribs() -> None:
    """Download my contributions and save to a file."""
    if os.path.exists(contribs_filename):
        start = wdcontribs.most_recent_timestamp(contribs_filename)
    else:
        start = config["contribs"]["default_start"]

    username = config["contribs"]["username"]

    out = open(contribs_filename, "a")

    uccontinue = None
    while True:
        reply = wdcontribs.api.get_contribs(username, start, uccontinue)
        contribs = reply["query"]["usercontribs"]
        for i in contribs:
            print(json.dumps(i), file=out)
        if "continue" not in reply:
            break
        uccontinue = reply["continue"]["uccontinue"]


def is_human(entity: wdcontribs.api.EntityType) -> bool:
    """Is this entity a human."""
    return "Q5" in wdcontribs.api.get_statement_qids(entity, "P31")


def get_occupation_totals(filename: str) -> collections.Counter[str]:
    """Read occupation counts from user contributions."""
    job_counts: collections.Counter[str] = collections.Counter()
    occupation_pid = "P106"
    required_pids = set(config["contribs"]["required_pids"].split(","))

    for entity in wdcontribs.iter_merge_contribs(contribs_filename):
        if not is_human(entity) or not entity["claims"].keys() & required_pids:
            continue

        for job in wdcontribs.api.get_statement_qids(entity, occupation_pid):
            job_counts[job] += 1

    return job_counts


@cli.command()
def occupation_totals() -> None:
    """Show top jobs for merge contributions."""
    job_counts: collections.Counter[str] = get_occupation_totals(contribs_filename)

    for job_qid, count in job_counts.most_common(30):
        job_name = wdcontribs.api.item_label(job_qid)
        click.echo(f"{job_name} — {count}")


if __name__ == "__main__":
    cli()
