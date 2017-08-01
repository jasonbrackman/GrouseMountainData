# coding=utf-8
#
# Filename: account_test.py
#
# Create Date: 2016-10-01
#
# ------------------------------------------------------------------


import io
import account


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
    pass


def test_dump_json_data():
    account.load_json_data(_storage_path="")


if __name__ == '__main__':
    account = mock_account()
    print(account.read())



