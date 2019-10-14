import csv
import os
import sys


def get_users():
    # TODO: grab users from DynamoDB
    users = []
    with open(os.path.join(sys.path[0], 'users.csv')) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            user = dict()
            for col in reader.fieldnames:
                user[col] = row[col]
            users.append(user)
    return users


# get_users()
