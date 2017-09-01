# ocrbot
a reddit bot designed to perform OCR using [pytesseract](https://github.com/madmaze/pytesseract) on images found in a subreddit

0. Install [Google Tesseract OCR](https://github.com/tesseract-ocr/tesseract) on your machine and be sure to note the installation directory. To make sure you can invoke tesseract as a command in your command prompt you must first locate the directory containing tesseract.exe, which is in your install directory. You must add this path to your environment variables (use google if you don't know how). Next use pip to install pytesseract, which is just python bindings for Tesseract OCR. Finally pip install praw to use the reddit api easily, and pip install pillow for the image preprocessing library.

1. Provide your validation.txt file in the same directory as ocrbot.py, this file must be empty other than 4 different lines:
  Line 0: your 26 character reddit api secret
  Line 1: your 14 character reddit client id
  Line 2: your reddit bot username
  Line 3: your reddit bot's password
  
2. Once your validation info is supplied and installed any prerequisite packages, you can run the bot like a normal python script.
It will loop through submissions in the supplied subreddit, looking for images, once an image is found it downloads it and performs OCR (optical character recognition) to try and detect text. If any text is found, it is passed through a filter to prepare it for a reddit comment. Finally it posts the reddit comment, and opens a new tab to the post for viewing.

Currently ships with a filter to create [zalgo text](http://www.eeemo.net/).
