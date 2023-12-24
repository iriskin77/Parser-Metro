## Описание задания

Hard. Написать парсер для сайта Метро (https://online.metro-cc.ru/)

Для каждой торговой площадки требования одни и те же. 
Спарсить любую категорию, где более 100 товаров и выгрузить в любой удобный формат(csv, json, xlsx). 
Важно, чтобы товары были в наличии.

Необходимые данные: 

id товара из сайта/приложения, 
наименование, 
ссылка на товар, 
регулярная цена, 
промо цена, 
бренд.

## Как установить

+ Клонировать репохитория 

+ Установить и активировать виртуальное окружение:
  + python -m venv venv
  + .\venv\Scripts\activate (windows)
  + source venv/biv/activate (linux)

+ Установить необходимые зависимости: pip install -r requirements.txt

+ Добавить свои прокси, потому что срок действия прокси из проекта уже
  скорее всего истек :3


## Как работает парсер


![](https://github.com/iriskin77/Habr_parser_api/blob/master/images/ParserMetro.png)

Парсер состоит из четырех классов: ParserMetroMixin ParserMetro ParserIdBrand ParserDetail

Парсер работает следующим образом:

Парсер циклический: запускается каждые 24 часа.

Класс ParserIdBrand отвечает за сбор Id и Brand товара. Класс ParserDetail отвечает за сбор названия, цены, ссылки товара. 
В классе ParserMetro данные собираются в формат json и записываются в файл. Визуально это выглядит следующим образом:

```json


    "Набор подарочный M&M's кондитерский Сани, 280г": {
        "id": 226825,
        "brand": "M&M'S",
        "actual_price": "349",
        "old_price": "489",
        "link": "https://online.metro-cc.ru/products/280g-podarochnyy-konditerskiy-nabor-mms-sani"
    },
    "Подарок новогодний Объединенные кондитеры Веселая карусель, 800г": {
        "id": 653474,
        "brand": "ОБЪЕДИНЕННЫЕ КОНДИТЕРЫ",
        "actual_price": "599",
        "old_price": "959",
        "link": "https://online.metro-cc.ru/products/novogodnij-podarok-veselaya-karusel-obedinennye-800g"
    },
    "Набор подарочный M&M's кондитерский посылка, 150г": {
        "id": 226822,
        "brand": "M&M'S",
        "actual_price": "169",
        "old_price": "221",
        "link": "https://online.metro-cc.ru/products/150g-podarochnyy-konditerskiy-nabor-mms-posylka"
    },
```



## Проблемы и ограничения:

+ Нет удобного интерфейса через cli (argspars) или через django-admin, посредством чего можно было бы
  удобно, например, добавлять категории для парсинга (сейчас там ссылка только на категорию сладостей), 
  или, скажем, изменять время обхода, или добавлять/удалять прокси и проч.

+ Данные не сохраняются ни в какую БД, только в файл json.

## Что можно было бы улучшить

+ Добавить интерфейс

+ Добавить БД (sqllite/postgre)

+ Добавить Docker


