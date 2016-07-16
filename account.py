import os
import re
import json
import datetime
import urllib.request
import urllib.error
import concurrent.futures
from bs4 import BeautifulSoup


def load_json_data(_storage_path=os.path.expanduser("~/Documents/grousemountaindata.json")):
    print("[LOADING] {}".format(_storage_path))

    # default accounts dict() to return if nothing has yet been saved to a file.
    accounts = dict()
    if os.path.isfile(_storage_path):
        with open(_storage_path, 'r', ) as handle:
            accounts = json.load(handle)

    print("[LOADING] Complete!")

    return accounts


def dump_json_data(data, _storage_path=os.path.expanduser("~/Documents/grousemountaindata.json")):
    print("[SAVING] {}".format(_storage_path))
    with open(_storage_path, 'w') as handle:
        json.dump(data, handle)
    print("[SAVING] Complete!")


def add_account(accounts, uuid=-1, name=None, age=None, sex=None, grinds=None, last_update=None):
    accounts[uuid] = {"name": name, "age": age, "sex": sex, "grinds": grinds, 'last_update': last_update}
    return accounts


def collect_grind_times(grind_times, uuid, _page=1):
    """
    grind_times is a list that contains dicts of date, start, end, time
    uuid is the user's unique identifier
    the page is used if there are several pages of json data regarding past grind times.
    """
    titles = ('date', 'start', 'end', 'time')
    pattern = re.compile('.*page=(\d.*)&tab.*')

    url_03 = "http://www.grousemountain.com/grind_stats/{0}?page={1}&tab=log".format(uuid, _page)

    try:
        with urllib.request.urlopen(url_03) as request:
            soup = BeautifulSoup(request.read(), "html.parser")

            data = [table.findAll('tr') for table in soup.findAll('table', {'class': 'table grind_log thin'})]
            for grinds in data:
                for grind in grinds:
                    times = [item.string.strip() for item in grind.findAll('td')]
                    times = dict(zip(titles, times))
                    if times and times not in grind_times:
                        grind_times.append(times)

            pages = _page
            element = soup.find('a', text=re.compile('Last'))
            if element is not None:
                results = re.match(pattern, element['href'])
                if results is not None:
                    # print("Result: Pages={}".format(results.groups()[0]))
                    pages = int(results.groups()[0])

            if _page < pages:
                collect_grind_times(grind_times, uuid, _page=_page + 1)

    except urllib.error.URLError as e:
        print("[ERROR] {}".format(e.reason))

    return grind_times


def collect_grind_data(number):
    root_url = "http://www.grousemountain.com/grind_stats/{}/".format(number)

    try:
        with urllib.request.urlopen(root_url) as page:
            soup = BeautifulSoup(page.read(), "html.parser")

            # full name associated with the UUID
            username = [div.find('h2') for div in soup.findAll('div', {'class': 'title red'})]
            name = username[0].string.strip()

            # is the user male or female?
            sex = None
            for sex_type in soup.findAll('small'):
                test = sex_type.string.strip()
                if "Men" in test:
                    sex = "Male"
                    break
                elif "Women" in test:
                    sex = "Female"
                    break

            # get approximate age of the user
            age = None
            for age_range in soup.findAll('small'):
                test = age_range.string.strip()
                if "Age" in test:
                    age = test.split("Age")[1].strip(") ")

            grinds = []
            grinds = collect_grind_times(grinds, number)
            print("[{}]: Found {}'s age:({}), sex:({}), and a number of grinds:({})".format(number,
                                                                                            name,
                                                                                            age,
                                                                                            sex,
                                                                                            len(grinds)))

            return str(number), name, age, sex, grinds

    except urllib.error.URLError as e:
        # print("{}: {}".format(number, e.reason))
        return number, e.reason, None, None, []

    except ConnectionResetError as e:
        print(e)


def thread_collect_accounts(accounts, numbers, pool=6):
    dirty = False
    with concurrent.futures.ProcessPoolExecutor(pool) as executor:
        futures = [executor.submit(collect_grind_data, number) for number in numbers]
        concurrent.futures.wait(futures)

        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        for result in results:
            if result is not None:
                accounts = add_account(accounts,
                                       uuid=result[0],
                                       name=result[1],
                                       age=result[2],
                                       sex=result[3],
                                       grinds=result[4])
                dirty = True

    if dirty:
        dump_json_data(accounts)


