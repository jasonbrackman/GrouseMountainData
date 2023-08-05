# coding=utf-8
#
# Filename: account_test.py
#
# Create Date: 2016-10-01
#
# ------------------------------------------------------------------


import io
from datascrape import account


def mock_account():
    accounts = dict()
    accounts['000001'] = {'name': 'John Smith',
                          'age': "20-29",
                          'sex': 'Male',
                          'grinds': [],
                          'last_update': '2016-06-03'}
    return io.StringIO(repr(accounts))
    # accounts[uuid] = {"name": name, "age": age, "sex": sex, "grinds": grinds, 'last_update': last_update}


def test_load_json_data():
    example = account.load_json_data(r'.\test.json')
    assert type(example) == dict


def test_add_account():
    test_uuid = -1
    test_accounts = account.add_account(dict())
    test_account_keys = test_accounts.get(test_uuid, dict()).keys()
    for key in ['name', 'age', 'sex', 'grinds', 'last_update']:
        if key not in test_account_keys:
            assert False, "The following key is missing from the account: {} Expected: {}".format(key, test_account_keys)


if __name__ == '__main__':
    account = mock_account()
    print(account.read())



