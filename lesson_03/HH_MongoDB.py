import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pymongo
from pymongo import MongoClient
from pymongo.errors import *

client = MongoClient('127.0.0.1', 27017)

db = client['HH_ru_vacancy']
HHvacancy = db.vacancy

HHvacancy.create_index([('vacancy', pymongo.TEXT)], name='search_index', unique=True)

url = 'https://www.hh.ru'

post = input('Введите искомую должность: ')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
params = {'clusters': 'true',
          'area': '1',
          # 'no_magic': 'true',
          'ored_clusters': 'true',
          'enable_snippets': 'true',
          # 'salary': '',
          'text': post,
          'page': 0,
          }

response = requests.get(url + '/search/vacancy/', params=params, headers=headers)
dom = BeautifulSoup(response.text, 'html.parser')

try:
    number_of_pages = dom.find_all('span', {'class': 'pager-item-not-in-short-range'})[-1].text
    print(f'С заданными условиями поиска найдено {number_of_pages} страниц вакансий.')
except:
    print('С заданными условиями поиска вакансий не найдено')
    sys.exit()

pages = int(input('Введите требуемое количество страниц с результатами поиска: '))

if pages > int(number_of_pages):
    print(f'Вы ввели количество страниц больше заданного. Поиск будет осуществлен на {number_of_pages} страницах')
    pages = int(number_of_pages)

new = 0
old = 0

vacancy_list = []

for i in range(pages):
    # response = requests.get(url + '/search/vacancy/', params=params, headers=headers)
    # dom = BeautifulSoup(response.text, 'html.parser')
    job_openings = dom.find_all('div', {'class', 'vacancy-serp-item vacancy-serp-item_premium'})

    for vacancy in job_openings:
        vacancy_data = {}
        name = vacancy.find('a')
        link = name.attrs.get('href')
        name = name.text
        try:
            salary = vacancy.find('div', {'class', 'vacancy-serp-item__sidebar'}).text
            list = salary.split(' ')
            match list:
                case (salary_min, _, salary_max, salary_money):
                    salary_min, salary_max, salary_money = int(salary_min.replace(u"\u202f", '')), int(
                        salary_max.replace(
                            u"\u202f", '')), salary_money
                case (no_need, comp, salary_money) if no_need == 'от':
                    salary_min, salary_max, salary_money = int(comp.replace(u"\u202f", '')), None, salary_money
                case (no_need, comp, salary_money) if no_need == 'до':
                    salary_min, salary_max, salary_money = None, int(comp.replace(u"\u202f", '')), salary_money

        except:
            salary_min = None
            salary_max = None
            salary_money = None

        block_with_hr_information = vacancy.find('div', {'class', 'vacancy-serp-item__meta-info-company'})
        try:
            hr_link = url + block_with_hr_information.find('a', {'class', 'bloko-link'})['href']
        except:
            hr_link = None

        vacancy_data['vacancy'] = name
        vacancy_data['link'] = link
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_money'] = salary_money
        vacancy_data['site'] = url

        try:
            HHvacancy.insert_one(vacancy_data)
            new += 1

        except DuplicateKeyError as double_error:
            old += 1
            # print('Doublicate: ', double_error)

    params['page'] += 1

price_salary = 120000

for search in HHvacancy.find({'$or': [{'salary_min': {'$gt': price_salary}}, {'salary_max': {'$gt': price_salary}}]}):
    pprint(search)

print(f'Добавлено {new} новых вакансий. Существующие {old} вакансий без изменений')
