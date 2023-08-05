from datascrape import account
import logging

logging.basicConfig(format='%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s',
                    datefmt='%m-%d-%Y %H:%M',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

results = account.load_json_data()
logger.debug("Length of results: {}".format(len(results)))
logger.debug("Type of results: {}".format(type(results)))

for k, v in results.items():

    if v:
        if v['age']:
            if "Male" in v['age'] or "Female" in v['age']:
                logging.debug("User ID: {}".format(k))
                logging.debug('SEX: ', v['sex'])
                logging.debug('AGE: ', v['age'])
                v['age'], v['sex'] = v['sex'], v['age']
                results[k] = v

        if v['sex']:
            if v['sex'][0].isdigit() is True:
                logging.debug('SEX: ', v['sex'])

# account.dump_json_data(results, 'grousemountaindata_new.json')