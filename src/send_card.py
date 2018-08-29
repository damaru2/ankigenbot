from selenium import webdriver
import traceback
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.action_chains import ActionChains


class CardSender:
    url = 'https://ankiweb.net/account/login'

    def __init__(self, username, password):
        self.driver = None
        #self.cap = webdriver.DesiredCapabilities.PHANTOMJS
        #self.cap["phantomjs.page.settings.resourceTimeout"] = 0
        #self.cap["phantomjs.page.settings.loadImages"] = False
        #self.driver = webdriver.PhantomJS(desired_capabilities=self.cap)
        #self.driver = webdriver.Chrome('/usr/bin/chromedriver')


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
        pass_box.send_keys(password + '\n')

    def send_card(self, front, back, deck):
        self.driver.find_element_by_xpath(
                            '//*[@id="navbarSupportedContent"]/ul[1]/li[2]/a').click()
        try:
            deck_box = self.driver.find_element_by_id('deck')
            deck_box.clear()
            deck_box.send_keys(deck)
        except:
            pass
        try:
            self.driver.find_element_by_xpath('//*[@id="f0"]').send_keys(front)
        except:
            pass
        try:
            self.driver.find_element_by_id('f1').send_keys(back)
        except:
            pass
        try:
            self.driver.find_element_by_xpath(
                    '/html/body/main/p/button').click()
        except:
            pass

        self.driver.quit()

if __name__ == "__main__":
    cs = CardSender('aaa@gmail.com', 'mypassword')
    cs.send_card('xoxoxo', ':)', 'Vocabulary')
