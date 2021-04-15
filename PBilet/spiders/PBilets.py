import scrapy
from lxml import html
from io import StringIO
import requests


class PbiletsSpider(scrapy.Spider):
    name = 'PBilets'
    URL_MAP = 'https://tula.planzala.ru/ajax/get/sector/map?id='
    URL_INFO = 'https://tula.planzala.ru/ajax/get/sector/info?date=IDEVENT&sector='
    def __init__(self, url = None, *args, **kwargs):
        super(PbiletsSpider, self).__init__(*args, **kwargs)
        self.start_urls=[url]

    def parse(self, response):
        """загрузка страницы мероприятия и получения всех необходимых данных"""

        page = html.parse(StringIO(response.text))

        # получения названия секторов, начальных цен(они будут нужны для билетов без мест), и кнопок для покупки билетов
        sectors = page.xpath('//td[@class="action_tickets_item_info_list_c_line_name_td"]/text()')
        begin_prices = page.xpath('//td[@class="action_tickets_item_info_list_c_line_price_td"]/span/text()')
        buttons = page.xpath('//td[@class="action_tickets_item_info_list_c_line_button_td"]/div')

        # проходим по всем интересующим нас элементам, списки одинаковой длины поэтому используем индексирование
        for (i, sector) in enumerate(sectors):
            # проверяем имеет ли кнопка атррибут необходимый для открытия карты, если нет значит она для билетов без мест(танцпол, входной билет и т.д.)
            if buttons[i].attrib.get('data-sector-id'):
                # формируем строку для получения JSON из аттрибутов кнопок, и извлекаем нужные нам словари.
                info = requests.get(self.URL_INFO.replace('IDEVENT', buttons[i].attrib['data-date-id']) + buttons[i].attrib['data-sector-id']).json()
                tickets = info['tickets']
                prices = info['prices']

                # загружаем и разбираем карту посадочных мест
                map = html.etree.fromstring(requests.get(self.URL_MAP + buttons[i].attrib['data-sector-id']).content)

                for ticket in tickets:
                    # получаем цену по id билета и id цены из словарей JSON
                    price = prices[str(tickets[ticket][1])][0]

                    # находим элемент места на карте посадочных мест по id билета
                    seat = map.xpath(f"//*[@data-seat-id='{ticket}']")[0]

                    yield {
                        "Сектор": sector,
                        "Ряд": seat.attrib['data-row-num'],      # аттрибут указывающий на номер ряда на карте
                        'место': seat.attrib['data-seat-num'],   # аттрибут указывающий на номер места на карте
                        "Цена": price
                    }
            else:
                # кнопка не имела аттрибутов для открытия карты, значит это билеты без мест
                yield {
                    "Сектор": sector,
                    "Ряд": '',
                    'место': '',
                    "Цена": begin_prices[i]
                }

