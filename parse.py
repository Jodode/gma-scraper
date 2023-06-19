from download import Downloader
from bs4 import BeautifulSoup
from json import loads, dumps

class Parser:
    def __init__(self, data=""):
        self.data = data
        # self.source = source
        self.json = None
        self.season_league = "None - None"
        self.country = "NoCountry"

    def parse(self):
        def magic():
            soup = BeautifulSoup(self.data, "html.parser")
            tags = soup.find_all("script")
            try:
                tags_for_season = soup.find_all("div", {"id": "breadcrumb-nav"})
                self.season_league = tags_for_season[0].find_next("a").contents[0].strip()
            except:
                print("Fail season and league")

            try:
                tags_for_season = soup.find_all("div", {"id": "breadcrumb-nav"})
                self.country = tags_for_season[0].find_next("span", {"class": "iconize"}).contents[1]
            except:
                print("Country fail")
            # print(tags_for_season[0].find_next("span", {"class": "iconize"}).contents)
            text = ""
            for tag in tags:
                if "matchCentreData" in tag.text:
                    text = tag.text
                    break
            if text == "":
                return False

            json_text = text.split("=")[1].strip()[:-1].replace('matchId', '"matchId"').replace('matchCentreData',
                                                                                                '"matchCentreData"')  # .replace('"', "'")
            placement_to_remove = json_text.find("matchCentreEventTypeJson")
            last_comma = json_text[:placement_to_remove].rfind(",")
            json_text = json_text[:last_comma] + '}'
            first_quote = json_text.find('"')
            json_text = '{' + json_text[first_quote:]

            self.json = loads(json_text)

        magic()

        return self.json, self.season_league, self.country

    def save(self, path_to_save="dump.json"):
        file = open(path_to_save, 'w')
        file.write(dumps(self.json))
        file.close()
