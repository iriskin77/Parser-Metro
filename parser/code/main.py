from parser import Parser
import asyncio



def main():

    url_moscow = "https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search&in_stock=1"
    url_saint_petersbourg = "https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search&in_stock=1"

    obj = Parser()

    """"Создаем файл, куда будем сохранять данные"""""

    obj.make_file("data_saint_petersbourg")

    """"Получаем список из страниц"""""
    lst_pages = obj.get_pages_url(url_saint_petersbourg)

    """"Получаем список Название, цену, ссылку на товар, они сохраняются в памяти в объекте класса"""""
    obj.get_title_price(lst_pages)

    """"Получаем список ссылок на каждый товар"""""

    lst_goods = obj.get_goods_url(lst_pages)

    """"Собираем id и брэнд с каждой карточки """""

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(obj.main_parser(lst_goods, "data_saint_petersbourg"))

if __name__ == '__main__':
    main()

