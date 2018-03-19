#!/usr/bin/python2
# coding=utf-8
from satori_api import API, LoginFailedException
import argparse
import re
import time
import sys
import os

def get_contest(api, contest):
    if re.match('^@\d+$', contest):
        return api.get_contests()[int(contest[1:])]['id']
    if re.match('^\d+$', contest):
        return int(contest)
    return None


def get_problem(api, contest, problem):
    if re.match('^@\d+$', problem):
        return api.get_submittable_problems(contest)[int(problem[1:])]['id']
    if re.match('^\d+$', problem):
        return int(problem)
    return None


def get_property(name, data):
    for line in data.splitlines():
        res = re.match('^\\s*(//|#|;)?\\s*@{}\\s+(?P<result>.*)\\s*$'.format(name), line)
        if res:
            return res.group('result')
    return None


def show_details(api, contest, solution, wait, timeout, wait_finished_handler):
    if not solution:
        print "Select solution"
        return

    contest = get_contest(api, contest)
    if contest is None:
        print "Bad contest id"
        return

    try:
        waiting = True
        while waiting:

            data = api.get_details(contest, solution)
            print "{} : [ {} ] ({}, {}) [{}]".format(data['code'], data['status'],
                                                     data['user'], data['date'], data['id'])

            for entry in data['report']:
                print "{}\t[ {} ]\t({})".format(entry['test'], entry['status'], entry['time'])

            if data['status'] != 'QUE':
                if wait and wait_finished_handler is not None:
                    wait_finished_handler(data)

                waiting = False
            else:
                waiting = wait

            if waiting:
                print "---"
                time.sleep(timeout)
    except KeyboardInterrupt:
        pass


def main(parser):
    args = parser.parse_args()

    sys.path.insert(0, args.config)

    try:
        import config

        if not hasattr(config, 'wait_finished_handler'):
            config.wait_finished_handler = None

    except ImportError:
        try:
            os.mkdir(args.config)
        except OSError:
            pass

        with open(os.path.join(args.config, 'config.py'), 'w') as config:
            config.write("""SATORI_LOGIN = '***'
SATORI_PASSWORD = '***'
SATORI_URL = 'https://satori.tcs.uj.edu.pl/'

def wait_finished_handler(data):
    pass
""")
            print "Fill-up {} file".format(os.path.join(args.config, 'config.py'))
            exit(0)

    try:
        api = API(login=config.SATORI_LOGIN, password=config.SATORI_PASSWORD, satori_url=config.SATORI_URL, verbose=True)
    except LoginFailedException:
        print "Login Failed"
        return

    if args.file:  # get data from file
        with open(args.file) as fd:
            data = fd.read()
            args.contest = args.contest or get_property("contest", data)
            args.problem = args.problem or get_property("problem", data)

    if args.list:
        for idx, entry in enumerate(api.get_contests()):
            print "{:3d} : {} ({})".format(idx, entry['name'], entry['id'])

    elif args.results:
        if not args.contest:
            print "Select contest"
            return

        contest = get_contest(api, args.contest)
        if contest is None:
            print "Bad contest id"
            return

        data = api.get_results(contest)
        for entry in data['results']:
            print "{}\t[ {} ]   \t({}) [{}]".format(entry['problem'], entry['status'], entry['date'], entry['id'])

    elif args.available_problems:
        if not args.contest:
            print "Select contest"
            return

        contest = get_contest(api, args.contest)
        if contest is None:
            print "Bad contest id"
            return

        data = api.get_submittable_problems(contest)
        for idx, entry in enumerate(data):
            print "{:3d} : {} : {}   [{}]".format(idx, entry['code'], entry['name'], entry['id'])

    elif args.details:
        show_details(api, args.contest, args.solution, args.wait, args.timeout, config.wait_finished_handler)

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

        contest = get_contest(api, args.contest)
        problem = get_problem(api, contest, args.problem)
        file_path = args.file

        response = api.submit(contest, problem, file_path, modify=args.modify)
        args.solution = response['solution']
        args.contest = response['contest']
        args.problem = response['problem']

        if args.wait:
            show_details(api, args.contest, args.solution, args.wait, args.timeout, config.wait_finished_handler)

    elif args.wait:
        try:
            while True:
                if not args.contest:
                    print "Select contest"
                    return

                contest = get_contest(api, args.contest)
                if contest is None:
                    print "Bad contest id"
                    return

                data = api.get_results(contest)
                for entry in data['results']:
                    print "{}\t[ {} ]   \t({})".format(entry['problem'], entry['status'], entry['date'])

                print "---\n"
                time.sleep(args.timeout)
        except KeyboardInterrupt:
            pass

            # TODO : the rest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true', help="list available contests")
    parser.add_argument('-r', '--results', action='store_true', help="show results")
    parser.add_argument('-d', '--details', action='store_true', help="show solution report")
    parser.add_argument('-c', '--contest', metavar='id', help="select contest with given @id / idx")
    parser.add_argument('-n', '--solution', help="select solution")
    parser.add_argument('-a', '--available-problems', action='store_true', help="list available problems")
    parser.add_argument('-f', '--file', help="select file")
    parser.add_argument('-p', '--problem', help="select problem")
    parser.add_argument('-s', '--submit', action='store_true', help="submit solution")
    parser.add_argument('-w', '--wait', action='store_true', help="wait for results")
    parser.add_argument('-o', '--original', dest='modify', action='store_false', help="send original file")
    parser.add_argument('-t', '--timeout', type=int, help="wait timeout", default=10)
    parser.add_argument('--config', help="configuration directory", default='./')
    main(parser)
