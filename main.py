import account

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

if __name__ == "__main__":

    # get_grinder_info()
    # collect_account_numbers(10000000000, 65000000000, 1000000, _storage_path=new_storage_path)
    # convert_to_new_class(accounts)
    pass
