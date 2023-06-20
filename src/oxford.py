from selenium import webdriver


OXFORD_PATH = "https://www.oxfordlearnersdictionaries.com/definition/english/"

def parse_examples(examples):
    examples = [ example.text for example in examples.find_elements_by_class_name('x-g') ]
    return "\nExamples:\n" + "\n".join(examples)
def parse_pref(x):
        return {
            "noun": "(n.) ",
            "suffix": "(suf.) ",
            "prefix": "(prefix) ",
            "verb": "(v.) ",
            "adjective": "(adj.) ",
            "abbreviation": "(abbrev.) ",
            "adverb": "(adv.) ",
            "preposition": "(prep.) ",
            "pronoun": "(pron.) ",
            "article": "(article) ",
            "exclamation": "(excl.) ",
            "conjunction": "(conj.) "
        }.get(x, "")   # "" is default if x not found



def retrive_defs(word):
    # uncommnet if you want to use chrome driver
        # path_to_chromedriver = 'chromedriver.exe' # change path as needed
        # options = webdriver.ChromeOptions()
        # options.set_headless(True)
        # driver = webdriver.Chrome(executable_path = path_to_chromedriver,chrome_options=options)

    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap["phantomjs.page.settings.resourceTimeout"] = 0
    cap["phantomjs.page.settings.loadImages"] = False
    driver = webdriver.PhantomJS(desired_capabilities=cap)
    driver.set_window_size(1920, 1080)

    driver.get(OXFORD_PATH+word)

    definitions = []

    prefix = parse_pref(driver.find_element_by_class_name('pos').text)

    content = driver.find_elements_by_class_name('sn-gs')
    for entries in content:
        for defs in entries.find_elements_by_class_name('sn-g'):
            examples = ""
            try:
                examples = parse_examples(defs.find_element_by_class_name('x-gs'))
            except:
                pass
            _def = defs.find_element_by_class_name('def').text

            definitions.append("{}{}{}".format(prefix, _def, examples))

    driver.quit()

    return definitions