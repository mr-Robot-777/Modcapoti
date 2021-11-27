import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint

url = 'https://www.hh.ru'

post = input('Введите искомую должность: ')
pages = int(input('Введите требуемое количество страниц с результатами поиска: '))

params = {'clusters': 'true',
          'area': '1',
          # 'no_magic': 'true',
          'ored_clusters': 'true',
          'enable_snippets': 'true',
          # 'salary': '',
          'text': post,
          'page': 0,
          }

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

vacancy_list = []

for i in range(pages):
    response = requests.get(url + '/search/vacancy/', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
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
                    salary_min, salary_max, salary_money = salary_min.replace(u"\u202f", ''), salary_max.replace(u"\u202f", ''), salary_money
                case (no_need, comp, salary_money) if no_need == 'от':
                    salary_min, salary_max, salary_money = int(comp.replace(u"\u202f", '')), None, salary_money
                case (no_need, comp, salary_money) if no_need == 'до':
                    salary_min, salary_max, salary_money = None, int(comp.replace(u"\u202f", '')), salary_money

        except:
            salary_min = None
            salary_max = None
            salary_money = None

        vacancy_data['vacancy'] = name
        vacancy_data['link'] = link
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_money'] = salary_money
        vacancy_data['site'] = url

        vacancy_list.append(vacancy_data)

    params['page'] += 1


with open('vacancy.json', 'w', encoding='utf-8') as f:
    json.dump(vacancy_list, f, ensure_ascii=False)
    pprint(vacancy_list)
