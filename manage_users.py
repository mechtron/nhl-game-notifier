#!/usr/bin/env python3

import argparse
from prettytable import PrettyTable

from notifier.dynamo import (
    create_user,
    delete_user,
    get_users,
)


def print_users(users):
    table = PrettyTable([
        "Id", "SmsNumber", "SmsNumberIsSubscribed", "FavouriteTeam", 
        "MinutesToNotifyBeforeGameStart", "LastNotified",
    ])
    for user in users:
        table.add_row([
            user["Id"],
            user["SmsNumber"],
            user["SmsNumberIsSubscribed"],
            user["FavouriteTeam"],
            user["MinutesToNotifyBeforeGameStart"],
            user["LastNotified"],
        ])
    print(table)


def manage_users(parsed_args):
    if parsed_args.action == "list":
        users = get_users()
        print_users(users)
    elif parsed_args.action == "create":
        create_user(
            sms_number=parsed_args.sms,
            team=parsed_args.team,
            minutes_to_notify_before=(
                parsed_args.notify_before_minutes
            ),
        )
    elif parsed_args.action == "delete":
        delete_user(parsed_args.id)
    else:
        raise ValueError("Invalid action {}".format(parsed_args.action))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="NHL Game Notififer user management interface"
    )
    parser.add_argument(
        "-a",
        "--action",
        help='Action (list, create or delete)',
        choices=["list", "create", "delete"],
        required=True,
    )
    parser.add_argument(
        "-i",
        "--id",
        help="User ID to delete (optional)",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-s",
        "--sms",
        help="User's SMS number",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-t",
        "--team",
        help="NHL team (3 character abbreviation)",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-n",
        "--notify-before-minutes",
        help="How many minutes to notify the user before new games",
        required=False,
        default=None,
    )
    parsed_args = parser.parse_args()
    manage_users(parsed_args)
