#!/usr/bin/python2
# coding=utf-8
from satori_api import API, LoginFailedException
import argparse
import re


def main(args):
    try:
        api = API(verbose=True)
    except LoginFailedException:
        print "Login Failed"
        return

    if args.list:
        for idx, entry in enumerate(api.get_contests()):
            print "{:3d} : {} ({})".format(idx, entry['name'], entry['id'])
    elif args.results:
        contest = None
        if re.match('^@\d+$', args.results):
            contest = int(args.results[1:])
        elif re.match('^\d+$', args.results):
            contest = api.get_contests()[int(args.results)]['id']
        if contest is None:
            print "Bad contest id"
            return

        for entry in api.get_results(contest):
            print "{}\t[ {} ]   \t({})".format(entry['problem'], entry['status'], entry['date'])

    # TODO : the rest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', action='store_true', help="list available contests")
    parser.add_argument('--results', '-r', metavar='id', help="show last results of contest with given @id / idx")
    main(parser.parse_args())
