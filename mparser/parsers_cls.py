import requests
import re
import unidecode
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiohttp_retry import RetryClient, ExponentialRetry
from requests.adapters import HTTPAdapter
from mparser.utils import ParserMetroMixin
from mparser.logg import init_logger

prox = {"http": "http://217.29.53.133:11012"}

class ParserIdBrand(ParserMetroMixin):

    logger = init_logger(__name__)

    main_page = "https://online.metro-cc.ru"

    products_id_brand = {}

    def get_products_links(self, lst_links_pages: list[str], headers: dict, prox: dict) -> list[str] | str:
        """"Input: links to pages with products.
            Output: the function returns a list with links to all product cards"""""

        self.logger.info(f'Fn get_products_links has started')

        links_all_products = []
        print('LINKS_PAGES FROM get_products_links',  lst_links_pages)
        for page_link in lst_links_pages:
            try:
                response, resp_status = self.make_request(url=page_link, headers=headers, prox=prox)
            except:
                response, resp_status = self.make_request(url=page_link, headers=headers, prox=prox)

            if resp_status == 200:
                soup = BeautifulSoup(response.text, "lxml")
                # check if products in stock
                if self.check_instock_page(soup):
                    links = soup.find_all('a', class_="product-card-photo__link reset-link")
                    products_links = [self.main_page + link["href"] for link in links]
                    for product_link in products_links:
                        links_all_products.append(product_link)
            else:
                self.logger.critical(f'Fn get_products_links. Failed to connect to a page to get products links. Bad request: {resp_status}')

        self.logger.info(f'Fn get_products_links has finished correctly')
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

                # get and save brand
                characteristics = link_card.find_all('li', class_='product-attributes__list-item')
                ch = [i.get_text(strip=True) for i in characteristics]
                brand = ''.join([i[5:] for i in ch if re.search('Бренд', i) is not None])

                self.products_id_brand[name] = {
                    'id': int(id),
                    'brand': brand,
                }

            else:
                self.logger.warning(f"Fn get_id_brand works incorrectly. Bad request: {response.status}")

    async def get_cards_info(self, links_product_cards: list[str], headers) -> None:
        """"Input: links to product cards.
            Output: the function retrieves id and brand from all product cards"""""

        self.logger.info(f'Fn get_cards_info has started')
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for link_product in links_product_cards:
                task = asyncio.create_task(self.get_id_brand(session=session, link_product_card=link_product, headers=headers))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self.logger.info(f'Fn get_cards_info has finished correctly')

    def collect_id_brand(self, checked_pages: list[str], headers: dict, prox: dict):
        """"Input: link to a page with category (meet, bread, etc.).
            Output: the function retrieves id and brand of all products using the function get_cards_info"""""

        product_cards = self.get_products_links(lst_links_pages=checked_pages, headers=headers, prox=prox)
        asyncio.run(self.get_cards_info(product_cards, headers))


class ParserDetail(ParserMetroMixin):

    products_detail = {}

    logger = init_logger(__name__)

    main_page = "https://online.metro-cc.ru"

    async def get_info_products(self, list_links_pages: list[str], headers: dict) -> None:
        """"Input: link to all pages with products.
            Output: the function retrieves names, prices, links of all products"""""

        self.logger.info(f'Fn get_info_products has started')

        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for link_page in list_links_pages:
                task = asyncio.create_task(self.get_info_product(session=session, link_page=link_page, headers=headers))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self.logger.info(f'Fn get_info_products has finished correctly')

    async def get_info_product(self, session, link_page: str, headers: dict) -> None:
            """"Input: link to a page with products.
                Output: the function retrieves name, price, link of a product"""""

            retry_options = ExponentialRetry(attempts=5)
            retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, client_session=session, start_timeout=1.5)

            async with retry_client.get(url=link_page, headers=headers) as response:
                resp = await response.text()
                soup = BeautifulSoup(resp, "lxml")

                # check if products in stock
                if self.check_instock_page(soup):

                    # Get and save products
                    try:
                        # Get products names
                        lst_title = soup.find_all("span", class_="product-card-name__text")
                        titles = [t.text.strip() for t in lst_title]
                        print('titles', titles)
                        # Get products prices
                        actual_prices = soup.find_all("div", class_="product-unit-prices__actual-wrapper")
                        actual_prices = [unidecode.unidecode(p.find("span", class_="product-price__sum-rubles").text.strip()) for p in actual_prices]
                        print('actual_prices', actual_prices)
                        # Get products prices
                        old_prices = soup.find_all("div", class_="product-unit-prices__old-wrapper")
                        old_prices = [unidecode.unidecode(p.get_text(strip=True)).rstrip("d/sht") for p in old_prices]
                        print('old_prices', old_prices)
                        # Get products links
                        all_links = soup.find_all("a", class_="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card")
                        all_links = [self.main_page + p["href"] for p in all_links]
                        print('all_links', all_links)

                        for i in range(len(titles)):
                            key = titles[i]
                            self.products_detail[key] = {}
                            self.products_detail[key]['actual_price'] = actual_prices[i]
                            self.products_detail[key]['old_price'] = old_prices[i]
                            self.products_detail[key]['link'] = all_links[i]

                    except Exception as ex:
                        self.logger.warning(f'Fn get_info_product. Failed to retrieve products titles, prices, links. Message error: {ex}')


    def collect_info_cards(self, checked_pages: list[str], headers: dict) -> None:
        """"Input: link to a page with category (meet, bread, etc.).
            Output: the function retrieves names, prices, links of all products using the function get_info_products"""""

        asyncio.run(self.get_info_products(list_links_pages=checked_pages, headers=headers))
