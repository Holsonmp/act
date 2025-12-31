#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime, timedelta
from random import randint
from subprocess import run as sp_run, DEVNULL


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()

    directory = resolve_directory(args.repository)
    os.makedirs(directory, exist_ok=True)
    os.chdir(directory)

    init_git_if_needed()
    configure_git_user(args)

    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days=args.days_before)
    total_days = args.days_before + args.days_after

    for day in (start_date + timedelta(n) for n in range(total_days)):
        if should_commit(day, args):
            for commit_time in commits_for_day(day, args):
                contribute(commit_time)

    setup_remote_and_push(args.repository)
    print("\n✔ Contributions ajoutées avec succès")


# -------------------------
# Git helpers
# -------------------------

def init_git_if_needed():
    if not os.path.isdir(".git"):
        sp_run(["git", "init", "-b", "main"], check=True)


def configure_git_user(args):
    if args.user_name:
        sp_run(["git", "config", "user.name", args.user_name])
    if args.user_email:
        sp_run(["git", "config", "user.email", args.user_email])


def setup_remote_and_push(repository):
    if not repository:
        return

    remotes = sp_run(
        ["git", "remote"],
        capture_output=True,
        text=True
    ).stdout.splitlines()

    if "origin" not in remotes:
        sp_run(["git", "remote", "add", "origin", repository], check=True)

    sp_run(["git", "branch", "-M", "main"], check=True)
    sp_run(["git", "push", "-u", "origin", "main"], check=True)


# -------------------------
# Commit logic
# -------------------------

def contribute(date):
    path = os.path.join(os.getcwd(), "README.md")

    with open(path, "a", encoding="utf-8") as f:
        f.write(message(date) + "\n")

    sp_run(["git", "add", "README.md"], check=True)
    sp_run([
        "git", "commit",
        "--allow-empty",
        "-m", message(date),
        "--date", date.strftime("%Y-%m-%d %H:%M:%S")
    ], stdout=DEVNULL)


def should_commit(day, args):
    if args.no_weekends and day.weekday() >= 5:
        return False
    return randint(0, 100) < args.frequency


def commits_for_day(day, args):
    return (
        day + timedelta(minutes=m)
        for m in range(randint(1, min(args.max_commits, 20)))
    )


def message(date):
    return date.strftime("Contribution: %Y-%m-%d %H:%M")


# -------------------------
# Utils
# -------------------------

def resolve_directory(repository):
    if repository:
        name = repository.rstrip("/").split("/")[-1]
        return name.replace(".git", "")
    return os.getcwd()


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument("-nw", "--no_weekends", action="store_true")
    parser.add_argument("-mc", "--max_commits", type=int, default=10)
    parser.add_argument("-fr", "--frequency", type=int, default=80)
    parser.add_argument("-r", "--repository", type=str)
    parser.add_argument("-un", "--user_name", type=str)
    parser.add_argument("-ue", "--user_email", type=str)
    parser.add_argument("-db", "--days_before", type=int, default=365)
    parser.add_argument("-da", "--days_after", type=int, default=0)

    args = parser.parse_args(argsval)

    if args.days_before < 0 or args.days_after < 0:
        sys.exit("days_before et days_after doivent être ≥ 0")

    return args


if __name__ == "__main__":
    main()
