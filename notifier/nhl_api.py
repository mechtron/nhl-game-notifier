import requests


NHL_API_BASE_URL = "https://statsapi.web.nhl.com/api/v1"


def get_teams():
    teams = requests.get("{}/teams".format(NHL_API_BASE_URL))
    return teams.json()["teams"]


def get_todays_games():
    todays_games = requests.get("{}/schedule".format(NHL_API_BASE_URL))
    return todays_games.json()['dates'][0]['games']


def get_team_stats(team_id):
    team_stats = requests.get("{base_url}/teams/{team_id}/stats".format(
        base_url=NHL_API_BASE_URL,
        team_id=team_id,
    ))
    return team_stats.json()["stats"]
