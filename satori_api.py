import re
from urllib import urlencode
import urllib2
import multipart_post_form

try:
    import config
except ImportError:
    with open('config.py', 'w') as config:
        config.write("""SATORI_LOGIN = '***'
SATORI_PASSWORD = '***'
SATORI_URL = 'https://satori.tcs.uj.edu.pl/'
""")
        print "Fill-up config.py file"
        exit(0)


class LoginFailedException(Exception):
    pass


class OperationFailedException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class API:
    def __init__(self, login=config.SATORI_LOGIN, password=config.SATORI_PASSWORD, verbose=False,
                 *args, **kwargs):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
        self.url = kwargs.get('url', config.SATORI_URL)

        response = self.get_data('login', {'login': login, 'password': password})

        self.user = re.search('<li>Logged in as ([^<]*)</li>', response)
        if self.user is None:
            raise LoginFailedException()
        self.user = self.user.group(1)
        if verbose:
            print 'Logged as {}'.format(self.user)

    def close(self):
        """
        Finish work with API
        """
        self.opener.close()
        self.opener = None

    def __del__(self):
        self.close()

    @staticmethod
    def get_errors(data):
        errors = []
        for err in re.finditer('<ul class="errorlist">(.*?)</ul>', data):
            errors.extend(re.findall('<li>(.*?)</li>', err.group()))
        return errors

    def get_data(self, url, data={}, headers={}):
        data = self.opener.open(urllib2.Request(self.url + url, data if isinstance(data, str) else urlencode(data),
                                                headers)).read()
        return data

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
        print 'contest/{}/results'.format(contest_id)
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

    def submit(self, contest_id, problem_id, file_path, modify=False):
        """
        Submit solution for the problem

        :return : True if success else False
        """
        print contest_id, problem_id, file_path
        url = self.url + 'contest/{}/submit'.format(contest_id)
        mp = multipart_post_form.MultiPartForm()
        mp.add_field('problem', str(problem_id))
        file_name = re.search('([^/]|\\\\/)*$', file_path).group()

        with open(file_path) as f:
            data = f.read()

        if modify:
            if re.search('\.java$', file_name):
                # remove package keyword
                data = re.sub("\A(?P<commentary>(^\s*//.*$[\n\r]*)*)(?P<package>^\s*package.*$)",
                              "\\g<commentary>//\\g<package>",
                              data,
                              flags=re.MULTILINE)

        mp.add_file('codefile', file_name, data)
        content = mp.get_content()

        response = self.get_data(url, content, {
            'Content-type': mp.get_content_type(),
            'Content-length': len(content),
        })

        return self.get_errors(response)
