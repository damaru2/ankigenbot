import pronouncing
import re

arpabet_to_ipa = {

        'AE1':'\'æ', 'AE2':'ˌæ',        'AE0':'æ',
        'AA1':'\'ɑ', 'AA2':'ˌɑ',        'AA0':'ɑ',
        'AH1':'\'ʌ', 'AH2':'ˌʌ',
        'EH1':'\'ɛ', 'EH2':'ˌɛ',        'EH0':'ɛ',
        'IH1':'\'ɪ', 'IH2':'ˌɪ',
        'AO1':'\'ɔ', 'AO2':'ˌɔ',        'AO0':'ɔ',
        'UH1':'\'ʊ', 'UH2':'ˌʊ',        'UH0':'ʊ',

        'ER1':'\'ɜr', 'ER2':'ˌɜr',      'ER0':'ɜr',

        # Diphthongs
        'IY1':'\'i', 'IY2':'ˌi',        'IY0':'i',
        'UW1':'\'u', 'UW2':'ˌu',        'UW0':'u',
        'AW1':'\'aʊ', 'AW2':'ˌaʊ',      'AW0':'aʊ',
        'AY1':'\'aɪ', 'AY2':'ˌaɪ',      'AY0':'aɪ',
        'EY1':'\'eɪ', 'EY2':'ˌeɪ',      'EY0':'eɪ',
        'Y UW1':'\'ju', 'Y UW2':'ˌju',  'Y UW0':'ju',
        'OW1':'\'oʊ', 'OW2':'ˌoʊ',      'OW0':'oʊ',
        'OY1':'\'ɔɪ', 'OY2':'ˌɔɪ',      'OY0':'ɔɪ',

        # Reduced
        'AH0':'ə',
        'IH0':'ᵻ',

        # Semi-vowels
        'W':'w',
        'Y':'j',

        'B':'b',
        'CH':'ʧ',
        'D':'d',
        'F':'f',
        'G':'g',
        'HH':'h',
        'JH':'ʤ',
        'K':'k',
        'L':'l',
        'M':'m',
        'N':'n',
        'NG':'ŋ',
        'P':'p',
        'R':'r',
        'S':'s',
        'SH':'ʃ',
        'T':'t',
        'DH':'ð',
        'TH':'θ',
        'V':'v',
        'Z':'z',
        'ZH':'ʒ',
}

def to_ipa(s):
    s = re.split('([^a-zA-Z\'])', s)
    for i in range(len(s)):
        if s[i] and (s[i][0].isalpha() or s[i][0] == '\''):
            try:
                s[i] = pronouncing.phones_for_word(s[i])[0]
            except IndexError:
                continue
            aux = []
            for phoneme in s[i].split(" "):
                if phoneme != '':
                    aux.append(arpabet_to_ipa[phoneme])
                    #aux.append(arpabet_to_new_spelling[phoneme])
            s[i] = "".join(aux)
    return "".join(s)

