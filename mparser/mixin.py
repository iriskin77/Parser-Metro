import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from mparser.logs.logg import init_logger

class ParserMetroMixin:

    logger = init_logger(__name__)

    def make_request(self, url: str, headers: dict, prox: dict):
        adapter = HTTPAdapter(max_retries=4)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(url=url, headers=headers, timeout=40, proxies=prox)

        if response.status_code == 200:
            return response, response.status_code
        return None, response.status_code

    def get_pages_url(self, url: str, headers: dict, prox: dict):
        """"Input: link to a page with category (meet, bread etc.).
            Output: the function returns a list with pages"""""

        self.logger.info(f'Fn get_pages_url has started')
        lst_links_pages = []

        try:
            response, resp_status = self.make_request(url=url, headers=headers, prox=prox)
        except:
            response, resp_status = self.make_request(url=url, headers=headers, prox=prox)

        if resp_status == 200:
            self.logger.info(f'Fn get_pages_url Success to connect')

            soup = BeautifulSoup(response.text, "lxml")
            lst_links = soup.find('ul', class_="catalog-paginate v-pagination").find_all('a', class_="v-pagination__item catalog-paginate__item")
            lst_links_pages = [link.text for link in lst_links]
            last_page = int(lst_links_pages[-1])

            for num_page in range(1, last_page + 1):
                if num_page < 2:
                    # Get the first page
                    link_page = url
                    lst_links_pages.append(link_page)
                else:
                    # Get other pages
                    link_page = url + f"?page={num_page}"
                    lst_links_pages.append(link_page)

            lst_links_pages = [link for link in lst_links_pages if not link.isdigit()]
            self.logger.info(f'Fn get_pages_url has finished correctly')
            return lst_links_pages

        else:
            self.logger.critical(f'Fn get_pages_url has finished incorrectly. Bad request: {resp_status}')

    def check_instock_page(self, soup: BeautifulSoup) -> bool:

        goods = soup.find_all("p", class_="product-title catalog-2-level-product-card__title style--catalog-2-level-product-card")
        check_goods = [i.text for i in goods]
        if check_goods == []:
            return True
        return False

