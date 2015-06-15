import os
import re
import json
import time
import pickle
import collections
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import concurrent.futures

grind = collections.namedtuple('grind', 'date, start, end, time')
class GrouseMountainAccount:

    __last_update = 0

    def __init__(self, uuid=-1, name=None, age=None, dates_and_times=None):
        self.uuid = uuid  # int
        self.name = name  # string
        self.age = age  # string? (ie: 40-50)
        self.dates_and_times = dates_and_times  # list of tuples containing (date, time) zero to n times

    def updated(self):
        self.__last_update = time.time()

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


def does_account_exist(number):
    accounts = load_data()
    root_url = "http://www.grousemountain.com/grind_stats/{}/".format(number)  # key2"
    if number not in accounts.keys():
        try:
            with urllib.request.urlopen(root_url) as page:
                soup = BeautifulSoup(page.read(390))

                titles = soup.findAll('title')
                for title in titles:
                    print("{}: {}".format(number, title.string.strip().split("'s Grouse Grind Stats")[0]))
                    return number, title.string.strip().split("'s Grouse Grind Stats")[0]

        except urllib.error.URLError as e:
            # print("{}: {}".format(number, e.reason))
            return number, e.reason

        except ConnectionResetError as e:
            print(e)
    else:
        # print("SKIPPED: {}: {}".format(number, account_info[number]))
        pass


def load_data(_storage_path=os.path.expanduser("~/Documents/grousemountain.pickle")):
    print("[LOADING] {}".format(_storage_path))
    accounts = list()  # will load a list of GrouseMountainAccounts
    if os.path.isfile(_storage_path):
        accounts = pickle.load(open(_storage_path, 'rb'))

    return accounts


def save_data(data, _storage_path=os.path.expanduser("~/Documents/grousemountain.pickle")):
    print("[SAVING] {}".format(_storage_path))
    pickle.dump(data, open(_storage_path, 'wb'))
    # print("[SAVED] Stored {} {} entries.".format(len(data), type(data[0])))


def collect_account_numbers(pickle_path):
    accounts = load_data()
    pool = 120
    with concurrent.futures.ProcessPoolExecutor(pool) as executor:
        # accounts seem to end in:
        # -15000
        # -05000
        # -03000
        # -06000
        options = [15000,
                   5000,
                   3000,
                   6000]
        for option in options:
            print("[info] Iterating over accounts ending in {}". format(option))
            futures = [executor.submit(does_account_exist, number) for number in range(10000000000 + option,
                                                                                       64000000000 + option,
                                                                                       1000000)]
            concurrent.futures.wait(futures)
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            for r in results:
                if r is not None:
                    accounts[r[0]] = r[1]
        # will incrementally save after each iteration through options
        save_data(accounts)


if __name__ == "__main__":
    # collect_account_numbers(_file)
    # data = get_grind_times(12345)

    new_storage_path = os.path.expanduser("~/Documents/grousemountaindata.pickle")

    accounts = load_data(_storage_path=new_storage_path)

    new_accounts = list()
    for num, name in accounts.items():

        account = GrouseMountainAccount(uuid=num)
        account.name = name
        if "Not Found" not in name and "Service Unavailable" not in name:
            print("[info] Getting Grind times for: {}".format(account.name))
            account.get_grind_times()
        new_accounts.append(account)

    save_data(new_accounts, _storage_path=new_storage_path)
    print("Done!")
