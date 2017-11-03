import account
import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def update_missing_accounts(missings: list, storage_location='./data/missings.json'):
    """
    Keeps a very simple tally of missing account names and numbers from the known database.
    :param missings: list: current list of missing accounts.
    :param storage_location: str: path to location on disk
    :return:
    """

    records = account.load_json_data(storage_location)
    records['missing'] = list(set(records.get('missing', list()) + missings))
    account.dump_json_data(records, storage_location)


def yield_todays_grinds():
    """
    Using some parsing magic keys and phrases collect the day's Grouse Grinds logged on the main page.
    - Note that this page is constantly updated throughout the day
    - I have not bothered to find out when exactly the page resets
    :yields: list of items.
    """

    page = requests.get("https://grousemountain.com/grind_stats#key7")
    soup = BeautifulSoup(page.text, "html.parser")
    tds = (tr_tag.findAll('td') for tr_tag in soup.findAll('tr'))
    tds = (td.text.strip() for td in tds if hasattr(td, 'text'))

    for items in tds:
        if items[1].startswith(("M", "F")):
            yield items


def get_found_and_missing_accounts():
    """
    Find all the account UUIDs & Records as well as the missing users.
    - Return them as two different lists to be kept track of
    :return: list(), list() - first list is found account info, the second is missing.
    """

    # load existing account data
    accounts = account.load_json_data()

    # Get today's Grind Info.
    missings = list()
    uuids_and_records = list()

    for name, _, _, _ in yield_todays_grinds():
        found = False

        for uuid, record in accounts.items():
            if record['name'].lower() == name.lower():
                found = True
                uuids_and_records.append((uuid, record))
                break

        if not found:
            logger.warning("Missing name from existing records: {}".format(name))
            missings.append(name)

    return uuids_and_records, missings


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                        datefmt='%m-%d-%Y %H:%M',
                        level=logging.INFO)

    uuids_and_records, missings = get_found_and_missing_accounts()

    if uuids_and_records:
        account.thread_update_account(uuids_and_records)

    if missings:
        update_missing_accounts(missings)

