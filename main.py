import account
import itertools
from datetime import datetime
import collections


def collect_multi_grind_attempts(accounts, males=True, females=True, unknowns=True):
    male_grind_attempts = collections.defaultdict(list)
    female_grind_attempts = collections.defaultdict(list)
    unknown_grind_attempts = collections.defaultdict(list)

    for uuid, data in accounts.items():
        if data['grinds'] is not None:
            dates = [grind['date'] for grind in data['grinds']]
            count = collections.Counter(dates)
            for date, attempts in count.items():
                if males:
                    if data['age'] == 'Male':
                        male_grind_attempts[attempts].append([uuid, data['name'], data['sex'], date])
                if females:
                    if data['age'] == 'Female':
                        female_grind_attempts[attempts].append([uuid, data['name'], data['sex'], date])
                if unknowns:
                    if data['age'] != 'Female' and data['age'] != 'Male':
                        unknown_grind_attempts[attempts].append([uuid, data['name'], data['sex'], date])

    return male_grind_attempts, female_grind_attempts, unknown_grind_attempts


def get_overlapping_grinds(accounts):
    # from datetime import datetime
    # from collections import namedtuple
    # Range = namedtuple('Range', ['start', 'end'])
    # r1 = Range(start=datetime(2012, 1, 15), end=datetime(2012, 5, 10))
    # r2 = Range(start=datetime(2012, 3, 20), end=datetime(2012, 9, 15))
    # latest_start = max(r1.start, r2.start)
    # earliest_end = min(r1.end, r2.end)
    # overlap = (earliest_end - latest_start).days + 1
    # print(overlap)

    grinds = accounts['13321']['grinds']

    for group in itertools.groupby(grinds, key=lambda x: x['date']):
        print("")
        #collection = group[1]
        starts_ends = [(datetime.strptime(item['start'], '%I:%M:%S %p'), datetime.strptime(item['end'], '%I:%M:%S %p'))
        for item in group[1]]
        print(starts_ends)
        print("Max: ", max((starts for starts in starts_ends[0])))
        print("Min: ", min((starts for starts in starts_ends[1])))
        #for item in sorted(starts):
        #    print(item)

        # for item in group[1]:
        #    print(group[0], item['start'])

    print('grinds: ', len(grinds))



def get_grinder_info():
    accounts = account.load_json_data()
    while True:
        result = input("Name please: ")
        if result == 'Q':
            break
        else:
            for uuid, data in accounts.items():
                account_name = data['name']
                if result.lower() in account_name.lower():
                    if data['grinds'] is not None:
                        print("{}: {}".format(account_name, data['grinds']))
                    else:
                        print("{}: {}".format(account_name, "No Grind Times Found."))


def display_multi_grind_table_stats():
    male_results, female_results, unknown_results = collect_multi_grind_attempts(accounts)
    males = [(k, len(v)) for k, v in male_results.items()]
    females = [(k, len(v)) for k, v in female_results.items()]
    unknowns = [(k, len(v)) for k, v in unknown_results.items()]
    # for k, v in results.items():
    #    for item in v:
    #        print(item[1], item[3], item[-1])
    print("\n{:10}{:8}{:11}{}".format("Females", "Males", "Unknowns", "Same Day Attempts:"))
    for index in range(1, 17):
        male = [item for item in males if item[0] == index]
        female = [item for item in females if item[0] == index]
        unknown = [item for item in unknowns if item[0] == index]

        male = 0 if len(male) == 0 else male[0][1]
        female = 0 if len(female) == 0 else female[0][1]
        unknown = 0 if len(unknown) == 0 else unknown[0][1]

        print("{:7}{:8}{:11}{:4}".format(female, male, unknown, index))


if __name__ == "__main__":
    accounts = account.load_json_data()
    get_overlapping_grinds(accounts)

    # display_multi_grind_table_stats()
