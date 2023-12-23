import requests
import re
import unidecode
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiohttp_retry import RetryClient, ExponentialRetry
from .utils import ParserMetroMixin
from .logg import init_logger


class ParserIdBrand(ParserMetroMixin):

    res_from_class = {
        'name_product': {
        'id': 123,
        'brand': 'name_brand'
    }
    }

    logger = init_logger(__name__)

    main_page = "https://online.metro-cc.ru"

    lst_all_brands = []
    lst_all_id = []

    dct_res = {}

    def get_products_links(self, lst_links_pages: list[str], headers) -> list[str] | str:
        """"Input: links to pages with products.
            Output: the function returns a list with links to all product cards"""""
        self.logger.info(f'Fn {self.get_products_links.__name__} has started')
        links_all_products = []
        for page_link in lst_links_pages:
            try:
                response = requests.get(url=page_link, headers=headers, timeout=120)
            except:
                response = requests.get(url=page_link, headers=headers, timeout=120)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                links = soup.find_all('a', class_="product-card-photo__link reset-link")
                products_links = [self.main_page + link["href"] for link in links]
                for product_link in products_links:
                    links_all_products.append(product_link)
            else:
                self.logger.critical(f'Fn {self.get_products_links.__name__} has finished incorrectly')
                return f"Bad request, status: {response.status_code}"

        self.logger.info(f'Fn {self.get_products_links.__name__} has finished correctly')
        return links_all_products

    async def get_id_brand(self, session, link_product_card: str, headers: dict) -> None:
        """"Input: link to a product card.
            Output: the function retrieves id and brand from a product card"""""

        retry_options = ExponentialRetry(attempts=5)
        retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, client_session=session, start_timeout=1.5)

        async with retry_client.get(url=link_product_card, headers=headers) as response:
            if response.ok:
                resp = await response.text()
                link_card = BeautifulSoup(resp, 'lxml')

                # get and save name
                name = link_card.find('h1', class_='product-page-content__product-name catalog-heading heading__h2').get_text(strip=True)

                # get and save id
                id = link_card.find('p', class_='product-page-content__article').get_text(strip=True)
                id = id.split(":")[1].strip()
                #self.lst_all_id.append(id.split(":")[1])

                # get and save brand
                characteristics = link_card.find_all('li', class_='product-attributes__list-item')
                ch = [i.get_text(strip=True) for i in characteristics]
                brand = ''.join([i[5:] for i in ch if re.search('Бренд', i) is not None])
                #self.lst_all_brands.append(brand)

                self.dct_res[name] = {
                    'id': int(id),
                    'brand': brand,
                }

            else:
                self.logger.warning(f"Fn {self.get_id_brand} works incorrectly. Bad request: {response.status}")

    async def get_cards_info(self, links_product_cards: list[str], headers) -> None:
        """"Input: links to product cards.
            Output: the function retrieves id and brand from all product cards"""""

        self.logger.info(f'Fn {self.get_cards_info.__name__} has started')
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for link_product in links_product_cards:
                task = asyncio.create_task(self.get_id_brand(session=session, link_product_card=link_product, headers=headers))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self.logger.info(f'Fn {self.get_cards_info.__name__} has finished correctly')

    def collect_id_brand(self, checked_pages: list[str], headers: dict):
        """"Input: link to a page with category (meet, bread, etc.).
            Output: the function retrieves id and brand of all products using the function get_cards_info"""""
        #links_pages = self.get_pages_url(url_main, headers)
        #checked_links_pages = self.check_instock(links_pages, headers)
        #print('CHECKED_LINKS_PAGES', checked_links_pages)
        product_cards = self.get_products_links(lst_links_pages=checked_pages, headers=headers)
        asyncio.run(self.get_cards_info(product_cards, headers))

# links_pages = self.get_pages_url(url_main, headers)
# checked_links_pages = self.check_instock(links_pages, headers)
# asyncio.run(self.get_info_products(checked_links_pages, headers))


