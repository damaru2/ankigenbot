# ankigenbot
[@ankigen_bot](https://t.me/ankigen_bot), Telegram bot to automatically generate and upload anki cards to [ankisrs.net](ankisrs.net). 

Anki is a very effective program to learn vocabulary, but anki does not have any way to **generate cards automatically**. Given a word in English, Spanish or French this bot will send you definitions with sentence examples and with a tap you can add them to your anki deck. 

Anki + [@ankigen_bot](https://t.me/ankigen_bot) is the best way to learn vocabulary: ___Send the bot every word you do not understand when you are reading, studying or interacting with people, it will not take you time and anki will make sure you do not ever forget all those words.___

## Features

+ Generate flashcards with definitions and examples for English, Spanish and French.
    + The word from the example is removed. In English, regular derivatives of the words are removed.

+ Automatically upload the cards to the deck of your anki account you select.

+ Generate the cards with the front/back fields swapped with `/swap`. Definition is front by default.

+ Include the pronunciation of the word in the flashcard with `/ipa`. Deactivated by default.

---

If you want [@ankigen_bot](https://t.me/ankigen_bot) to support another language, you can open an issue and point me to a hopefully nice, free and simple dictionary for that language.

![image3](https://github.com/damaru2/ankigenbot/blob/master/.assets/image3.png)

## Write a word and select the definitions you want
<img src="https://github.com/damaru2/ankigenbot/blob/master/.assets/image1.png" width="650">

<img src="https://github.com/damaru2/ankigenbot/blob/master/.assets/image2.png" width="650">

<img src="https://github.com/damaru2/ankigenbot/blob/master/.assets/image4.jpg" width="450">

---
## Installation
For executing this code, you will need to have:

+ The following python libraries: sqlite3, selenium, the telegram-bot libraries and pronouncing. For instance, with pip it would be
```
pip3 install sqlite3 selenium python-telegram-bot pronouncing
```

+ [translate shell](https://github.com/soimort/translate-shell/), follow the instructions in the repository for installation.

+ Create a file called `private_conf.py` with a variable `token_id` initialized to the toked_id of your telegram bot. You also have to create in the root directory two folders called `data` and `log`. In commands:
```
git clone https://github.com/damaru2/ankigenbot
cd ankigenbot
mkdir data log
echo "token_id = '<your_bot_token_id>'" > ./src/private_config.py
```

+ Chrome (or Chromium). Open `src/send_card.py` and edit `options.binary_location` so it points to where your Chrome/Chromium binary file is.

Once everything is installed you can run the bot from the root directory:
```
python3 src/ankigen_bot.py
```
