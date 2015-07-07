import os
import re
import json
import urllib.request
import urllib.error
import concurrent.futures
from bs4 import BeautifulSoup

def add_account(accounts, uuid=-1, name=None, age=None, sex=None, grinds=None):
    accounts[uuid] = {"name": name, "age": age, "sex": sex, "grinds": grinds}
    return accounts

def collect_grind_times(grind_times, uuid, _page=1):
    """
    grind_times is a list that contains dicts of date, start, end, time
    uuid is the user's unique identifier
    the page is used if there are several pages of json data regarding past grind times.
    """
    titles = ('date', 'start', 'end', 'time')
    pattern = re.compile('.*page=(\d.*)')

    url_02 = "http://www.grousemountain.com/grind_stats/{0}".format(uuid)
    """
    # the first URL was working up until the end of June/2015 -- then the site broke.??
    # the second URL must be retrieving the data internally, but the history is incomplete, only showing 100 climbs.
    url_01 = "http://www.grousemountain.com/grind_stats/{0}.json?page={1}".format(uuid, _page)

    try:
        with urllib.request.urlopen(url_01) as request:
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
                    times = dict(zip(titles, data))
                    if times not in grind_times:
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
    """
    try:
        with urllib.request.urlopen(url_02) as request:
            soup = BeautifulSoup(request.read(), "html.parser")

            data = [table.findAll('tr') for table in soup.findAll('table', {'class': 'table grind_log thin'})]
            for grinds in data:
                for grind in grinds:
                    times = [item.string.strip() for item in grind.findAll('td')]
                    times = dict(zip(titles, times))
                    if len(times) > 0 and times not in grind_times:
                        grind_times.append(times)

    except urllib.error.URLError as e:
        print("[ERROR] {}".format(e.reason))

    return grind_times

def load_json_data(_storage_path=os.path.expanduser("~/Documents/grousemountaindata.json")):
    print("[LOADING] {}".format(_storage_path))

    # default accounts dict() to return if nothing has yet been saved to a file.
    accounts = dict()
    if os.path.isfile(_storage_path):
        with open(_storage_path, 'r',) as handle:
            accounts = json.load(handle)

    print("[LOADING] Complete!")

    return accounts

def dump_json_data(data, _storage_path=os.path.expanduser("~/Documents/grousemountaindata.json")):

    print("[SAVING] {}".format(_storage_path))
    with open(_storage_path, 'w') as handle:
        json.dump(data, handle)
    print("[SAVING] Complete!")

def get_grind_data(number):
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

            return str(number), name, sex, age, grinds

    except urllib.error.URLError as e:
        # print("{}: {}".format(number, e.reason))
        return number, e.reason, None, None, []

    except ConnectionResetError as e:
        print(e)
"""
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


def create_account(_accounts, uuid, username):
    if "Not Found" not in username and "Service Unavailable" not in username:
        print("[info] Getting Grind times for: {}".format(username))
        grinds = collect_grind_times([], uuid)
    else:
        grinds = None

    accounts = add_account(_accounts, uuid=uuid, name=username, grinds=grinds)
    return accounts
"""

def collect_account_numbers(min, max, step):
    accounts = load_json_data()

    def get_unknown_uuids(min, max, step, _accounts):
        # accounts seem to end in:
        options = [5000,
                   15000,
                   6000,
                   16000,
                   4000,
                   14000,
                   3000,
                   13000,
                   2000,
                   12000]

        numbers = list()
        for option in options:
            print("Collecting: {}".format(option))
            for number in range(min+option, max+option, step):
                if str(number) not in _accounts.keys():
                    print("[info] Found an uncollected number: {}".format(number))
                    numbers.append(number)
        print(len(numbers))
        return numbers

    dirty = False
    pool = 4
    numbers = get_unknown_uuids(min, max, step, accounts)
    with concurrent.futures.ProcessPoolExecutor(pool) as executor:
        futures = [executor.submit(get_grind_data, number) for number in numbers]
        concurrent.futures.wait(futures)
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        for result in results:
            if result is not None:
                accounts = add_account(accounts,
                                       uuid=result[0],
                                       name=result[1],
                                       age=result[2],
                                       sex=result[3],
                                       grinds=results[4])
                dirty = True

    if dirty:
        dump_json_data(accounts)

if __name__ == "__main__":
    # uuid = 22597005000
    # print(get_grind_data(uuid))

    # x = collect_grind_times([], 22597005000, page=1)
    # print(len(x))

    collect_account_numbers(10000000000, 68000000000, 1000000)

    pass
