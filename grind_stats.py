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
    records = records if records else {'missing': []}
    records['missing'] = list(set(records['missing'] + missings))

    logger.info("Length of missing peeps: {}".format(len(records['missing'])))

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
    for name in soup.findAll('tr'):
        tds = name.findAll('td')
        if tds and len(tds) == 4:
            items = [td.text.strip() for td in tds if td.text.strip() != '']
            if len(items) == 4 and items[1].startswith(("M", "F")):
                yield items


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                        datefmt='%m-%d-%Y %H:%M',
                        level=logging.INFO)
    dirty = False

    # load existing account data
    accounts = account.load_json_data()

    # Get today's grinds
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

    update_missing_accounts(missings)

    account.thread_update_account(uuids_and_records)
