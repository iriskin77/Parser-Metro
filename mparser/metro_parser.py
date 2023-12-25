import json
from datetime import datetime
from random import choice
from apscheduler.schedulers.background import BlockingScheduler
from mparser.logs.logg import init_logger
from mparser.parsers_cls import ParserDetail, ParserIdBrand
from mparser.config.config import settings


class ParserMetro(ParserDetail, ParserIdBrand):


    def __init__(self, url_main: str, prox: list[dict]):
        self.url_main = url_main
        self.prox = prox
        self.scheduler = BlockingScheduler()
        self.headers = settings.get_headers()
        self.path_file = settings.get_path()

    def merge_jsons(self, json_brands, json_names):
        for key in json_names:
            if key in json_brands:
                json_brands[key]['actual_price'] = json_names[key]['actual_price']
                json_brands[key]['old_price'] = json_names[key]['old_price']
                json_brands[key]['link'] = json_names[key]['link']

        return json_brands

    def execute(self) -> None:
        self.logger.info("The parser has started")
        proxi = choice(self.prox)
        links_pages = self.get_pages_url(self.url_main, self.headers, proxi)
        self.collect_info_cards(links_pages, self.headers)
        self.collect_id_brand(links_pages, self.headers, proxi)
        js = self.merge_jsons(self.products_id_brand, self.products_detail)
        with open(f"{self.path_file}/data/products_candies2.json", "w", encoding="utf-8") as file:
            json.dump(js, file, indent=4, ensure_ascii=False)
        self.logger.info("The parser has finished correctly, data was loaded into json. Next start in 24 hours")

    def __call__(self, *args, **kwargs):
        self.scheduler.add_job(self.execute, 'interval', hours=24)

        for job in self.scheduler.get_jobs():
            job.modify(next_run_time=datetime.now())

        self.scheduler.start()





