from json import loads, dump
import csv
from tabulate import tabulate
from math import asin, degrees
from collections import defaultdict

class Sanitizer:
    def __init__(self, source, match_id, s_l, c):
        self.json = source
        self.raw_data = []
        self.sanitized = False
        self.match_id = match_id
        self.season_league = s_l
        self.country = c


    def sanitize_data(self, csv=False):
        def transform_to_meters(x, y):
            meters_x = (100 - int(x)) * 1.05
            meters_y = abs(50 - int(y)) * 0.68

            return meters_x, meters_y

        data = []
        short_info = self.json

        league, season = list(map(lambda x: x.strip(), self.season_league.split("-")))

        shots_by_player_before = defaultdict(int)
        passes_by_player_before = defaultdict(int)
        shots_by_team_before = defaultdict(int)
        try:
            players = self.json["matchCentreData"]["playerIdNameDictionary"]
            home_team = self.json["matchCentreData"]["home"]
            # self.raw_data.append(self.json["matchCentreData"])
            away_team = self.json["matchCentreData"]["away"]
            away_team_name = away_team["name"]
            home_team_name = home_team["name"]
            away_team_players = away_team["players"]
            for i in away_team_players:
                del i["stats"]
            home_team_players = home_team["players"]
            for i in home_team_players:
                del i["stats"]
            # print(home_team)
            match_date = self.json["matchCentreData"]["startTime"]

            teams = {
                "home_team_id": home_team["teamId"],
                "home_team_name": home_team_name,
                "home_team_players": home_team_players,
                "away_team_id": away_team["teamId"],
                "away_team_name": away_team_name,
                "away_team_players": away_team_players,
                "match_date": match_date,
                "ft_score": self.json["matchCentreData"]["ftScore"],
                "country": self.country,
                "league": league,
                "season": season
            }
            # print(teams)

            players_list = []
            for playerId, playerName in players.items():
                players_list.append({"player_id": int(playerId), "player_name": playerName})

            for event in self.json["matchCentreData"]["events"]:
                if event["type"]["value"] == 1:
                    passes_by_player_before[event["playerId"]] += 1
                if "isShot" in event:
                    team_id = ""
                    team_name = ""
                    if event["teamId"] == home_team["teamId"]:
                        team_id = event["teamId"]
                        team_name = home_team_name
                    else:
                        team_id = event["teamId"]
                        team_name = away_team_name

                    event_to_data = {"match_id": self.match_id, "team_id": team_id, "team_name": team_name, "playerId": str(event["playerId"]), "x": event["x"], "y": event["y"],
                                     "shootedBy": None, "bigChance": False}

                    for piece in event['qualifiers']:
                        if piece["type"]["displayName"] in ("RightFoot", "LeftFoot", "Head"):
                            event_to_data["shootedBy"] = piece["type"]["displayName"]
                        if piece["type"]["displayName"] in ("BigChance"):
                            event_to_data["bigChance"] = True
                    meters = transform_to_meters(event_to_data['x'], event_to_data['y'])
                    distance = round((meters[0] ** 2 + meters[1] ** 2) ** 0.5, 5)

                    if "isOwnGoal" in event:
                        if event["isOwnGoal"]:
                            continue
                    # distance = ((100 - int(event_to_data['x'])) ** 2 + (100 - int(event_to_data['y'])) ** 2) ** 0.5
                    event_to_data["distance"] = distance
                    event_to_data["angle"] = round(degrees(asin(meters[1] / distance)), 5)
                    event_to_data["passes_before"] = passes_by_player_before[event["playerId"]]
                    event_to_data["shots_before"] = shots_by_player_before[event["playerId"]]
                    is_goal = event["isGoal"] if "isGoal" in event else False
                    event_to_data["shots_by_team_before"] = shots_by_team_before[event["teamId"]]
                    event_to_data["isGoal"] = is_goal
                    event_to_data["ft_score"] = self.json["matchCentreData"]["ftScore"]

                    data.append(event_to_data)

                    shots_by_team_before[event["teamId"]] += 1
                    shots_by_player_before[event["playerId"]] += 1
                    if is_goal:
                        shots_by_player_before[event["playerId"]] = 0
                        shots_by_team_before[event["teamId"]] = 0
            self.json = data
            self.sanitized = True
            return [self.json, players_list, teams]
        except:
            # print(self.json)
            return False

    def json_to_csv(self, filename: str = "data.csv"):
        if not self.sanitized:
            raise ValueError("Данные не обработаны, запись запрещена!")

        file = csv.writer(open(filename, "w"))
        file.writerow(self.json[0].keys())
        for stat in self.json:
            file.writerow([x[1] for x in stat.items()])
