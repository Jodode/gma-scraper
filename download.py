from fake_headers import Headers
from requests import request, ConnectionError
import cloudscraper


class Downloader(object):

    def __init__(self, url: str = "https://google.com", params=None, method: str = "GET"):
        self.__data__ = None
        if params is None:
            params = {}

        # self.__method = method
        self.scrap_drive = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )
        self.__url = url
        self.params = params
        self.headers = Headers(headers=True).generate()

    def make_request(self):
        try:

            data = self.scrap_drive.get(self.__url)
            if data.ok:
                self.__data__ = data
            else:
                raise ValueError(f"Сайт недоступен, код ошибки {data.status_code}")
        except ConnectionError:
            raise ConnectionError("Такого сайта не существует")

    def get_html(self):
        if self.__data__ is None:
            self.make_request()
        return self.__data__.text

    def save(self, filename="index.html"):
        try:
            file = open(filename, "w")
            if self.__data__ is None:
                raise ValueError("Нет данных с сайта")
            file.write(self.__data__.text)
            file.close()
        except:
            raise FileExistsError("Файл уже существует!")

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value
        self.make_request()

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, value):
        self.__method = value
        self.make_request()
