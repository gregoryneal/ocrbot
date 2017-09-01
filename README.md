# ocrbot
a reddit bot designed to perform OCR on images found in a subreddit

1. Provide your validation.txt file in the same directory as ocrbot.py, this file must be empty other than 4 different lines:
  Line 0: your 26 character reddit api secret
  Line 1: your 14 character reddit client id
  Line 2: your reddit bot username
  Line 3: your reddit bot's password
  
2. Once your validation info is supplied you can run the bot like a normal python script, it will loop through submissions in the supplied subreddit,
looking for images, once an image is found it downloads it and performs OCR (optical character recognition). If anything is found, the text is then
passed through a filter to prepare it for a reddit comment. Then the option to open a window and compare the reddit image with the OCR text is given,
once closed an option to reply to the image with the OCR text is given. If selected the bot will post on the selected submission.

Currently ships with a filter to create [zalgo text](http://www.eeemo.net/), or text with tons of combining characters
