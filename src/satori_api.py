import re
from sys import version_info
import preprocessor

if version_info.major == 2:
    from urllib import urlencode
    from urllib2 import build_opener, HTTPCookieProcessor, Request
else:
    from urllib.parse import urlencode
    from urllib.request import build_opener, HTTPCookieProcessor, Request

import multipart_post_form


class LoginFailedException(Exception):
    pass


class OperationFailedException(Exception):
    def __init__(self, message=None, data=None):
        self.message = message
        self.data = data

    def __str__(self):
        return self.message


class API:
    def __init__(self, login="", password="", satori_url="", verbose=False,
                 *args, **kwargs):
        self.opener = build_opener(HTTPCookieProcessor)
        self.url = kwargs.get('url', satori_url)

        response = self.get_data('login', {'login': login, 'password': password})

        self.user = re.search('<li>Logged in as ([^<]*)</li>', response)
        if self.user is None:
            raise LoginFailedException()
        self.user = self.user.group(1)
        if verbose:
            print('Logged as {}'.format(self.user))

    def close(self):
        """
        Finish work with API
        """
        self.opener.close()
        self.opener = None

    def __del__(self):
        self.close()

    @staticmethod
    def raise_errors(data):
        errors = []
        for err in re.finditer('<ul class="errorlist">(.*?)</ul>', data):
            errors.extend(re.findall('<li>(.*?)</li>', err.group()))
        if errors:
            raise OperationFailedException(errors, data)

    def get_data(self, url, data={}, headers={}):
        data = self.opener.open(Request(self.url + url, data.encode() if isinstance(data, str) else urlencode(data).encode(),
                                                headers)).read()
        return data if version_info.major == 2 else data.decode()

    def get_contests(self):
        """
        Get available contests
        """
        data = self.get_data('contest/select')
        links = re.finditer('<a class="stdlink" href="/contest/(\d*)/">([^<]*)</a>', data)
        return [{
            'id': entry.group(1),
            'name': entry.group(2),
        } for entry in links]

    def get_results(self, contest_id):
        """
        Get results of recently sent solutions

        :rtype: {'id': , 'name' , 'results': [{'id': , 'problem': , 'date': , 'status': }, ...]}
        """
        print('contest/{}/results'.format(contest_id))
        data = self.get_data('contest/{}/results'.format(contest_id))
        results = re.finditer('<tr><td><a class="stdlink" href="/contest/\d*/results/(\d*)">\d*</a></td><td>([^<]*)\
</td><td>([^<]*)</td><td class="status"><div class="submitstatus"><div class="[^"]*">([^<]*)</div></div></td></tr>',
                              data)

        return {
            'id': contest_id,
            # 'name': # TODO
            'results': [{
                'id': entry.group(1),
                'problem': entry.group(2),
                'date': entry.group(3),
                'status': entry.group(4),
            } for entry in results],
        }

    def get_submittable_problems(self, contest_id):
        """
        Get list of submittable problems of given contest

        :rtype : [{'id': , 'code': , 'name': }, ...]
        """
        data = self.get_data('contest/{}/submit'.format(contest_id))
        problems = re.finditer('<option value="(\d*)">([^:<]*): ([^<]*)</option>', data)

        return [{
            'id': entry.group(1),
            'code': entry.group(2),
            'name': entry.group(3),
        } for entry in problems]

    def get_details(self, contest_id, solution_id):
        """
        Get report of the solution

        :rtype : {'id': , 'user': , 'code' : , 'date' : , 'status': , 'report': [{'test': , 'status': , 'time': }, ...]}
        """
        data = self.get_data('contest/{}/results/{}'.format(contest_id, solution_id))

        self.raise_errors(data)

        result = {}

        res = re.search('<table class="results">.*?</tr>.*?<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?\
<td>(.*?)</td>.*?<td.*?>(.*?)</td>.*?</tr>.*?</table>', data, flags=re.DOTALL)

        result['id'] = res.group(1)
        result['user'] = res.group(2)
        result['code'] = res.group(3)
        result['date'] = res.group(4)
        result['status'] = res.group(5)

        result['report'] = []
        report = re.search('<h4>Checking report</h4>.*?(<tr><td>.*?)</tbody>', data, flags=re.DOTALL)
        if report:
            report = report.group(1)
            result['report'] = [{
                'test': entry.group(1),
                'status': entry.group(2),
                'time': re.sub('&nbsp;', '---', entry.group(3)),
            } for entry in re.finditer('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?</tr>',
                                       report, flags=re.DOTALL)]

        return result

    def submit(self, contest_id, problem_id, file_path, modify=False):
        """
        Submit solution for the problem

        :return : True if success else False
        """
        print("{} {} {}".format(contest_id, problem_id, file_path))
        url = self.url + 'contest/{}/submit'.format(contest_id)
        mp = multipart_post_form.MultiPartForm()
        mp.add_field('problem', str(problem_id))
        file_name = re.search('([^/]|\\\\/)*$', file_path).group()

        with open(file_path) as f:
            data = f.read()

        if modify:
            data = preprocessor.process(file_name, data)

        mp.add_file('codefile', file_name, data)
        content = mp.get_content()

        response = self.get_data(url, content, {
            'Content-type': mp.get_content_type(),
            'Content-length': len(content),
        })

        self.raise_errors(response)

        result = {}

        res = re.search('<tr><td><a class="stdlink" href="/contest/(\d*)/results/(\d*)">(\d*)</a>', response)

        if not res:
            raise OperationFailedException(['undefined post-submit error'], response)

        result['contest'] = res.group(1)
        result['problem'] = res.group(2)
        result['solution'] = res.group(3)

        return result