def collect_account_numbers(min, max, step):
    accounts = load_json_data()
    file = os.path.expanduser("~/Documents/grousemountain_baddata.json")
    accounts_not_found = load_json_data(_storage_path=file)

    def get_unknown_uuids(min, max, step, _accounts, options):
        numbers = list()
        for option in options:
            print("Collecting: {}".format(option))
            for number in range(min + option, max + option, step):
                if str(number) not in _accounts.keys():
                    # print("[info] Found an uncollected number: {}".format(number))
                    numbers.append(number)
        print("[info] New numbers found: {}".format(len(numbers)))
        return numbers

    all_accounts = accounts.copy()
    all_accounts.update(accounts_not_found)
    if max > 100000:  # 00000:
        # accounts seem to end in:
        options = [0]
        # 8000,  # 18000,
        # 7000, 17000,
        # 6000, 16000,
        # 5000, 15000,
        # 4000, 14000,
        # 3000, 13000,
        # 2000, 12000]
        numbers = get_unknown_uuids(min, max, step, all_accounts, options)
    else:
        options = [0]
        numbers = get_unknown_uuids(min, max, step, all_accounts, options)

    thread_collect_accounts(accounts, numbers)


def split_accounts():
    # Split accounts between those that are "Not Found" and those that are valid.
    accounts = load_json_data()
    collection = [(uuid, data) for uuid, data in accounts.items() if data['name'] == "Not Found"]

    bad_accounts_dirty = False
    file = os.path.expanduser("~/Documents/grousemountain_baddata.json")
    bad_accounts = load_json_data(_storage_path=file)
    for info in collection:
        uuid, data = info
        if uuid not in bad_accounts.keys():
            bad_accounts[uuid] = data
            bad_accounts_dirty = True
    if bad_accounts_dirty:
        dump_json_data(bad_accounts, _storage_path=file)

    for uuid in bad_accounts.keys():
        if uuid in accounts.keys():
            del accounts[uuid]
    dump_json_data(accounts)

    print("Length of bad accounts: {}".format(len(bad_accounts)))


def merge_to_main_accounts(_path_to_merge):
    data_merge = load_json_data(_storage_path=_path_to_merge)
    accounts = load_json_data()
    dirty = False
    for uuid, data in data_merge.items():
        if uuid in accounts:
            if accounts[uuid]['grinds'] is None:
                accounts[uuid]['grinds'] = data['grinds']
            else:
                for grind in data['grinds']:
                    if grind not in accounts[uuid]['grinds']:
                        accounts[uuid]['grinds'].append(grind)
                        dirty = True
                        print('Updating: {}'.format(data['name']))

    if dirty:
        dump_json_data(accounts)


def update_accounts(min=0, start=44500000000, stop=445000000000000):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    accounts = load_json_data()
    dirty = False
    for uuid, data in accounts.items():
        if len(accounts[uuid]['grinds']) > min and start < int(uuid) < stop:

            if 'last_update' in accounts[uuid]:
                # print(uuid, "Needs Updating...")

                uuid, name, sex, age, grinds = collect_grind_data(uuid)

                if accounts[uuid]['grinds'] is None:
                    accounts[uuid]['grinds'] = list()

                for grind in grinds:
                    if grind not in accounts[uuid]['grinds']:
                        accounts[uuid]['grinds'].append(grind)
                        print('\tFound New Grind...')
                        dirty = True

                accounts[uuid]['last_update'] = current_date
    if dirty:
        dump_json_data(accounts)


def update_account(uuid, data):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    uuid, name, sex, age, grinds = collect_grind_data(uuid)

    if data['grinds'] is None:
        data['grinds'] = list()

    for grind in grinds:
        if grind not in data['grinds']:
            data['grinds'].append(grind)

    data['last_update'] = current_date

    return uuid, data


def thread_update_accounts(_min, _max, pool=10):
    accounts = load_json_data()
    dirty = False
    with concurrent.futures.ProcessPoolExecutor(pool) as executor:
        futures = [executor.submit(update_account, uuid, data) for uuid, data in accounts.items() if _min < int(uuid) < _max]
        concurrent.futures.wait(futures)

        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        for result in results:
            if result is not None:
                uuid, data = result
                accounts[uuid] = data
                dirty = True

    if dirty:
        dump_json_data(accounts)

    print("Completed...")

if __name__ == "__main__":
    end_max = 65000000000
    # end_max = 7000000000
    vals = range(0, end_max, 1000000000)
    for min, max in zip(vals, vals[1:]):
        #print(min, max)
        thread_update_accounts(min, max)

    # TODO: Create a click interface to download the changes for the day and scrape only those items.

    # thread_update_accounts(6000000000, 7000000001)
    # uuid = <VALID UUID>
    # print(collect_grind_data(uuid))

    # x = collect_grind_times([], 22597005000, page=1)
    # print(len(x))
    # 18014003000

    # collect_account_numbers(240000000000, 451000000000, 1000000)
    # recheck_names("Service Unavailable")
    # split_accounts()
    # grinds_over_100()
    # data_merge = os.path.expanduser("~/Documents/grousemountaindata_special.json")
    # merge_to_main_accounts(data_merge)

    pass
