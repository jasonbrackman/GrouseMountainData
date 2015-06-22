import os
import pickle
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import concurrent.futures
import account

def load_data(_storage_path=os.path.expanduser("~/Documents/grousemountaindata.pickle")):
    print("[LOADING] {}".format(_storage_path))
    accounts = list()  # will load a list of GrouseMountainAccounts
    if os.path.isfile(_storage_path):
        accounts = pickle.load(open(_storage_path, 'rb'))
    print("[LOADING] Complete!")
    return accounts

def save_data(data, _storage_path=os.path.expanduser("~/Documents/grousemountaindata.pickle")):
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
        print("{}: {}".format(number, e.reason))
        return number, e.reason

    except ConnectionResetError as e:
        print(e)

def create_account(uuid, username):
    new_account = account.GrouseMountain(uuid=uuid)
    new_account.name = username
    if "Not Found" not in username and "Service Unavailable" not in username:
        print("[info] Getting Grind times for: {}".format(new_account.name))
        new_account.get_grind_times()

    return new_account

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
                   6000,
                   5000,
                   4000,
                   3000,
                   2000]
        existing_account_numbers = [_account.uuid for _account in _accounts]
        numbers = list()
        for option in options:
            print("Collecting: {}".format(option))
            for number in range(min+option, max+option, step):
                if number not in existing_account_numbers:
                    print("[info] Found an uncollected number: {}".format(number))
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

def convert_to_new_class(old_accounts):
        new_accounts = list()
        for old_account in old_accounts:
            print("Updating: {}".format(old_account.name))
            new_account = account.GrouseMountain(uuid=old_account.uuid,
                                                 name=old_account.name,
                                                 #age =old_account.age,
                                                 #sex =old_account.sex,
                                                 dates_and_times=old_account.dates_and_times)
            new_accounts.append(new_account)

        new_storage_path = os.path.expanduser("~/Documents/grinders.pickle")
        save_data(new_accounts, _storage_path=new_storage_path)

def get_grinder_info():
    new_storage_path = os.path.expanduser("~/Documents/grinders.pickle")
    accounts = load_data(_storage_path=new_storage_path)
    while True:
        result = input("Name please: ")
        if result == 'Q':
            break
        else:
            for account in accounts:
                if result.lower() in account.name.lower():
                    if account.dates_and_times is not None:
                        print("{}: {}".format(account.name, account.dates_and_times[-1]))
                    else:
                        print("{}: {}".format(account.name, "No Grind Times Found."))

if __name__ == "__main__":
    # get_grinder_info()
    # collect_account_numbers(10000000000, 65000000000, 1000000, _storage_path=new_storage_path)
    # convert_to_new_class(accounts)
    pass
