# ocrbot
a reddit bot designed to perform OCR using [pytesseract](https://github.com/madmaze/pytesseract) on images found in a subreddit. This code is used to run Reddit's [ocr_bot](https://www.reddit.com/user/ocr_bot/)

0. Install [Google Tesseract OCR](https://github.com/tesseract-ocr/tesseract) on your machine and be sure to note the installation directory. To make sure you can invoke tesseract as a command in your command prompt you must first locate the directory containing tesseract.exe, which is in your install directory. You must add this path to your environment variables (use google if you don't know how). Next you must install a series of python packages for the bot to work. You can use pip to install all of these:
* ```pip install pytesseract``` - these are just python bindings for Tesseract OCR.   
* ```pip install praw```        - so the bot can access the reddit api.
* ```pip install pillow```      - for the image preprocessing library.
* ```pip install zalgo_text```  - [my own creation](https://github.com/gregoryneal/zalgo), this allows the zalgo text filter to work.

1. Provide your validation.txt file in the same directory as ocrbot.py, this file must be empty other than 4 different lines:
  Line 0: your 26 character reddit api secret
  Line 1: your 14 character reddit client id
  Line 2: your reddit bot username
  Line 3: your reddit bot's password
  
2. Once your validation info is supplied and installed any prerequisite packages, you can run the bot like a normal python script.
It will loop through submissions in the supplied subreddit, looking for images, once an image is found it downloads it and performs OCR (optical character recognition) to try and detect text. If any text is found, it is passed through a filter to prepare it for a reddit comment. Finally it posts the reddit comment, and opens a new tab to the post for viewing.
