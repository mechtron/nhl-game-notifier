from datetime import datetime
import pytz

from dynamo import get_users
from nhl_api import (
    get_teams,
    get_todays_games,
)
from sns import send_sms_notification


def convert_team_abbreviation_to_id(teams, team_abbreviation):
    for team in teams:
        if team["abbreviation"] == team_abbreviation:
            return team["id"]
    raise ValueError("Invalid team_abbreviation {}".format(team_abbreviation))


def team_is_playing(game, team_id):
    return (game["teams"]["away"]["team"]["id"] == team_id or
            game["teams"]["home"]["team"]["id"] == team_id)


def parse_game_date(game_date):
    return datetime.strptime(game_date, "%Y-%m-%dT%H:%M:%SZ")


def user_was_notified_recently(user):
    delta_seconds = (datetime.utcnow() - user["last_notified"]).total_seconds()
    delta_hours = delta_seconds / 3600
    return delta_hours < 12


def time_to_notify_user(user, game):
    game_datetime_parsed = parse_game_date(game["gameDate"])
    delta_seconds = (game_datetime_parsed - datetime.utcnow()).total_seconds()
    minutes_to_game_start = delta_seconds / 60
    time_to_notify = (
        minutes_to_game_start <= user["minutes_to_notify_before_game"] and
        not user_was_notified_recently(user)
    )
    print(
        "Game ID {game_id} starts in {minutes_to_start} minutes, time to "
        "notify user {user_sms} about {user_team}? {time_to_notify}".format(
            game_id=game["gamePk"],
            minutes_to_start=int(minutes_to_game_start),
            user_sms=user["sms_number"],
            user_team=user["team"],
            time_to_notify=time_to_notify,
        )
    )
    return time_to_notify


def convert_utc_to_est_pst_strings(date_time):
    fmt = "%I:%M %p"
    time_utc = date_time.replace(tzinfo=pytz.UTC)
    time_est = time_utc.astimezone(pytz.timezone('US/Eastern'))
    time_pst = time_utc.astimezone(pytz.timezone('US/Pacific'))
    return dict(
        est=time_est.strftime(fmt),
        pst=time_pst.strftime(fmt),
    )


def generate_sms_message(game):
    game_start_parsed = parse_game_date(game["gameDate"])
    game_start_strings = convert_utc_to_est_pst_strings(game_start_parsed)
    return (
        "It's gametime! {away_team} ({away_wins}-{away_losses}-{away_ot_so}) "
        "vs {home_team} ({home_wins}-{home_losses}-{home_ot_so}) "
        "starts at {game_start_time_est} EST/{game_start_time_pst} PST"
    ).format(
        away_team=game["teams"]["away"]["team"]["name"],
        away_wins=game["teams"]["away"]["leagueRecord"]["wins"],
        away_losses=game["teams"]["away"]["leagueRecord"]["losses"],
        away_ot_so=game["teams"]["away"]["leagueRecord"]["ot"],
        home_team=game["teams"]["home"]["team"]["name"],
        home_wins=game["teams"]["home"]["leagueRecord"]["wins"],
        home_losses=game["teams"]["home"]["leagueRecord"]["losses"],
        home_ot_so=game["teams"]["home"]["leagueRecord"]["ot"],
        game_start_time_est=game_start_strings['est'],
        game_start_time_pst=game_start_strings['pst'],
    )


def main():
    teams = get_teams()
    todays_games = get_todays_games()
    users = get_users()
    for user in users:
        user_favorite_team_id = convert_team_abbreviation_to_id(
            teams,
            user["team"],
        )
        for game in todays_games:
            if team_is_playing(game, user_favorite_team_id):
                if time_to_notify_user(user, game):
                    send_sms_notification(user, generate_sms_message(game))


def handler(_event, _context):
    main()


if __name__ == "__main__":
    main()
