#!/usr/bin/python2
# coding=utf-8
from satori_api import API, LoginFailedException
import argparse
import re
import time


def main(parser):
    args = parser.parse_args()
    try:
        api = API(verbose=True)
    except LoginFailedException:
        print "Login Failed"
        return

    def get_contest(contest):
        if re.match('^@\d+$', contest):
            return api.get_contests()[int(contest[1:])]['id']
        if re.match('^\d+$', contest):
            return int(contest)
        return None

    def get_problem(contest, problem):
        if re.match('^@\d+$', problem):
            return api.get_submittable_problems(contest)[int(problem[1:])]['id']
        if re.match('^\d+$', problem):
            return int(problem)
        return None

    if args.list:
        for idx, entry in enumerate(api.get_contests()):
            print "{:3d} : {} ({})".format(idx, entry['name'], entry['id'])

    elif args.results:
        if not args.contest:
            print "Select contest"
            return

        contest = get_contest(args.contest)
        if contest is None:
            print "Bad contest id"
            return

        data = api.get_results(contest)
        for entry in data['results']:
            print "{}\t[ {} ]   \t({})".format(entry['problem'], entry['status'], entry['date'])

    elif args.available_problems:
        if not args.contest:
            print "Select contest"
            return

        contest = get_contest(args.contest)
        if contest is None:
            print "Bad contest id"
            return

        data = api.get_submittable_problems(contest)
        for idx, entry in enumerate(data):
            print "{:3d} : {} : {}   [{}]".format(idx, entry['code'], entry['name'], entry['id'])

    elif args.submit:
        if not args.contest:
            print "Select contest"
            return
        if not args.problem:
            print "Select problem"
            return
        if not args.file:
            print "Select file"
            return

        contest = get_contest(args.contest)
        problem = get_problem(contest, args.problem)
        file_path = args.file

        api.submit(contest, problem, file_path, modify=args.modify)

    if args.wait:
        try:
            while True:
                if not args.contest:
                    print "Select contest"
                    return

                contest = get_contest(args.contest)
                if contest is None:
                    print "Bad contest id"
                    return

                data = api.get_results(contest)
                for entry in data['results']:
                    print "{}\t[ {} ]   \t({})".format(entry['problem'], entry['status'], entry['date'])

                print "---\n"
                time.sleep(10)
        except KeyboardInterrupt:
            pass

    # TODO : the rest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true', help="list available contests")
    parser.add_argument('-r', '--results', action='store_true', help="show results")
    parser.add_argument('-c', '--contest', metavar='id', help="select contest with given @id / idx")
    parser.add_argument('-a', '--available-problems', action='store_true', help="list available problems")
    parser.add_argument('-f', '--file', help="select file")
    parser.add_argument('-p', '--problem', help="select problem")
    parser.add_argument('-s', '--submit', action='store_true', help="submit solution")
    parser.add_argument('-w', '--wait', action='store_true', help="wait for results")
    parser.add_argument('-o', '--original', dest='modify', action='store_false', help="send original file")
    main(parser)
