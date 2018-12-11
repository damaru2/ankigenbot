# ankigenbot
[@ankigen_bot](https://t.me/ankigen_bot), Telegram bot to automatically generate and upload anki cards to [ankisrs.net](ankisrs.net). Anki is a very effective program to learn vocabulary, but anki does not have any way to generate cards automatically. This is a program that given a word in English, Spanish or French it will send you definitions with sentence examples and with a tap you can add them to your anki deck.

If you want [@ankigen_bot](https://t.me/ankigen_bot) to support another language, you can open an issue and point me to a hopefully nice, free and simple dictionary for that language.

![image3](https://github.com/damaru2/ankigenbot/blob/master/.assets/image3.png)

## Write a word and select the definitions you want
<img src="https://github.com/damaru2/ankigenbot/blob/master/.assets/image1.png" width="650">

<img src="https://github.com/damaru2/ankigenbot/blob/master/.assets/image2.png" width="650">

<img src="https://github.com/damaru2/ankigenbot/blob/master/.assets/image4.jpg" width="450">

---
## Installation
For executing this code, you need selenium, Chrome or Chromium,the telegram libraries and [translate shell](https://github.com/soimort/translate-shell/). 

Create a file called `private_conf.py` with a variable `token_id` initialized to the toked_id of your telegram bot.

Open `src/send_card.py` and edit `options.binary_location` so it points to your Chromium/Chrome binary file

You also have to create in the root directory two folders called `data` and `log`.
