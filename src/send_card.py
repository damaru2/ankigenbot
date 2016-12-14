from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.action_chains import ActionChains


class CardSender:
    url = 'https://ankiweb.net/account/login'

    def __init__(self, username, password):
        self.driver = None
        self.cap = webdriver.DesiredCapabilities.PHANTOMJS
        self.cap["phantomjs.page.settings.resourceTimeout"] = 0
        self.cap["phantomjs.page.settings.loadImages"] = False
        self.driver = webdriver.PhantomJS(desired_capabilities=self.cap)
        self.driver.set_window_size(1920, 1080)
        self.driver.get(CardSender.url)
        usr_box = self.driver.find_element_by_id('email')
        usr_box.send_keys(username)
        pass_box = self.driver.find_element_by_id('password')
        pass_box.send_keys(password + '\n')

    def send_card(self, front, back, deck):
        # Click on add
        self.driver.find_element_by_xpath(
            '//*[@id="headerTable"]/tbody/tr[2]/td/a[3]').click()
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
        self.driver.find_element_by_xpath(
            '//*[@id="modelarea"]/tbody/tr[1]/td[3]/button').click()
        self.driver.quit()

if __name__ == "__main__":
    cs = CardSender('davidmartirubio@gmail.com', 'myankipassword')
    cs.send_card('xoxoxo', ':)', 'Vocabulary')
