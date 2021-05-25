from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from pymongo import MongoClient

mongodb = MongoClient('localhost', 27017)
db = mongodb['db_mail']
collection = db.mail

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://mail.ru/')

elem = driver.find_element_by_name('login')
elem.send_keys('study.ai_172')
elem.send_keys(Keys.ENTER)

time.sleep(2)
elem = driver.find_element_by_name('password')
elem.send_keys('NextPassword172!')
elem.send_keys(Keys.ENTER)

# Сработал один раз ...
# field = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
# field = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.NAME, 'password')))
# field.send_keys('NextPassword172!')
# field.send_keys(Keys.ENTER)

time.sleep(2)
mail_list = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
# link1 = []
# for i in mail_list:
#     a = i.get_attribute('href')
#     link1.append(a)
link = list(map(lambda adress: adress.get_attribute('href'), mail_list))

all_link = set()
all_link = all_link.union(set(link))

while True:
    actions = ActionChains(driver)
    actions.move_to_element(mail_list[-1])
    actions.perform()

    time.sleep(5)
    mail_list = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    link = list(map(lambda adress: adress.get_attribute('href'), mail_list))

    if link[-1] not in all_link:
        all_link = all_link.union(set(link))
    else:
        break


for i in list(all_link):
    mail={}
    driver.get(i)
    time.sleep(3)
    mail['send'] = driver.find_element_by_class_name('letter-contact').get_attribute('title')
    mail['date'] = driver.find_element_by_class_name('letter__date').text
    mail['title'] = driver.find_element_by_xpath('//h2').text
    mail['body'] = driver.find_element_by_class_name('letter-body').text

    collection.insert_one(mail)














# for m in mail_list:
#     print(m)
# for m in mail_list:
#     print(m.find_element_by_xpath("//a[contains(@class, 'js-tooltip-direction_letter-bottom')]").get_attribute('data-id'))

# mail_list = driver.find_elements_by_class_name('llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal')
# print(len(mail_list))
# for m in mail_list:
#     print(m.find_element_by_class_name('llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal').get_attribute('href'))
