import account

results = account.load_json_data('grousemountaindata_new.json')
print(len(results))
print(type(results))
for k, v in results.items():

    if v:
        if v['age']:
            if "Male" in v['age'] or "Female" in v['age']:
                print(k)
                print('SEX: ', v['sex'])
                print('AGE: ', v['age'])
                v['age'], v['sex'] = v['sex'], v['age']
                results[k] = v

        if v['sex']:
            if v['sex'][0].isdigit() is True:
                print('SEX: ', v['sex'])


# account.dump_json_data(results, 'grousemountaindata_new.json')