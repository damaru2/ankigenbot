# -*- coding: utf-8 -*-

import os
import re
from subprocess import PIPE, Popen


class AnkiAutomatic:

    last = ["Synonyms", "Examples","See also", "EOF"]

    def __init__(self, concept):
        self.concept = concept

    def retrieve_defs(self, language='en'):
        concept = self.concept.lower()
        if concept.find(" ") != -1:
            return
        query = "trans -no-auto -d {}:{} {}".format(language, language, concept)
        #asdf = os.popen(query)
        translation = Popen(query, shell=True, stdout=PIPE).stdout.read().decode('utf8')
        tr = ParseTranslation(translation)
        concept = tr.get_concept().strip('\t\r\n\0')
        # This is to remove the "null" that appears after the change in google translate
        concept = concept.split()[0]
        aux = tr.next_line()
        prefix = self.pref(aux)
        if prefix == "":
            return
        line = self.normalize(tr.next_line())
        n_def = 0  # Number of definitions
        definitions = []
        while True:
            n_def += 1
            if not line:
                break
            example = self.parse_example(tr.next_line(), concept, language)
            if not example:
                tr.go_back()
            definitions.append("{}{}{}".format(prefix, line, example))
            line = tr.next_line()
            if line in AnkiAutomatic.last:
                break
            if self.pref(line) == "":
                while line != "":
                    line = tr.next_line()
                line = tr.next_line()
                if line in AnkiAutomatic.last:
                    break
            new_prefix = self.pref(line)
            if new_prefix != "":  # Change of prefix
                prefix = new_prefix
                line = self.normalize(tr.next_line())
            else:
                if line:
                    line = self.normalize(line)
                else:
                    line = self.normalize(tr.next_line())

        return definitions

    def pref(self, x):
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

    def normalize(self, line):
        # Remove first and last "words" which are format tags
        res = line.split(' ', 1)[1].strip()[:-5]
        if res[-1] == '.':
            res = res[:-1]
        return res

        #return line.rsplit('.', 1)[0].split(' ', 1)[1].strip()

    def parse_example(self, example, concept, language):
        if example[:11] == '        - \"':   # If there is example
            # This removes the concept or variations of it
            example = example.split("\"")[1]

            def remove_pattern(example, concept):
                # This is so words that contain concept or a conjugation of it
                # as a substring are not removed
                dots = "....."
                regex = re.compile("(^|[^a-zA-Z]){}([^a-zA-Z]|$)".format(concept), re.IGNORECASE)
                return regex.sub("\g<1>{}\g<2>".format(dots), example)

            # remove concept variations
            if language == 'en':
                example = remove_pattern(example, '{}s'.format(concept))
                example = remove_pattern(example, "{}es".format(concept))

                if concept[-1] == 'e':
                    example = remove_pattern(example, "{}d".format(concept))
                    example = remove_pattern(example, "{}ing".format(concept[:-1]))

                example = remove_pattern(example, "{}ed".format(concept))
                example = remove_pattern(example, "{}{}ed".format(concept, concept[-1]))
                example = remove_pattern(example, "{}ing".format(concept))
                example = remove_pattern(example, "{}{}ing".format(concept, concept[-1]))
                if concept[-1] == 'f':
                    example = remove_pattern(example, "{}ves".format(concept[:-1]))
                if concept[-1] == 'fe':
                    example = remove_pattern(example, "{}ves".format(concept[:-2]))
                    #example = remove_pattern(example, "{}ing".format(concept[:1], concept[:-1]))
                if concept[-1] == 'y':
                    example = remove_pattern(example, "{}ies".format(concept[:-1]))
                    example = remove_pattern(example, "{}ied".format(concept[:-1]))
            if language == 'es':
                example = remove_pattern(example, '{}s'.format(concept))
            example = remove_pattern(example, concept)

            return " (e.g. {})".format(example)
        else:
            return ''

    # PC support
    def send_to_file(self, card_lines, concept):
        f = open(AnkiAutomatic.target_file, 'a')
        for line in card_lines:
            f.write("\"{}\"; {}\n".format(line, concept))
        f.close()

    # PC support
    def ask_user(self, n_def, definitions, concept):
        card_lines = []
        if n_def == 1:
            definitions = definitions.replace("\\\"", "\"")[7:-2]
            confirm = os.system('''zenity --question --ok-label=\"Ok\" --cancel-label=\"Cancel\"  --height=10 --text=\" The following card will be added:\n {} \"'''
                                .format(definitions.replace("\"", "\\\"")))
            if confirm == 0:
                card_lines.append(definitions)
        elif n_def > 1:
            lines = os.popen("zenity  --list --text '{} - Select definitions to be updated to Anki's database' --checklist --column \"Pick\" --column \"Definitions\" {} --width=1000 --height=450".format(concept, definitions)).read()
            card_lines = lines[:-1].split('|')
        else:  # no definitions found
                os.system("zenity --question --ok-label=\"Ok\" --cancel-label=\"Cancel\"  --height=10 --text=\"No definitions were found for \\\"{}\\\" \"".format(concept))
        return card_lines


class ParseTranslation:

    def __init__(self, translation):
        self.translation = translation.split('\n')
        self.counter = -1
        self.concept = self.next_line().lower()
        phonetic = self.next_line()
        # If there was a phonetic line, extra read
        if len(phonetic) > 0:  # and phonetic[0] == '/': TODO check that this extra condition is not neccesary
            self.next_line()

    def next_line(self):
        self.counter += 1
        try:
            return self.translation[self.counter]
        except IndexError:
            return 'EOF'

    def go_back(self):
        self.counter -= 1

    def get_concept(self):
        return self.concept


if __name__ == "__main__":
    defs = AnkiAutomatic('awesome').retrieve_defs()
    print(defs)
