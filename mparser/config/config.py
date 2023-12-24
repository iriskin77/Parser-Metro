from fake_useragent import UserAgent
from pathlib import Path

class Settings:

    def __init__(self):
        self.fake_headers = UserAgent()

    headers = {
        "User-Agent": '',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
    }


    def get_path(self):
        abs_path: Path = Path(__file__).resolve().parent.parent
        return abs_path

    def get_headers(self):
        self.headers["User-Agent"] = self.fake_headers.random
        return self.headers

    def set_fake_ua(self):
        self.headers["User-Agent"] = self.fake_headers.random


settings = Settings()
