from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo_trends']
MvideoTrends = db.MvideoTrends

url = 'https://www.mvideo.ru/'

driver = webdriver.Firefox(executable_path='./geckodriver')
driver.get(url)

actions = ActionChains(driver)
actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN)
actions.perform()
driver.implicitly_wait(15)

contains = driver.find_element(By.XPATH, "//mvid-shelf-group[contains(@class, 'page-carousel-padding ng-star-inserted')]")
button = contains.find_element(By.XPATH, ".//button[contains(@class, 'tab')][2]")
button.click()

product_cards = driver.find_element(By.CSS_SELECTOR, 'mvid-product-cards-group')
names = product_cards.find_elements(By.CLASS_NAME, 'product-mini-card__name')
prices = product_cards.find_elements(By.CLASS_NAME, 'product-mini-card__price')
product_data = list(zip(names, prices))

result_list = []

for product in product_data:
    product_dict = {'name': product[0].text,
                    'link': product[0].find_element(By.XPATH, ".//a").get_attribute('href'),
                    'price': int(product[1].find_element(By.CLASS_NAME, 'price__main-value').text.replace(' ', ''))}
    result_list.append(product_dict)


for i in result_list:
    try:
        MvideoTrends.update_one({'link': i['link']}, {'$set': i}, upsert=True)
    except DuplicateKeyError as e:
        print(e)

driver.close()

for files in MvideoTrends.find():
    pprint(files)
