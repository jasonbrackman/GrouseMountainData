import account
import itertools
from datetime import datetime
import collections


def collect_grinds_by_year(accounts):
    grind_attempts = collections.defaultdict(int)
    for uuid, data in accounts.items():
        if data['grinds']:
            dates = [grind['date'].split('-')[0] for grind in data['grinds']]
            count = collections.Counter(dates)
            for date, attempts in count.items():
                grind_attempts[date] += attempts

    print("Year\tCount")
    for k, v in sorted(grind_attempts.items()):
        print('{}\t{}'.format(k, v))


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
                    if data['sex'] == 'Male':
                        male_grind_attempts[attempts].append([uuid, data['name'], data['sex'], date])
                if females:
                    if data['sex'] == 'Female':
                        female_grind_attempts[attempts].append([uuid, data['name'], data['sex'], date])
                if unknowns:
                    if data['sex'] != 'Female' and data['sex'] != 'Male':
                        unknown_grind_attempts[attempts].append([uuid, data['name'], data['sex'], date])

    return male_grind_attempts, female_grind_attempts, unknown_grind_attempts


def get_overlapping_grinds(accounts, uuid):
    print(accounts[uuid]['name'])
    grinds = accounts[uuid]['grinds']

    for group in itertools.groupby(grinds, key=lambda x: x['date']):
        collection = group[1]

        starts_ends = [(datetime.strptime(item['start'], '%I:%M:%S %p'), datetime.strptime(item['end'], '%I:%M:%S %p'))
                       for item in collection]

        current_start = None
        current_end = None
        for item in reversed(starts_ends):
            # print('info: ', item)
            start = datetime.time(item[0])
            end = datetime.time(item[1])
            if current_start and current_end:
                possible_cheat = time_in_range(current_start, current_end, start)
                if possible_cheat:
                    print("Grind Overlap for {0}: Grind start ({1}) overlaps with the previous {2}-{3} of the same day".format(group[0], start, current_start, current_end))
            current_start = start
            current_end = end

    print('Grinds Parsed: ', len(grinds))


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


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
    print(len(accounts))

    # collect_grinds_by_year(accounts)
    display_multi_grind_table_stats()

    uuid = '22597005000'  # jasonb
    # get_overlapping_grinds(accounts, uuid)

    data = accounts[uuid]
    dates = [grind['date'] for grind in data['grinds']]
    count = collections.Counter(dates)

    print("Grinder: {}".format(data['name']))
    print("Grinds completed in a single day:")
    print("-" * 40)
    print('{:6}\t{:6}\t{:10}'.format("Month", "Max Grinds/Day", "Days Achieved Max"))
    total_grinds = 0
    months = ('off', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    for month in range(1, 13):

        counts_dates = [count for date, count in sorted(count.items()) if date.startswith('2017-{:02d}'.format(month))]
        final_count = collections.Counter(counts_dates)
        m = months[month]
        for multi, attempts in final_count.items():
            total_grinds += multi*attempts
            print('{:6}\t{:6}\t{:10}'.format(m, multi, attempts))
            m = '   '

    print("Total Grinds For Season: {}".format(total_grinds))
