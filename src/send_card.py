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
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@autocomplete="username"]')))
        usr_box = self.driver.find_element_by_xpath('//input[@autocomplete="username"]')
        usr_box.send_keys(username)
        pass_box = self.driver.find_element_by_xpath('//input[@autocomplete="current-password"]')
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
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/main/form/button')))

            # This is the card type
            type_elem = self.driver.find_element_by_xpath('/html/body/div/main/div[1]/div/div/div[2]/input')
            type_elem.click()
            if self.card_type:
                try:
                    type_elem.send_keys(self.card_type + '\n')
                    if type_elem.get_attribute('value'): # It it was succesful the selectable returns empty string
                        raise NoCardTypeFoundError(deck)
                            # throw exception if there is nothing
                except:
                    ret = 'The card type ```{}``` could not be found, so I am using the default Basic card type. Consider changing the /cardtype to the default value (by sending /cardtype twice) or to another card type that exists in your Anki'.format(self.card_type)
                    self.card_type = ""

            if not self.card_type:
                # Card type = Basic
                type_elem.send_keys("Basic\n")
                # TODO click on the first one if there is no Basic although
                # there should always be Basic, right?

            # Select deck type (previously we could write here)
            deck_elem = self.driver.find_element_by_xpath('/html/body/div/main/div[2]/div/div/div[2]/input')
            deck_elem.click()
            deck_elem.send_keys(deck+'\n')
            if deck_elem.get_attribute('value'): # It it was succesful the selectable returns empty string
                raise NoDeckFoundError(deck)

            if tags:
                self.driver.find_element_by_xpath(
                    '/html/body/div/main/form/div[last()]/div/input').send_keys(tags)

            # Fill fields

            self.driver.find_element_by_xpath('/html/body/div/main/form/div[1]/div/div').send_keys(front)
            self.driver.find_element_by_xpath('/html/body/div/main/form/div[2]/div/div').send_keys(back)

            # Add
            self.driver.find_element_by_xpath(
                    '/html/body/div/main/form/button').click()
        except:
            print(traceback.format_exc())
            if not os.path.isfile('screenshot_error.png'):
                self.driver.save_screenshot("screenshot_error.png")
            raise
        return ret


class NoDeckFoundError(Exception):
    def __init__(self, deck):
        self.deck = deck

class NoCardTypeFoundError(Exception):
    def __init__(self, card_type):
        self.card_type = card_type

if __name__ == "__main__":
    cs = CardSender('aaa@gmail.com', 'mypassword')
    cs.send_card('xoxoxo', ':)', 'Vocabulary')
