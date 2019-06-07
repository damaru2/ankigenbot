# ankigenbot
[@ankigen_bot](https://t.me/ankigen_bot), Telegram bot to automatically generate and upload anki cards to [ankisrs.net](ankisrs.net). 

Anki is a very effective program to learn vocabulary, but anki does not have any way to **generate cards automatically**. Given a word in English, Spanish or French this bot will send you definitions with sentence examples and with a tap you can add them to your anki deck. 

Anki + [@ankigen_bot](https://t.me/ankigen_bot) is the best way to learn vocabulary: Send the bot every word you do not understand when you are reading, studying or interacting with people, it will not take you time and anki will make sure you do not ever forget all those words.

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
For executing this code, you need selenium, Chrome or Chromium,the telegram libraries and [translate shell](https://github.com/soimort/translate-shell/) and pronouncing (python library). 

Create a file called `private_conf.py` with a variable `token_id` initialized to the toked_id of your telegram bot.

Open `src/send_card.py` and edit `options.binary_location` so it points to your Chromium/Chrome binary file

You also have to create in the root directory two folders called `data` and `log`.
