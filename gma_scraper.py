import json

import bs4
import cloudscraper
from collections import defaultdict
from requests import request, HTTPError, ConnectionError
from fake_headers import Headers
import ast
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from parse import Parser
from data import Sanitizer
from json import dumps
import time

class Scraper(object):
    def __init__(self):
        self.__url__ = "https://1xbet.whoscored.com"
        self.webdriver = webdriver.Safari()
        # self.__team_id__ = team_id
        self.league = "rpl_last"
        self.__html__ = None
        self.__teams__ = {}
        self.__seasons_url__ = []
        self.__seasons_id__ = []
        self.matches_id = []

    def __getHTML__(self, url: str = None):
        try:
            self.webdriver.get(url)
            time.sleep(3)
            self.__html__ = self.webdriver.page_source

            data = self.webdriver.execute_script('''
            data = JSON.stringify(tables[0]["performance"]);
            return data;
            ''')
            data = ast.literal_eval(data)
            for team in data:

                if team[1] not in self.__teams__:
                    self.__teams__[team[1]] = team[2]
                    self.__seasons_id__.append(team[0])
            # self.webdriver.close()

        except HTTPError as e:
            raise e

    def scrape_seasons(self):
        soup = bs4.BeautifulSoup(self.__html__, "html.parser")
        season_tags = soup.find_all("select", {"id": "seasons"})[0].find_all("option")

        for season_tag in season_tags:
            self.__seasons_url__.append(season_tag.get("value"))

    def scrape_matches_id(self):
        scrap_drive = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )

        for delta, season in enumerate(self.__seasons_id__):
            end_year = 2023 - delta
            start_year = end_year - 1
            for year in range(start_year, end_year + 1):
                for month in range(13):
                    api_content = scrap_drive.get(f"https://1xbet.whoscored.com/tournamentsfeed/{season}/Fixtures/?d={year}{f'0{month}' if month < 10 else month}&isAggregate=false&showAllStageMatches=true").text
                    api_content = api_content.replace(",,", ",0,")
                    try:
                        data = ast.literal_eval(api_content)
                    except:
                        print("BAD API")
                        continue
                    time.sleep(5)
                    if len(data) > 0:
                        for match in data:
                            self.matches_id.append(match[0])

        open(f"matches_id_{self.league}.txt", "w").write(str(self.matches_id))

    def __getTeams__(self):
        return self.__teams__

    def __scrape_matches__(self):

        self.matches_id = ast.literal_eval(open(f"matches_id_{self.league}.txt").read())

        scrap_drive = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )

        csv_data = []
        # print(self.matches_id[-1])
        # print(len(self.matches_id))
        # return
        dump_json = {}
        players = []
        teams_per_match = {}
        for i, match_id in enumerate(self.matches_id):
            if i % 100 == 0:
                print(i)
            data = scrap_drive.get(f"https://1xbet.whoscored.com/Matches/{int(match_id)}/Live/").text
            time.sleep(5)
            parser_whoscored = Parser(data)

            json_data, season_league, country = parser_whoscored.parse()
            if json_data == False:
                continue
            dump_json[match_id] = json_data
            sanit = Sanitizer(json_data, match_id, season_league, country)

            sanit_data = sanit.sanitize_data()
            if not sanit_data:
                print(sanit_data)
                print("Bad Data")
            else:
                # print(sanit_data)
                players.extend(sanit_data[1])
                csv_data.extend(sanit_data[0])
                teams_per_match[match_id] = sanit_data[2]
        # print(csv_data)

        open(f"matches_{self.league}.txt", "w").write(json.dumps(teams_per_match))

        #
        file = csv.writer(open(f"data_res_{self.league}.csv", "w"))
        file.writerow(csv_data[0].keys())
        for stat in csv_data:
            file.writerow([x[1] for x in stat.items()])


        file = csv.writer(open(f"players_res_{self.league}.csv", "w"))
        file.writerow(players[0].keys())
        for stat in players:
            file.writerow([x[1] for x in stat.items()])

    def process(self):
        # self.__getHTML__(self.__url__ + "/Regions/182/Tournaments/77")
        # self.scrape_seasons()
        # print(self.__seasons_url__[0])
        # # for season in self.__seasons_url__[:6]:
        # self.__getHTML__(self.__url__ + self.__seasons_url__[0])
        # #     # print(self.__teams__)
        # self.__seasons_id__ = sorted(set(self.__seasons_id__), reverse=True)
        # print(self.__seasons_id__)
        # self.scrape_matches_id()
        self.__scrape_matches__()



# print(scrap_driver.get("https://1xbet.whoscored.com/Regions/81/Tournaments/6/Germany-2-Bundesliga").text)
Scraper().process()
