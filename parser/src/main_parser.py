import pandas as pd
import numpy as np
from .logg import init_logger
from .parsers import ParserDetail, ParserIdBrand


class ParserMetro(ParserDetail, ParserIdBrand):

    logger = init_logger(__name__)

    def __init__(self, url_main: str, headers: dict, path_file: str, name_file: str):
        self.url_main = url_main
        self.headers = headers
        self.path_file = path_file
        self.name_file = name_file

    def merge(self, json_brands, json_names):
        for key in json_names:
            if key in json_brands:
                json_brands[key]['actual_price'] = json_names[key]['actual_price']
                json_brands[key]['old_price'] = json_names[key]['old_price']
                json_brands[key]['link'] = json_names[key]['link']

        return json_brands

    def write_to_excel(self, *args, path_file: str, name_file: str) -> None:

        names_columns = ["id", "Название", "Цена со скидкой", "Цена без скидки", "Бренд", "Ссылка"]
        res = pd.DataFrame()
        for index in range(len(names_columns)):
            name_column = names_columns[index]
            lst = args[index]
            res[name_column] = pd.Series(lst)

        res["Цена без скидки"] = res["Цена без скидки"].replace('', np.nan)
        mask = res["Цена без скидки"].isnull()
        res.loc[mask, ["Цена со скидкой", "Цена без скидки"]] = res.loc[mask, ["Цена без скидки", "Цена со скидкой"]].to_numpy()
        res.to_excel(f'{path_file}/{name_file}.xlsx', index=False)

#url_main: str, headers: dict, path_file: str, name_file: str
    def __call__(self) -> None:
        links_pages = self.get_pages_url(self.url_main, self.headers)
        checked_links_pages = self.check_instock(links_pages, self.headers)
        self.collect_info_cards(checked_links_pages, self.headers)
        self.collect_id_brand(checked_links_pages, self.headers)
        print("ID_BRANDS")
        for i in self.dct_res.items():
            print(i)
        print('NAMES_PRICE')
        for i in self.dct_res2.items():
            print(i)



