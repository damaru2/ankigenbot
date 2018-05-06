from urllib import request
from lxml import html

#######################

def parse_examples(examples):
    try:
        parsed = [example.text_content() for example in examples[0].cssselect('.x-g') ]
        return "\nExamples:\n" + "\n".join(parsed)
    except:
        return ""

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


OXFORD_PATH = "https://www.oxfordlearnersdictionaries.com/definition/english/"

def retrive_defs(word):
    url = OXFORD_PATH + word
    doc_html = request.urlopen(url).read()
    doc = html.fromstring(doc_html)
    prefix = parse_pref(doc.xpath("//span[@class='pos'][1]/text()")[0])

    content = doc.cssselect(".sn-gs")
    definitions = []

    for entries in content:
        for defs in entries.cssselect(".sn-g"):
            examples = examples = parse_examples(defs.cssselect('.x-gs'))
            _def = defs.cssselect('.def')[0].text_content()

            definitions.append("{}{}{}".format(prefix, _def, examples))

    return definitions

print( "\n#################\n".join(retrive_defs('get')))