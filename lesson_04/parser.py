from lxml import html
import requests
from pprint import pprint
from pymongo import *

client = MongoClient('127.0.0.1', 27017)
db = client['news_world']
news = db.news

url = 'https://lenta.ru'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

response = requests.get('https://lenta.ru/rubrics/russia/', headers=header)

dom = html.fromstring(response.text)

result_news = []
search_items = dom.xpath(".//div[contains(@class, 'item ')]")

for item in search_items:
    news_item = {}

    title = item.xpath(".//h3[@class='card-title']/text()")[0].replace("\xa0", "")
    link = url + item.xpath(".//a[@class='titles']/@href")[0]
    time = item.xpath(".//span[@class='time']/text()")[0]

    news_item['title'] = title
    news_item['link'] = link
    news_item['time'] = time

    news.insert_one(news_item)

for info in news.find({}):
    pprint(info)
