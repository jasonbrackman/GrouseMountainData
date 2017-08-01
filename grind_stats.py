import ssl
import account
import urllib.request
from bs4 import BeautifulSoup


def todays_grinds():
    root_url = "https://grousemountain.com/grind_stats#key7"
    gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)  # Only for gangstars
    with urllib.request.urlopen(root_url, context=gcontext) as page:
        soup = BeautifulSoup(page.read(), "html.parser")

        for name in soup.findAll('tr'):
            tds = name.findAll('td')
            if tds and len(tds) == 4:
                items = [td.text.strip() for td in tds if td.text.strip() != '']
                if len(items) == 4 and items[1].startswith(("M", "F")):
                    yield items

accounts = account.load_json_data()
results = todays_grinds()
for result in results:
    found = False
    for k, v in accounts.items():
        # print(v['name'])
        if v['name'] == result[0]:
            found = True
            print("found: {}".format(result[0]))
            break

    if not found:
        print('MISSING: {}'.format(result[0]))

    #print(result[0])
