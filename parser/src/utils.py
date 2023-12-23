import requests
from .logg import init_logger
from bs4 import BeautifulSoup


class ParserMetroMixin:

    logger = init_logger(__name__)

    def get_pages_url(self, url: str, headers) -> list[str] | int:
        """"Input: link to a page with category (meet, bread etc.).
            Output: the function returns a list with pages"""""
        self.logger.info(f'Fn {self.get_pages_url.__name__} has started')
        lst_links_pages = []
        try:
            response = requests.get(url, headers=headers, timeout=60)
            self.logger.info(f'Fn {self.get_pages_url.__name__} Success to connect')
        except:
            response = requests.get(url, headers=headers, timeout=60)
            self.logger.info(f'Fn {self.get_pages_url.__name__} Failed to connect. Waiting for to retry connection')

        if response.status_code == 200:
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
        else:
            self.logger.critical(f'Fn {self.get_pages_url.__name__} has finished correctly')
            return response.status_code

        lst_links_pages = [link for link in lst_links_pages if not link.isdigit()]
        self.logger.info(f'{self.get_pages_url.__name__} has finished correctly')
        return lst_links_pages

    def check_instock(self, links_pages: list[str], headers) -> list[str]:
        """"Input: links to pages with product cards.
            Output: the function returns a list of links with pages that have only products in stock"""""
        pages_instock = []

        for page in links_pages:

            try:
                response = requests.get(url=page, headers=headers, timeout=20)
            except:
                response = requests.get(url=page, headers=headers, timeout=20)

            soup = BeautifulSoup(response.text, "lxml")
            goods = soup.find_all("p", class_="product-title catalog-2-level-product-card__title style--catalog-2-level-product-card")
            check_goods = [i.text for i in goods]
            #print('CHECK GOODS FROM check_instock', goods)

            if check_goods == []:
                pages_instock.append(page)
                #print('if check_goods == []: PAGES_INSTOCK', pages_instock)
            else:
                #print('else PAGES_INSTOCK', pages_instock)
                return pages_instock
        #return pages_instock
