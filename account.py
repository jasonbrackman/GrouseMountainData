import re
import json
import time
import collections
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

# Class that stores data points surrounding a grouse mountain account along with some convenience functions to collect
# data.

# TODO: eliminate class altogether and move to sqlite3 or json storage
# Namedtuple is outside the class because of a limitation of Pickle to pickle nested classes
grind = collections.namedtuple('grind', 'date, start, end, time')
class GrouseMountain:

    __last_update = 0

    def __init__(self, uuid=-1, name=None, age=None, sex=None, dates_and_times=None):
        self.uuid = uuid  # int
        self.name = name  # string
        self.age = age  # string? (ie: 40-50)
        self.sex = sex
        self.dates_and_times = dates_and_times  # list of tuples containing (date, time) zero to n times

    def updated(self):
        self.__last_update = time.time()

    def get_sex(self):
        root_url = "http://www.grousemountain.com/grind_stats/{}/".format(self.uuid)

        try:
            with urllib.request.urlopen(root_url) as page:
                soup = BeautifulSoup(page.read())

                spans = soup.findAll('span', {'class': 'small'})
                for span in spans:
                    print("FOUND: {}: {}".format(self.name, span.string.split()[:-1]))
                    self.sex = span.split()[-1]

        except urllib.error.URLError as e:
                print("[ERROR] Could not determine sex: {}".format(e.reason))

    def get_grind_times(self, page=1, force=False):
        if self.__last_update == 0 or int(self.__last_update/3600) > 2 or force:
            pattern = re.compile('.*page=(\d.*)')
            url = "http://www.grousemountain.com/grind_stats/{0}.json?page={1}".format(self.uuid, page)

            try:
                with urllib.request.urlopen(url) as request:
                    data = request.read().decode(request.info().get_param('charset') or 'utf-8')

                    jdata = json.loads(data)
                    # print(jdata['html'])
                    soup = BeautifulSoup(jdata['html'])

                    # <span class='last'>
                    # <a href="/grind_stats/22597005000.json?page=2" data-remote="true">Last &raquo;</a>
                    # </span>

                    rows = soup.find_all('tr')
                    for row in rows:
                        data = row.find_all(text=re.compile('\d.*'))
                        data = [d.strip() for d in data]
                        if len(data) == 4:
                            if self.dates_and_times is None:
                                self.dates_and_times = [grind._make(data)]
                            else:
                                self.dates_and_times.append(grind._make(data))

                    pages = page
                    element = soup.find('a', text=re.compile('Last'))
                    if element is not None:
                        results = re.match(pattern, element['href'])
                        if results is not None:
                            # print("Result: Pages={}".format(results.groups()[0]))
                            pages = int(results.groups()[0])

                    if page < pages:
                        self.get_grind_times(page=page + 1)

            except urllib.error.URLError as e:
                print("[ERROR] {}".format(e.reason))

            self.updated()
