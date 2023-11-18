import requests
from bs4 import BeautifulSoup
import pandas as pd
import unidecode
import asyncio
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from headers import headers
from fake_useragent import UserAgent
import csv

def save_error(name_file, message_error):
    with open(f"{name_file}.txt", "r") as file:
        file.writelines(message_error)

class Parser:

    file = pd.DataFrame()

    main_page = "https://online.metro-cc.ru"

    lst_all_brands = []
    lst_all_id = []
    lst_all_titles = []
    lst_all_actual_prices = []
    lst_all_old_prices = []
    lst_all_links = []

    @staticmethod
    def check_count(lst_goods):
        if len(lst_goods) < 100:
            return True
        else:
            raise Exception

    def make_file(self, name_file):
        with open(f'{name_file}.csv', 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'id', 'Название', 'Цена со скидкой', 'Цена без скидки','Брэнд', 'Ссылка'])

    def get_pages_url(self, url: str) -> list[str]:
        """"Функция принимает главную страницу, потом собирает с нее ссылки на все оставшиеся страницы. Возвращает список со страницами"""""
        lst_links_pages = []
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            lst_links = soup.find('ul', class_="catalog-paginate v-pagination").find_all('a', class_="v-pagination__item catalog-paginate__item")
            lst_links_pages = [link.text for link in lst_links]
            last_page = int(lst_links_pages[-1])

            for num_page in range(1, last_page + 1):
                if num_page < 2:
                    """"Получаем первую страницу"""""
                    link_page = self.main_page + "/category/chaj-kofe-kakao/kofe?from=under_search&in_stock=1"
                    lst_links_pages.append(link_page)
                else:
                    """"Получаем все остальные страницы"""""
                    link_page = self.main_page + f"/category/chaj-kofe-kakao/kofe?from=under_search&in_stock=1&page={num_page}"
                    lst_links_pages.append(link_page)
        else:
            return response.status_code

        lst_links_pages = [link for link in lst_links_pages if not link.isdigit()]

        return lst_links_pages


    def get_goods_url(self, lst_links_pages: list[str]) -> list[str]:
        """"Функция принимает список со страницами и возвращает список с ссылками на товары"""""
        lst_all_goods = []
        for page_link in lst_links_pages:
            response = requests.get(url=page_link)
            if response.status_code == 200:

                soup = BeautifulSoup(response.text, "lxml")
                lst_links = soup.find_all('a', class_="product-card-photo__link reset-link")
                lst_goods = [self.main_page + link["href"] for link in lst_links]
                for good in lst_goods:
                    lst_all_goods.append(good)
            else:
                return response.status_code
        return lst_all_goods


    def get_title_price(self, lst_links_pages):
        """"Функция принимает список со страницами и возвращает словари с ключами title, actual_price, old_price, link, словари записываются в файл"""""

        for link_page in lst_links_pages:
            response = requests.get(url=link_page)
            soup = BeautifulSoup(response.text, "lxml")
            try:
                lst_title = soup.find_all("span", class_="product-card-name__text")
                titles = [t.text.strip() for t in lst_title]
                self.lst_all_titles.extend(titles)
            except Exception as ex:
                save_error("errors", f"titles {str(self.get_title_price.__name__)} {str(ex)}")
            try:
                act_pr = []
                actual_prices = soup.find_all("div", class_="product-unit-prices__actual-wrapper")
                # for price in actual_prices:
                #     pr = unidecode.unidecode(price.find("span", class_="product-price__sum-rubles").text.strip())
                #     act_pr.append([p for p in pr if p.isdigit()])
                actual_prices = [unidecode.unidecode(p.find("span", class_="product-price__sum-rubles").text.strip()) for p in actual_prices]
                self.lst_all_actual_prices.extend(actual_prices)

            except Exception as ex:
                save_error("errors", f"actual_prices {str(self.get_title_price.__name__)} {str(ex)}")

            try:
                old_pr = []
                old_prices = soup.find_all("div", class_="product-unit-prices__old-wrapper")
                # for price in old_prices:
                #     pr = unidecode.unidecode(price.get_text(strip=True))
                #     old_pr.append([i for i in pr if i.isdigit() or i == ''])
                old_prices = [unidecode.unidecode(p.get_text(strip=True)).rstrip("d/sht") for p in old_prices]
                # print(old_pr)
                self.lst_all_old_prices.extend(old_prices)

            except Exception as ex:
                save_error("errors", f"old_prices {str(self.get_title_price.__name__)} {str(ex)}")
            try:
                all_links = soup.find_all("a", class_="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card")
                all_links = [self.main_page + p["href"] for p in all_links]
                self.lst_all_links.extend(all_links)
            except Exception as ex:
                save_error("errors", f"all_links {str(self.get_title_price.__name__)} {str(ex)}")

        #self.file.to_csv(r"C:\Parser_Metro\parser\data2.csv")

    async def get_info(self, session, link_good, headers):
        """"Функция принимает ссылку на карточку с товаром и возвращает словарь с ключами id, title, brand"""""
        retry_options = ExponentialRetry(attempts=5)
        retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, client_session=session, start_timeout=0.5)
        async with retry_client.get(url=link_good, headers=headers) as response:
            if response.ok:
                resp = await response.text()
                link_card = BeautifulSoup(resp, 'lxml')

                # Получаем id
                id = link_card.find('p', class_='product-page-content__article').get_text(strip=True)
                self.lst_all_id.append(id.split(":")[1])

                # Получаем брэнд
                brand = link_card.find('a', class_='product-attributes__list-item-link reset-link active-blue-text').get_text(strip=True)
                self.lst_all_brands.append(brand)

    async def main_parser(self, list_link, name_file_save):

        ua = UserAgent()
        fake_ua = {'user-agent': ua.random}

        async with aiohttp.ClientSession(headers=fake_ua) as session:
            tasks = []
            for link in list_link:
                task = asyncio.create_task(self.get_info(session=session, link_good=link, headers=fake_ua))
                tasks.append(task)
            await asyncio.gather(*tasks)

        self.file["id"] = pd.Series(self.lst_all_id)
        self.file["Название"] = pd.Series(self.lst_all_titles)
        self.file["Цена со скидкой"] = pd.Series(self.lst_all_actual_prices)
        self.file["Цена без скидки"] = pd.Series(self.lst_all_old_prices)
        self.file["Бренд"] = pd.Series(self.lst_all_brands)
        self.file["Ссылка"] = pd.Series(self.lst_all_links)

        self.file.to_csv(rf"C:\Parser_Metro\parser\{name_file_save}.csv", index=False)

