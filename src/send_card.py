from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from private_conf import chrome_binary_location

import time
import traceback


import os


class CardSender:
    url = 'https://ankiweb.net/account/login'

    def __init__(self, username, password, card_type):
        self.driver = None

        self.last_access = time.time()

        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920x1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        options.binary_location = chrome_binary_location

        self.driver = webdriver.Chrome(chrome_options=options)

        self.driver.set_window_size(1920, 1080)
        self.driver.get(CardSender.url)
        usr_box = self.driver.find_element_by_id('email')
        usr_box.send_keys(username)
        pass_box = self.driver.find_element_by_id('password')
        pass_box.send_keys('{}\n'.format(password))
        self.card_type = card_type

    def send_card(self, front, back, deck, tags):
        ret = None
        try:
            # Click on the "Add" tab
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="navbarSupportedContent"]/ul[1]/li[2]/a')))
            self.driver.find_element_by_xpath(
                            '//*[@id="navbarSupportedContent"]/ul[1]/li[2]/a').click()

            # Wait for all the elements used to appear
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, 'models')))
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, 'deck')))
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, 'f0')))
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, 'f1')))

            select = Select(self.driver.find_element_by_id('models'))
            if self.card_type:
                try:
                    select.select_by_visible_text(self.card_type)
                except:
                    ret = 'The card type ```{}``` could not be found, so I am using the default Basic card type. Consider changing the /cardtype to the default value (by sending /cardtype twice) or to another card type that exists in your Anki'.format(self.card_type)
                    self.card_type = ""

            if not self.card_type:
                # Card type = Basic
                try:
                    select.select_by_visible_text("Basic")
                except:
                    for option in select.options: #iterate over the options, place attribute value in list
                        if "Basic" in option.text:
                            select.select_by_visible_text(option.text)
                            break

            # Select deck type (previously we could write here)
            try:
                select = Select(self.driver.find_element_by_id('deck'))
                select.select_by_visible_text(deck)
            except NoSuchElementException:
                raise NoDeckFoundError(deck)

            if tags:
                self.driver.find_element_by_id('f-1').send_keys(tags)

            # Fill fields
            self.driver.find_element_by_xpath('//*[@id="f0"]').send_keys(front)
            self.driver.find_element_by_id('f1').send_keys(back)

            # Add
            self.driver.find_element_by_xpath(
                    '/html/body/main/p/button').click()
        except:
            print(traceback.format_exc())
            if not os.path.isfile('screenshot_error.png'):
                self.driver.save_screenshot("screenshot_error.png")
            raise
        return ret


class NoDeckFoundError(Exception):
    def __init__(self, deck):
        self.deck = deck

if __name__ == "__main__":
    cs = CardSender('aaa@gmail.com', 'mypassword')
    cs.send_card('xoxoxo', ':)', 'Vocabulary')
