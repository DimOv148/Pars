import json
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
db = mongodb['db_mv']
collection = db.mv

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')

block = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')]/following:: div[@class = 'gallery-content accessories-new ']")

actions = ActionChains(driver)
actions.move_to_element(block)
actions.perform()

button = block.find_element_by_xpath("//h2[contains(text(), 'Новинки')]/following :: div[3]/child:: a[contains(@class, 'next-btn')]")
for i in range(8):
    prod = block.find_elements_by_xpath(".//a[@class = 'fl-product-tile-picture fl-product-tile-picture__link']")
    temp_list = list(map(lambda x: x.get_attribute('data-product-info'), prod))
    temp_list = set(temp_list)
    button.click()
    time.sleep(3)
temp_lst = list(set(temp_list))
for i in temp_lst:
    i = i.replace("\n''\t\t\t\t\t", '')
    try:
        i = json.loads(i)
        collection.insert_one(i)
    except Exception:
        continue

