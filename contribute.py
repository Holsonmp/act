#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime, timedelta
from random import randint
from subprocess import run, CalledProcessError


def sh(cmd):
    run(cmd, check=True)


def is_git_repo(path):
    return os.path.isdir(os.path.join(path, '.git'))


def main(argv=sys.argv[1:]):
    args = arguments(argv)
    curr_date = datetime.now()

    # --- Détermination du dossier ---
    if args.repository:
        repo_name = args.repository.rstrip('/').split('/')[-1].replace('.git', '')
    else:
        repo_name = os.getcwd()

    # --- Cas dépôt existant ---
    if is_git_repo(os.getcwd()):
        repo_path = os.getcwd()

    elif args.repository:
        if os.path.isdir(repo_name):
            os.chdir(repo_name)
            if not is_git_repo(os.getcwd()):
                sys.exit("Dossier existant mais pas un dépôt git.")
        else:
            sh(['git', 'clone', args.repository])
            os.chdir(repo_name)

    else:
        sys.exit("Aucun dépôt git détecté et aucun remote fourni.")

    # --- Config utilisateur ---
    if args.user_name:
        sh(['git', 'config', 'user.name', args.user_name])
    if args.user_email:
        sh(['git', 'config', 'user.email', args.user_email])

    # --- Sync avec remote si présent ---
    try:
        sh(['git', 'pull', '--rebase'])
    except CalledProcessError:
        pass  # dépôt local seulement

    # --- Génération des commits ---
    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days=args.days_before)

    for day in (start_date + timedelta(n) for n in range(args.days_before + args.days_after)):
        if args.no_weekends and day.weekday() >= 5:
            continue
        if randint(0, 100) > args.frequency:
            continue

        for _ in range(contributions_per_day(args)):
            contribute(day + timedelta(minutes=randint(1, 120)))

    # --- Push ---
    try:
        sh(['git', 'push'])
    except CalledProcessError:
        pass

    print("✔ Contributions ajoutées sans recréer le dépôt.")


def contribute(date):
    with open('README.md', 'a', encoding='utf-8') as f:
        f.write(message(date) + '\n')

    sh(['git', 'add', 'README.md'])
    sh([
        'git', 'commit',
        '--allow-empty',
        '--date', date.strftime('%Y-%m-%d %H:%M:%S'),
        '-m', message(date)
    ])


def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    return randint(1, min(max(args.max_commits, 1), 30))


def arguments(argsval):
    p = argparse.ArgumentParser()

    p.add_argument('-nw', '--no_weekends', action='store_true')
    p.add_argument('-mc', '--max_commits', type=int, default=10)
    p.add_argument('-fr', '--frequency', type=int, default=80)
    p.add_argument('-r', '--repository', type=str)
    p.add_argument('-un', '--user_name', type=str)
    p.add_argument('-ue', '--user_email', type=str)
    p.add_argument('-db', '--days_before', type=int, default=365)
    p.add_argument('-da', '--days_after', type=int, default=0)

    return p.parse_args(argsval)


if __name__ == "__main__":
    main()
