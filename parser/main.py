from parser.src.main_parser import ParserMetro
from src.config import settings
from fake_useragent import UserAgent

ua = UserAgent()

url_main = "https://online.metro-cc.ru/category/sladosti-chipsy-sneki/konfety-podarochnye-nabory"

path_file = settings.get_path()
name_file = 'products Metro4'
headers = settings.get_headers()

headers2 = {
        "User-Agent": ua.safari,
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
    }

def main():

    pars = ParserMetro(url_main, headers2, path_file, name_file)
    pars()


if __name__ == '__main__':
    main()

