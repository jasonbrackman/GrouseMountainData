import account
import requests
from bs4 import BeautifulSoup


def missing_accounts(missings: list, storage_location='./data/missings.json'):
    records = account.load_json_data(storage_location)
    records = records if records else {'missing': []}
    records['missing'] = list(set(records['missing'] + missings))

    print("[info] Length of missing peeps: {}".format(len(records['missing'])))

    account.dump_json_data(records, storage_location)


def todays_grinds():
    root_url = "https://grousemountain.com/grind_stats#key7"
    page = requests.get(root_url)

    soup = BeautifulSoup(page.text, "html.parser")
    for name in soup.findAll('tr'):
        tds = name.findAll('td')
        if tds and len(tds) == 4:
            items = [td.text.strip() for td in tds if td.text.strip() != '']
            if len(items) == 4 and items[1].startswith(("M", "F")):
                yield items

if __name__ == "__main__":
    dirty = False

    # load existing account data
    accounts = account.load_json_data()

    # Get today's grinds
    names = (grind[0] for grind in todays_grinds())
    missings = list()
    for name in names:
        found = False

        for uuid, record in accounts.items():
            if record['name'].lower() == name.lower():
                found = True
                # print("Existing Account: {}".format(name))
                _uuid, _record = account.update_account(uuid, record)
                accounts[_uuid] = _record
                dirty = True
                break

        if not found:
            missings.append(name)

    for missing in missings:
        print('MISSING: {}'.format(missing))

    missing_accounts(missings)

    if dirty:
        account.dump_json_data(accounts)
