#!/usr/bin/env python
# coding: utf-8

# In[120]:


from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import requests
from pprint import pprint


# In[121]:


def hh(find_vacancy):

    vacancy = []

    url = 'https://hh.ru/search/vacancy'

    params = {'area':'', 'fromSearchLine':'true', 'st':'searchVacancy', 'text': find_vacancy, 'from':'suggest_post', 'page':''}

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)         Chrome/90.0.4430.93 Safari/537.36'}

    response = requests.get(url, params = params, headers = headers)

    if response.ok:
        dom = bs(response.text, 'html.parser')
        page_block = dom.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            last_page = '1'
        else:
            last_page = int(page_block.find('a', {'data-qa': 'pager-next'}).find_previous('a').getText()) - 1

    for page in range(0, last_page):
        params['page'] = page
        response = requests.get(url, params = params, headers = headers)

        if response.ok:
            dom = bs(response.text, 'html.parser')

            vacancy_field = dom.find('div', {'data-qa': 'vacancy-serp__results'}).find_all('div', {'class': 'vacancy-serp-item'})

            for field in vacancy_field:
                vacancy.append(vacancy_parser_hh(field))

    return vacancy


# In[122]:


def vacancy_parser_hh(field):
    vacancy = {}
    
    vacancy_name = field.find('a', {'data-qa':'vacancy-serp__vacancy-title'}).getText()
        
    city = field.find('span', {'class': 'vacancy-serp-item__meta-info'}).getText().split(', ')[0]
    
    vacancy_link = field.find('a', {'data-qa':'vacancy-serp__vacancy-title'})['href']
    
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


# In[123]:


def super_job(find_vacancy):

    vacancy = []

    url = 'https://www.superjob.ru/vacancy/search'

    params = {'keywords':find_vacancy, 'noGeo':'1', 'page':''}
    
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)         Chrome/90.0.4430.93 Safari/537.36'}

    response = requests.get(url, params = params, headers = headers)

    if response.ok:
        dom = bs(response.text, 'html.parser')
        page_block = dom.find('div', {'class': '_3zucV L1p51 _1Fty7 _2tD21 _3SGgo'})
        if not page_block:
            last_page = '1'
        else:
            last_page = int(page_block.find('a', {'class': 'icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe'}).find_previous('a').getText())

    for page in range(1, last_page):
        params['page'] = page
        response = requests.get(url, params = params, headers = headers)

        if response.ok:
            dom = bs(response.text, 'html.parser')

            vacancy_field = dom.find('div', {'class': 'iJCa5 _1LlO2 X7voU _2nteL'}).find_all('div', {'class': 'iJCa5 f-test-vacancy-item _1fma_ _2nteL'})

            for field in vacancy_field:
                vacancy.append(vacancy_parser_superjob(field))

    return vacancy


# In[124]:


def vacancy_parser_superjob(field):
    vacancy = {}
    url = 'https://www.superjob.ru/vacancy/search'
    
    vacancy_name = field.find('div', {'class':'_1h3Zg _2rfUm _2hCDz _21a7u'}).find_next('a').getText()
    
    city = field.find('span', {'class': '_1h3Zg f-test-text-company-item-location e5P5i _2hCDz _2ZsgW'}).findChildren()[2].getText().split(',')[0]
    
    vacancy_link = url + field.find('div', {'class':'_1h3Zg _2rfUm _2hCDz _21a7u'}).find_next('a')['href']
    
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
    
    #vacancy['ne'] = salary
    vacancy['name'] = vacancy_name
    vacancy['city'] = city
    vacancy['salary_min'] = salary_min
    vacancy['salary_max'] = salary_max
    vacancy['salary_currency'] = salary_currency
    vacancy['link'] = vacancy_link
    vacancy['site'] = 'superjob.ru'
   
        
    return vacancy    


# In[125]:


def vacancy_parser(find_vacancy):
        
    vacancy = []
    vacancy.extend(hh(find_vacancy))
    vacancy.extend(super_job(find_vacancy))
    
    df = pd.DataFrame(vacancy)

    return df



# In[126]:


find_vacancy = 'Python'
df = vacancy_parser(find_vacancy)


# In[127]:


pprint(df)


# In[ ]:




