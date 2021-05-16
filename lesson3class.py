from bs4 import BeautifulSoup as bs
from pprint import pprint
from pymongo import MongoClient
import json
import re
import requests


class Les3Class():
    def __init__(self, name_db, name_collection):
        self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

        self.url_hh = 'https://hh.ru/search/vacancy'
        self.url_superjob = 'https://www.superjob.ru/vacancy/search'

        self.mongodb = MongoClient('localhost', 27017)
        self.db = self.mongodb[name_db]
        self.collection = self.db[name_collection]

    def find_salary(self, salary):
        job_opportunities = self.collection.find({'salary_max': {'$gt': salary}})
        for job in job_opportunities:
            pprint(job)

    def start_parsers(self, find_vacancy):
        self.hh(find_vacancy)
        self.super_job(find_vacancy)

    def get_response(self, url, params = None):
        response = requests.get(url, params = params, headers = self.headers)
        return response

    def get_dom(self, response):
        if response.ok:
            dom = bs(response.text, 'html.parser')
            return dom

    def last_page_hh(self, response):
        dom = self.get_dom(response)
        if dom:
            page_block = dom.find('div', {'data-qa': 'pager-block'})
            if not page_block:
                last_page = '1'
            else:
                last_page = int(page_block.find('a', {'data-qa': 'pager-next'}).find_previous('a').getText()) - 1
        return last_page

    def last_page_superjob(self, response):
        dom = self.get_dom(response)
        if dom:
            page_block = dom.find('div', {'class': '_3zucV L1p51 _1Fty7 _2tD21 _3SGgo'})
            if not page_block:
                last_page = '1'
            else:
                last_page = int(page_block.find('a', {
                    'class': 'icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe'}).find_previous(
                    'a').getText())
        return last_page

    def unique(self, name_field, list_values):
        return bool (self.collection.find_one({name_field: {'$in': [list_values]}}))

    def hh(self, find_vacancy):

        params = {'area': '', 'fromSearchLine': 'true', 'st': 'searchVacancy', 'text': find_vacancy,
                  'from': 'suggest_post', 'page': ''}

        response = self.get_response(self.url_hh, params)
        last_page = self.last_page_hh(response)

        for page in range(0, last_page):
            params['page'] = page
            response = self.get_response(self.url_hh, params)

            if response.ok:
                dom = self.get_dom(response)
                vacancy_field = dom.find('div', {'data-qa': 'vacancy-serp__results'}).find_all('div', {
                    'class': 'vacancy-serp-item'})
                for field in vacancy_field:
                    vacancy = self.vacancy_parser_hh(field)

                    if self.unique('link', vacancy['link']):
                        self.collection.update_one({'link': vacancy['link']}, {'$set': vacancy})
                    else:
                        self.collection.insert_one(vacancy)

    def vacancy_parser_hh(self, field):
        vacancy = {}
        vacancy_name = field.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()

        city = field.find('span', {'class': 'vacancy-serp-item__meta-info'}).getText().split(', ')[0]

        vacancy_link = field.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']

        salary = field.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText().replace('\u202f', '')
            salary = re.split(r'[ -]+', salary)
            if salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1])
            elif salary[0] == 'от':
                salary_min = int(salary[1])
                salary_max = None
            else:
                salary_min = int(salary[0])
                salary_max = int(salary[-2])

            salary_currency = salary[-1]

        vacancy['name'] = vacancy_name
        vacancy['city'] = city
        vacancy['salary_min'] = salary_min
        vacancy['salary_max'] = salary_max
        vacancy['salary_currency'] = salary_currency
        vacancy['link'] = vacancy_link
        vacancy['site'] = 'hh.ru'

        return vacancy

    def super_job(self, find_vacancy):

        params = {'keywords': find_vacancy, 'noGeo': '1', 'page': ''}

        response = self.get_response(self.url_superjob, params)
        last_page = self.last_page_superjob(response)

        for page in range(0, last_page):
            params['page'] = page
            response = self.get_response(self.url_superjob, params)

            if response.ok:
                dom = self.get_dom(response)

                vacancy_field = dom.find('div', {'class': 'iJCa5 _1LlO2 X7voU _2nteL'}).find_all('div', {
                    'class': 'iJCa5 f-test-vacancy-item _1fma_ _2nteL'})

                for field in vacancy_field:
                    vacancy = self.vacancy_parser_superjob(field)

                    if self.unique('link', vacancy['link']):
                        self.collection.update_one({'link': vacancy['link']}, {'$set': vacancy})
                    else:
                        self.collection.insert_one(vacancy)

    def vacancy_parser_superjob(self, field):
        vacancy = {}
        url = 'https://www.superjob.ru/vacancy/search'

        vacancy_name = field.find('div', {'class': '_1h3Zg _2rfUm _2hCDz _21a7u'}).find_next('a').getText()

        city = \
        field.find('span', {'class': '_1h3Zg f-test-text-company-item-location e5P5i _2hCDz _2ZsgW'}).findChildren()[
            2].getText().split(',')[0]

        vacancy_link = url + field.find('div', {'class': '_1h3Zg _2rfUm _2hCDz _21a7u'}).find_next('a')['href']

        salary = field.find('span', {'class': '_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW'})

        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText().replace('\u00a0', ' ')
            salary = re.split(r'[ —]+', salary)
            if salary[0] == 'По':
                salary_min = None
                salary_max = None
                salary_currency = None
            elif salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1] + salary[2])
                salary_currency = salary[-1]
            elif salary[0] == 'от':
                salary_min = int(salary[1] + salary[2])
                salary_max = None
                salary_currency = salary[-1]
            elif len(salary) < 4:
                salary_min = int(salary[0] + salary[1])
                salary_max = int(salary[0] + salary[1])
                salary_currency = salary[-1]
            else:
                salary_min = int(salary[0] + salary[1])
                salary_max = int(salary[2] + salary[3])
                salary_currency = salary[-1]

        # vacancy['ne'] = salary
        vacancy['name'] = vacancy_name
        vacancy['city'] = city
        vacancy['salary_min'] = salary_min
        vacancy['salary_max'] = salary_max
        vacancy['salary_currency'] = salary_currency
        vacancy['link'] = vacancy_link
        vacancy['site'] = 'superjob.ru'

        return vacancy