class ParserDetail(ParserMetroMixin):

    # a = {
    #     { 'name': {
    #         'actual_price': 123,
    #         'old_price': 123,
    #         'link': 'https',
    #     }
    #     }
    # }

    dct_res2 = {}

    logger = init_logger(__name__)

    main_page = "https://online.metro-cc.ru"

    lst_all_titles = []
    lst_all_actual_prices = []
    lst_all_old_prices = []
    lst_all_links = []

    async def get_info_products(self, list_links_pages: list[str], headers) -> None:
        """"Input: link to all pages with products.
            Output: the function retrieves names, prices, links of all products"""""

        self.logger.info(f'{self.get_info_products.__name__} has started')

        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for link_page in list_links_pages:
                task = asyncio.create_task(self.get_info_product(session=session, link_page=link_page, headers=headers))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self.logger.info(f'{self.get_info_products.__name__} has finished correctly')

    async def get_info_product(self, session, link_page: str, headers: dict) -> None:
            """"Input: link to a page with products.
                Output: the function retrieves name, price, link of a product"""""

            retry_options = ExponentialRetry(attempts=5)
            retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, client_session=session, start_timeout=1.5)

            async with retry_client.get(url=link_page, headers=headers) as response:
                resp = await response.text()
                soup = BeautifulSoup(resp, "lxml")

                # Get and save products titles
                try:
                    lst_title = soup.find_all("span", class_="product-card-name__text")
                    titles = [t.text.strip() for t in lst_title]
                    for title in titles:
                        self.dct_res2[title] = {}
                    #self.lst_all_titles.extend(titles)
                except Exception as ex:
                    self.logger.warning(f'Fn {self.get_info_product}. Failed to retrieve products titles. Message error: {ex}')

                # Get and save products actual prices
                try:
                    actual_prices = soup.find_all("div", class_="product-unit-prices__actual-wrapper")
                    actual_prices = [unidecode.unidecode(p.find("span", class_="product-price__sum-rubles").text.strip()) for p in actual_prices]
                    for item in self.dct_res2.items():
                        for price in actual_prices:
                            self.dct_res2[item[0]]['actual_price'] = price
                    #self.lst_all_actual_prices.extend(actual_prices)
                except Exception as ex:
                    self.logger.warning(f'Fn {self.get_info_product}. Failed to retrieve products actual prices. Message error: {ex}')

                # Get and save products old prices
                try:
                    old_prices = soup.find_all("div", class_="product-unit-prices__old-wrapper")
                    old_prices = [unidecode.unidecode(p.get_text(strip=True)).rstrip("d/sht") for p in old_prices]
                    for item in self.dct_res2.items():
                        for price in old_prices:
                            self.dct_res2[item[0]]['old_price'] = price
                    #self.lst_all_old_prices.extend(old_prices)
                except Exception as ex:
                    self.logger.warning(f'Fn {self.get_info_product}. Failed to retrieve products old prices. Message error: {ex}')

                # Get and save products links
                try:
                    all_links = soup.find_all("a", class_="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card")
                    all_links = [self.main_page + p["href"] for p in all_links]
                    for item in self.dct_res2.items():
                        for link in all_links:
                            self.dct_res2[item[0]]['link'] = link
                    #self.lst_all_links.extend(all_links)
                except Exception as ex:
                    self.logger.warning(f'Fn {self.get_info_product}. Failed to retrieve products links. Message error: {ex}')

    def collect_info_cards(self, checked_pages: list[str], headers) -> None:
        """"Input: link to a page with category (meet, bread, etc.).
            Output: the function retrieves names, prices, links of all products using the function get_info_products"""""

        #links_pages = self.get_pages_url(url_main, headers)
        #checked_links_pages = self.check_instock(links_pages, headers)
        asyncio.run(self.get_info_products(checked_pages, headers))

