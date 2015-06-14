import os
import pickle
import json
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import concurrent.futures

def check_if_account_exists(number):
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

class GrouseMountainAccounts:
    _pickle_path =

    def __init__(self, uuid, name, times):
        uuid = # int
        name =
        times =


def load_accounts(self):
    accounts = list() # will load a list of GrouseMountainAccounts
    if os.path.isfile(self._pickle_path):
        accounts = pickle.load(open(self._pickle_path, 'rb'))
    return accounts

def save_accounts(self):

def collect_account_numbers(pickle_path):


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
            print(option)
            futures = [executor.submit(check_if_account_exists, number) for number in range(10000000000 + option,
                                                                                            64000000000 + option,
                                                                                            1000000)]
            concurrent.futures.wait(futures)
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            for r in results:
                if r is not None:
                    accounts[r[0]] = r[1]

    pickle.dump(accounts, open(pickle_path, 'wb'))
    print(len(accounts))

def get_grind_times(account):
    url = "http://www.grousemountain.com/grind_stats/{}.json".format(account)
    print(url)
    try:
        with urllib.request.urlopen(url) as data:
            print(data)
    except urllib.error.URLError as e:
            print("[ERROR] {}".format(e.reason))


if __name__ == "__main__":
    accounts = dict()
    _file = os.path.expanduser("~/Documents/grousemountain.pickle")

    #collect_account_numbers(_file)

    data = get_grind_times(12345)
