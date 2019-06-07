from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

import traceback
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.action_chains import ActionChains

import os


class CardSender:
    url = 'https://ankiweb.net/account/login'

    def __init__(self, username, password):
        self.driver = None

        self.last_access = time.time()

        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920x1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        options.binary_location = "/usr/lib/chromium-browser/chromium-browser"
        self.driver = webdriver.Chrome(chrome_options=options)

        self.driver.set_window_size(1920, 1080)
        self.driver.get(CardSender.url)
        usr_box = self.driver.find_element_by_id('email')
        usr_box.send_keys(username)
        pass_box = self.driver.find_element_by_id('password')
        pass_box.send_keys('{}\n'.format(password))

    def send_card(self, front, back, deck):
        try:
            # Click on the "Add" tab
            self.driver.find_element_by_xpath(
                            '//*[@id="navbarSupportedContent"]/ul[1]/li[2]/a').click()

            # Card type = Basic
            select = Select(self.driver.find_element_by_id('models'))

            try:
                select.select_by_visible_text("Basic")
            except:
                for option in select.options: #iterate over the options, place attribute value in list
                    if "Basic" in option.text:
                        select.select_by_visible_text(option.text)

            # Write deck type
            deck_box = self.driver.find_element_by_id('deck')
            deck_box.clear()
            deck_box.send_keys(deck)

            # Fill fields
            self.driver.find_element_by_xpath('//*[@id="f0"]').send_keys(front)
            self.driver.find_element_by_id('f1').send_keys(back)

            # Add
            self.driver.find_element_by_xpath(
                    '/html/body/main/p/button').click()
        except:
            print(traceback.format_exc())
            if not os.path.isfile('screenshot_error.png'):
                driver.save_screenshot("screenshot_error.png")
            raise


if __name__ == "__main__":
    cs = CardSender('aaa@gmail.com', 'mypassword')
    cs.send_card('xoxoxo', ':)', 'Vocabulary')
