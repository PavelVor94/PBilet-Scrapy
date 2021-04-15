<H1>PBilet проект содержит два паука Scrapy</H2>
  <li>PEvents - для извлечения данных о всех мероприятиях</li>
  <li>PBilets - для извлечения данных о доступных билетах для конкретного мероприятия</li>

<BR>
<BR>


<H2>установка необходимых библиотек pip install -r requirements.txt</H2>

<BR>
<BR>


<H3>запуск пауков(необходимо находиться в папке проекта Scrapy):</H3>
  <H4>PEvents необходима передача одного аргумента -o с названием выходного файла, например:</H4>
      <li>scrapy crawl PEvents -o events.csv</li>

<BR>
<BR>


  <H4>PBilets нужно передать аргумент -a url="ссылка на страницу мероприятия" и -o с названием выходного файла, например:</H3>
      <li>scrapy crawl PBilets -a url=https://tula.planzala.ru/event/mgzavrebi-hronologiya -o tickets.csv</li>
      <li>scrapy crawl PBilets -a url=https://tula.planzala.ru/event/otel-zhelanij -o tickets1.csv</li>
<BR>
пожалуйста не используйте одинарные ковычки при передачи url, или двойные или вообще без ковычек.

      
