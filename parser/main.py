from parser import Parser
import asyncio



def main():

    url = "https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search"

    obj = Parser()

    """"Создаем файл, куда будем сохранять данные"""""

    obj.make_file("data")

    """"Получаем список из страниц"""""
    lst_pages = obj.get_pages_url(url)

    """"Получаем список Название, цену, ссылку на товар, они сохраняются в памяти в объекте класса"""""
    obj.get_title_price(lst_pages)

    """"Получаем список ссылок на каждый товар"""""

    lst_goods = obj.get_goods_url(lst_pages)

    """"Собираем id и брэнд с каждой карточки """""

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(obj.main_parser(lst_goods, "data"))

if __name__ == '__main__':
    main()

