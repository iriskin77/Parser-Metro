from Parser-Metro.mparser.metro_parser import ParserMetro


url_main = "https://online.metro-cc.ru/category/sladosti-chipsy-sneki/konfety-podarochnye-nabory"

prox = [
        {"http": "http://217.29.53.133:11012"},
        {"https": "https://217.29.53.104:11045"},
        {"https": "https://217.29.53.104:11046"},
]

def main():

    pars_metro = ParserMetro(url_main, prox)
    pars_metro()

if __name__ == '__main__':
    main()





