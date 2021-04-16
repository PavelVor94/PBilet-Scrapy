import scrapy
from lxml import html
from io import StringIO
from datetime import datetime

class PeventsSpider(scrapy.Spider):
    name = 'PEvents'
    start_urls = ['https://tula.planzala.ru/']
    BASE_URL = 'https://tula.planzala.ru'
    months = {'января' : "01" ,
              "февраля" : "02" ,
              "марта":"03" ,
              "апреля":"04",
              "мая":"05",
              "июня":"06",
              "июля":"07",
              "августа": "08",
              "сентября": "09",
              "октября" : "10",
              "ноября": "11",
              "декабря":"12" }
    added = []

    """Я понимаю, что решение делать словарь месяцев для даты не самое лучшее, но к сожелению datetime может преобразовать русские месяца только если они в именительном падеже,
    у нас же здесь в родительном. но что что, а ubuntu 20.10 спокойно их преобразовала, и даже не заметила не угодный падеж, но к сожелению windows так не может,
    можно было установить PyICU, но на windows она тоже встает только с бубном, а я не знаю какая у вас ОС. Поэтому пришлось делать более универсальное решение, пусть и не красивое."""


    def parse(self, response):
        """Загрузка главной страницы и получение всех категорий"""

        page = html.parse(StringIO(response.text))
        categories = page.xpath('//div[@class="site_header_menu_block_item"]/a')

        for category in categories:
            # формируем ссылки на категорию и переходим по ней для извлечения нужных данных, в meta кидаем название категории
            yield  scrapy.Request(self.BASE_URL+category.attrib['href'], callback=self.load_category, meta={'category' : category.text})


    def load_category(self, response):
        """Загрузка категории и получение необходимых данных"""

        page = html.parse(StringIO(response.text))

        # получаем необходимые нам списки элементов.
        dates_events = page.xpath('//div[@class="tickets_list_block_info_column2_date"]/text()')[::2]
        times_events = page.xpath('//div[@class="tickets_list_block_info_column2_date"]/span/text()')
        place_events = page.xpath('//div[@class="tickets_list_block_info_column1_location"]/text()')
        category_events = response.meta['category']
        urls_events = page.xpath('//div[@class="tickets_list_block_info_column1_title"]/a')

        # перебор всех записей на странице, у нас много списков одинаковой длины, поэтому удобнее использовать индексирование.
        for (i, url_event) in enumerate(urls_events):

            # извлекаем дату и время из строк полученных со страницы, для дальнейшего преобразования в нужный нам формат
            tm = times_events[i].strip()[2:].strip()
            (day, month) = dates_events[i].strip()[:-1].split(' ')
            dt = datetime.strptime(f'{day} {self.months[month]} 2021 +{tm}', "%d %m %Y %H:%M")

            # если дата уже прошла. значит это мероприятие в следующем году. меняем год на 2022
            if datetime.now() > dt :
                dt = dt.replace(year=2022)

            # исключаем повторы проверяя на наличие в списке пройденных ссылок мероприятий
            if not url_event.attrib['href'] in self.added:
                yield {
                    'Название': urls_events[i].text.strip(),
                    'Дата и время': dt.strftime('%Y.%m.%d %H:%M'),
                    'Название площадки': place_events[i].strip(),
                    'Категория': category_events,
                    'Ссылка': self.BASE_URL + url_event.attrib['href']
                }

                # добавляем ссылку на мероприятие в список пройденных.
                self.added.append(url_event.attrib['href'])

        # получение ссылок на все страницы в категории, у scrapy есть встроенный фильтр, поэтому можно не бояться что мы зациклимся.
        pages = page.xpath('//div[@class="page_navigation_links_item2"]/a')
        for page in pages:
            yield scrapy.Request(self.BASE_URL + page.attrib['href'], callback=self.load_category, meta={'category': response.meta['category']})

