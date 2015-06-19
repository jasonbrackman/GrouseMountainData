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

def load_data(_storage_path=os.path.expanduser("~/Documents/grousemountain.pickle")):
    print("[LOADING] {}".format(_storage_path))
    accounts = list()  # will load a list of GrouseMountainAccounts
    if os.path.isfile(_storage_path):
        accounts = pickle.load(open(_storage_path, 'rb'))
    print("[LOADING] Complete!")
    return accounts

def save_data(data, _storage_path=os.path.expanduser("~/Documents/grousemountain.pickle")):
    print("[SAVING] {}".format(_storage_path))
    pickle.dump(data, open(_storage_path, 'wb'))
    print("[SAVING] Complete!")

def does_account_exist(number):
    root_url = "http://www.grousemountain.com/grind_stats/{}/".format(number)  # key2"

    try:
        with urllib.request.urlopen(root_url) as page:
            soup = BeautifulSoup(page.read(390))

            titles = soup.findAll('title')
            for title in titles:
                print("FOUND: {}: {}".format(number, title.string.strip().split("'s Grouse Grind Stats")[0]))
                return number, title.string.strip().split("'s Grouse Grind Stats")[0]

    except urllib.error.URLError as e:
        # print("{}: {}".format(number, e.reason))
        return number, e.reason

    except ConnectionResetError as e:
        print(e)

def collect_account_numbers(min, max, step, _storage_path=None):
    accounts = load_data(_storage_path=_storage_path)

    def get_unknown_uuids(min, max, step, _accounts):
        # accounts seem to end in:
        # -15000
        # -05000
        # -03000
        # -02000
        # -06000
        options = [15000,
                   5000,
                   4000,
                   3000,
                   2000,
                   6000]
        existing_account_numbers = [_account.uuid for _account in _accounts]
        numbers = list()
        for option in options:
            for number in range(min+option, max+option, step):
                if number not in existing_account_numbers:
                    numbers.append(number)
        print(len(numbers))
        return numbers

    dirty = False
    pool = 25
    numbers = get_unknown_uuids(min, max, step, accounts)
    with concurrent.futures.ProcessPoolExecutor(pool) as executor:
        futures = [executor.submit(does_account_exist, number) for number in numbers]
        concurrent.futures.wait(futures)
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        for result in results:
            if result is not None:
                new_account = create_account(result[0], result[1])
                accounts.append(new_account)
                dirty = True

    if dirty:
        save_data(accounts, _storage_path=_storage_path)


def create_account(uuid, username):
    new_account = GrouseMountainAccount(uuid=uuid)
    new_account.name = username
    if "Not Found" not in username and "Service Unavailable" not in username:
        print("[info] Getting Grind times for: {}".format(new_account.name))
        new_account.get_grind_times()

    return new_account

if __name__ == "__main__":
    new_storage_path = os.path.expanduser("~/Documents/grousemountaindata.pickle")
    collect_account_numbers(64000000000, 65550000000, 1000000, _storage_path=new_storage_path)

    accounts = load_data(_storage_path=new_storage_path)
    while True:
        result = input("Name please: ")
        if result == 'Q':
            break
        else:
            for account in accounts:
                if result.lower() in account.name.lower():
                    if account.dates_and_times is not None:
                        print("{}: {}".format(account.name, account.dates_and_times[0]))
                    else:
                        print("{}: {}".format(account.name, "No Grind Times Found."))

    print("Done!")
