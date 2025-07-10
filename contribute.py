#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()

    repo_path = os.getcwd()
    is_git_repo = os.path.isdir(os.path.join(repo_path, '.git'))

    if not is_git_repo:
        run(['git', 'init', '-b', 'main'])

    if args.user_name:
        run(['git', 'config', 'user.name', args.user_name])

    if args.user_email:
        run(['git', 'config', 'user.email', args.user_email])

    if args.days_before < 0 or args.days_after < 0:
        sys.exit('days_before and days_after must be >= 0')

    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days=args.days_before)

    for day in (start_date + timedelta(n) for n in range(args.days_before + args.days_after)):
        if (not args.no_weekends or day.weekday() < 5) and randint(0, 100) < args.frequency:
            for commit_time in (
                day + timedelta(minutes=m)
                for m in range(contributions_per_day(args))
            ):
                contribute(commit_time)

    if args.repository:
        run(['git', 'remote', 'remove', 'origin'])
        run(['git', 'remote', 'add', 'origin', args.repository])
        run(['git', 'push', '-u', 'origin', 'main'])

    print('Repository generation completed successfully.')


def contribute(date):
    readme = os.path.join(os.getcwd(), 'README.md')
    if not os.path.exists(readme):
        open(readme, 'w').close()

    with open(readme, 'a') as file:
        file.write(message(date) + '\n')

    run(['git', 'add', 'README.md'])
    run([
        'git', 'commit',
        '--allow-empty',
        '-m', message(date),
        '--date', date.strftime('%Y-%m-%d %H:%M:%S')
    ])


def run(commands):
    Popen(commands).wait()


def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    return randint(1, min(max(args.max_commits, 1), 20))


def arguments(argsval):
    parser = argparse.ArgumentParser()

    parser.add_argument('-nw', '--no_weekends', action='store_true')
    parser.add_argument('-mc', '--max_commits', type=int, default=10)
    parser.add_argument('-fr', '--frequency', type=int, default=80)
    parser.add_argument('-r', '--repository', type=str)
    parser.add_argument('-un', '--user_name', type=str)
    parser.add_argument('-ue', '--user_email', type=str)
    parser.add_argument('-db', '--days_before', type=int, default=365)
    parser.add_argument('-da', '--days_after', type=int, default=0)

    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
