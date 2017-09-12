from PIL import Image, ImageEnhance, ImageFilter
from prawcore import PrawcoreException
from zalgo_text import zalgo
from enum import Enum
import praw
import shutil
import time
import requests
import pytesseract as ocr
import webbrowser
import random
import re
import datetime
import os
import db

class RunType(Enum):
	POSTING = 1,    #will post to reddit, make sure you are validated
	DEBUG = 2,      #will only print out the full text for inspection, will not add to completed id file, nor will it check it for visited links

class bot():    

	@property
	def runType(self):
		return self._runType

	@runType.setter
	def runType(self, value):
		if value is RunType.DEBUG:
			print("DEBUG MODE")
			self.recordsubmissions = False
			self.checkVisitedFile = False
		if value is RunType.POSTING:
			print("POSTING MODE")
			self.recordsubmissions = True
			self.checkVisitedFile = True
		self._runType = value

	def __init__(self, **kwargs):
		self.SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+"/"

		#place your reddit api secret, client id, username and password on seperate lines in validation.txt in this directory
		validation = self.loadCredentials()
		print(validation)
		self.secret = validation[0]
		self.clientId = validation[1]
		self.username = validation[2]
		self.password = validation[3]

		self.image_fname = self.SCRIPT_DIR+"images/img"

		self.reddit = None
		self.subreddit = "surrealmemes"
		self.recordsubmissions = True
		self.checkVisitedFile = True

		self.preText = "**^^there ^^are ^^WORDS ^^nearby**"
		self.postText = "^^^^i ^^^^am ^^^^a ^^^^bot ^^^^| ^^^^created ^^^^by ^^^^" + zalgo.zalgofy("CHAOS") + "^^^^| ^^^^[feedback](https://www.reddit.com/message/compose/?to=ocr_bot)"

		#process this many submissions before exiting, so the program doesn't run forever
		#if you want the program to run forever (process every new submission forever), set this value to -1
		self.numSubmissionsToProcess = -1

		#get a Reddit instance
		self.reddit = praw.Reddit(client_id=self.clientId,
						client_secret=self.secret,
						password=self.password,
						user_agent='python:'+self.username+':v0.1 (by /u/'+self.username+')',
						username=self.username)

		self.runType = RunType.DEBUG

		print("Loaded " + self.username + "...")

	def loadCredentials(self):		
		return list(db.getCredentials())

	def submissionFilter(self, submission):
		'''
		Use to selectively filter submissions based on contents.
		Returns True if you the submission can be further processed
		Returns False if the submission should be skipped
		'''

		#only look for imgur links or direct hosted images
		if ("imgur.com" not in submission.url and "i.redd.it" not in submission.url):
			return False

		#we dont want imgur albums either
		if ("/a/" in submission.url):
			return False

		#also only take images that are linked directly so we can download them
		if (".jpg" not in submission.url and ".png" not in submission.url):
			return False

		#iterate through the filter file and see if it contains sumbission.id, if so we have already processed this image
		if self.checkVisitedFile:
			if db.linkExists(submission.id):
				return False
		return True

	def recordNewSubmission(self, submissionId):
		if not self.recordsubmissions:
			return
		
		db.addVisitedLink(submissionId)
		
	def approveMessage(self, message):
		canReturn = False
		answer = False

		yes = [ 'yes', 'y', 'yea', 'yep', 'ye', ]
		no = [ 'no', 'n', 'nope', '', ]

		while True:
			msg = input(message + " Y/N: ").lower()
			if msg in yes:
				return True
			elif msg in no:
				return False
			else:
				print("please enter Y or N")

		return answer

	def englishWordFuzzyReplaceFilter(self, text):
		'''
		fuzzy compares each word in the text and replaces it with the most similar match, essentially tries to correct some errors in recognition
		'''

	def lettersOnlyFilter(self, text):
		'''
		removes all non alphabetic characters
		'''
		#get each line of text
		lines = text.split("\n") #something like [pretext multiple words, text multi words line 1, text multi words line 2, etc... , post text]
		newLines = [] 

		#iterate through the lines
		for line in lines: # line = 'pretext multiple words' etc... goal: create newLine = 
			#get each word
			words = line.split(' ') #something like [pretext, multiple, words,]
			newWords = []
			for word in words: # 'pretext' etc...
				newWord = ''.join(c for c in word if c.isalpha())
				newWords.append(newWord)              

			newLines.append(' '.join(newWords))

		#recompose it back into a reddit comment and print some data
		text = "\n".join(newLines)
		return text

	def wordLengthFilter(self, text, minWordLength):
		'''
		Removes any word shorter than minWordLength
		'''
		#get each line of text
		lines = text.split("\n") #something like [pretext multiple words, text multi words line 1, text multi words line 2, etc... , post text]
		newLines = [] 

		#iterate through the lines
		for line in lines: # line = 'pretext multiple words' etc...
			#get each word
			words = line.split(' ') #something like [pretext, multiple, words,]
			newWords = []
			for word in words: # 'pretext' etc...
				a = word.strip()
				if len(a) >= minWordLength: #dont worry about any empty words either
					newWords.append(a)           

			newLines.append(' '.join(newWords))

		#recompose it back into a newline string
		text = "\n".join(newLines)
		return text

	def lineLengthFilter(self, text, minLineLength):
		'''
		removes all lines shorter than minLineLength
		'''
		#get each line of text
		lines = text.split("\n") #something like [pretext multiple words, text multi words line 1, text multi words line 2, etc... , post text]
		newLines = [] 

		#iterate through the lines
		for line in lines: # line = 'pretext multiple words' etc...
			if len(line) >= minLineLength:
				newLines.append(line)

		#recompose it back into a newline string
		text = "\n".join(newLines)
		return text

	#prepare the text for submission at /r/surrealmemes, pretty much randomly applies combining characters to words ("zalgo" text)
	def surrealifyFilter(self, text):
		'''
		Prepares the text for submission to /r/surrealmemes.
		Randomly applies a zalgo filter to lines,
		Randomly wraps words in an angery flag, which makes it shake all crazy in the subreddit's comments
		'''
		chanceLineIsZalgofied = 0.4
		changeWordIsAngery = 0.1

		#get each line of text
		lines = text.split("\n") #something like [pretext multiple words, text multi words line 1, text multi words line 2, etc... , post text]
		newLines = [] 

		#iterate through the lines
		for line in lines: # line = 'pretext multiple words' etc... goal: create newLine = 
			zalgofy = False
			if random.uniform(0,1) <= chanceLineIsZalgofied:
				zalgofy = True

			#get each word, decompose it into a list of letters, zalgofy and then recompose the words and lines individually... just watch
			words = line.split(' ') #something like [pretext, multiple, words,]
			newWords = []
			for word in words: # 'pretext' etc...
				newWord = word
				#zalgofy if we need to, then angery it if we need to
				if zalgofy:
					newWord = zalgo.zalgofy(word)

				if random.uniform(0,1) <= changeWordIsAngery and word.replace(" ", ""):
					if random.uniform(0,1) < 0.5:
						newWord = "[" + newWord.strip("[\/] ") + "](/a)" #strip those characters that we dont want, they will mess up the comment
					else:
						newWord = "[" + newWord.strip("[\/] ") + "](/angery)"

				newWords.append(newWord)              

			newLines.append(' '.join(newWords))

		#recompose it back into a newline string and return
		text = "\n".join(newLines)
		return text

	def fullFilterText(self, text, pretext, posttext, pretextFilter=False, posttextFilter=False):
		'''
		Convenience method to create a fully formatted reddit comment, will replace \n with \n\n        
		This is where you will add the pretext and the post text to the comment.
		'''
		#chain your filters here, inner ones are evaluated first
		filters = self.filterSingleString

		#apply filters to pre and post text
		if pretextFilter:
			pretext = filters(pretext)
		if posttextFilter:
			posttext = filters(posttext)

		text = filters(text) #text filters
		return str(pretext + "\n&nbsp;\n" + text + "\n&nbsp;\n" + posttext).replace("\n","\n\n")

	def filterSingleString(self, text):
		'''
		Here you can chain filters to the reddit comment for different effects:
		
			wordsOnlyFilter:    removes all non alphabetical characters
			wordLengthFilter:   removes all words shorter than the argument
			surrealFilter:      randomly applies the zalgo filter to lines and wraps words in [word](/a) tags so they shake on /r/surrealmemes

		Text will be a newline escaped string.
		An example would be something like:

		text = self.wordsOnlyFilter(text)
		text = self.wordLengthFilter(text, 4)
		return text
		'''
		text = self.lettersOnlyFilter(text)     #remove all non english letters
		#text = self.wordLengthFilter(text, 2)   #remove all words shorter than 3 characters
		text = self.lineLengthFilter(text, 1)   #only accept lines that have at least 1 character in them
		text = self.surrealifyFilter(text)
		return text

	#processes an image for OCR, fpath is assumed to be an image type file
	def processImage(self, fpath):
		'''
		This method will attempt to extract text from an image using various preprocessing techniques and picking the best result (the longest result)
		
		Prepreprocessing: convert the image to grayscale

		First method: Apply gaussian blur
		Second method: Apply sharpness filter
		Third method: First and second method for some reason?
		'''
		texts = []
		image = Image.open(fpath)        
		image = self.remove_transparency(image)
		image = image.convert("L")
		baseimage = image.copy() #a reference to the unprocessed image, only process this bad boy

		#first method
		image = baseimage.filter(ImageFilter.GaussianBlur())
		#image = image.convert("1")        
		image.save(fpath)
		#save for testing
		texts.append(ocr.image_to_string(image))

		#second method
		image = baseimage.filter(ImageFilter.SHARPEN)
		image.save(fpath)
		texts.append(ocr.image_to_string(image))

		#third method
		image = baseimage.filter(ImageFilter.GaussianBlur()).filter(ImageFilter.SHARPEN)
		image.save(fpath)
		texts.append(ocr.image_to_string(image))

		#add more methods here

		#now pick the longest on and return it
		longestText = max(texts, key=len)
		print("Used method " + str(texts.index(longestText) + 1))

		return longestText

	def remove_transparency(self, im, bg_colour=(255, 255, 255)):
		# Only process if image has transparency (http://stackoverflow.com/a/1963146)
		if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

			# Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
			alpha = im.convert('RGBA').split()[-1]

			# Create a new background image of our matt color.
			# Must be RGBA because paste requires both images have the same format
			# (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
			bg = Image.new("RGBA", im.size, bg_colour + (255,))
			bg.paste(im, mask=alpha)
			return bg

		else:
			return im

	def makeComment(self, submission, comment):
		if self.reddit is None:
			return None

		#reauthorize the bot to post
		self.reddit.read_only = False

		try:
			submission.reply(comment)
			print("submission approved")
			#append the submission id to the file so we never work on it again
			self.recordNewSubmission(submission.id)
		except PrawcoreException:
			print("error submitting comment")
			input("press enter to continue...")
		self.reddit.read_only = True

	#initialize the bot and loop through the posts
	def generatePosts(self):        
		print("Browsing posts from /r/" + self.subreddit)
		if self.numSubmissionsToProcess == -1:
			print("Processing all new submissions until manually terminated...")
		else:
			print("Processing " + str(self.numSubmissionsToProcess) + " submissions before termination.")

		#deauthorize the reddit instance until just before we want to post
		self.reddit.read_only = True

		#get the /r/all subreddit
		posts = self.reddit.subreddit(self.subreddit)

		i = 0
		while True:
			if self.numSubmissionsToProcess != -1 and i >= self.numSubmissionsToProcess:
				print("Finished processing all " + str(self.numSubmissionsToProcess) + " submissions.")
				break

			try:
				#loop through posts
				for submission in posts.stream.submissions():

					if self.numSubmissionsToProcess != -1 and i >= self.numSubmissionsToProcess:
						break

					if not self.submissionFilter(submission):
						continue

					print("Processing submission: " + submission.id)

					#get the pics extension so we can open the correct type of file
					ext = submission.url[-4:]  
					fpath = self.image_fname + ext

					#download the image and copy it to a file
					response = requests.get(submission.url, stream=True)
					with open(fpath, "wb") as img_file:
						shutil.copyfileobj(response.raw, img_file)           

					#remove this data
					del response

					text = self.processImage(fpath)

					c = True #skip this image?
					for line in text.split('\n'):
						if len(line.replace(' ', '')) > 2:
							c = False #not if there are any long enough lines in it
							break

					if c:
						print("Text too short, skipping...")
						print(text)
						self.recordNewSubmission(submission.id)
						continue
			
					#create the reddit comment
					fulltext = self.fullFilterText(text, self.preText, self.postText)

					print("Finished processing " + str(submission.id) + "!")
					print("\nFull Post:\n")
					print(fulltext)

					if self.runType is RunType.POSTING:
						#try to post and open the comment window
						try:
							i += 1
							progress = str(i) + " of "
						
							if self.numSubmissionsToProcess == -1:
								progress += "∞"
							else:
							   progress += str(self.numSubmissionsToProcess)

							print("progress: " + progress + " - " + datetime.datetime.now().strftime("%X"))
							self.makeComment(submission, fulltext)
						except PrawcoreException:
							print("There was an error posting, restarting stream...")
							break
			except PrawcoreException:
				print("Prawcore exception, restarting stream...")
				continue
			except KeyboardInterrupt:
				print("Keyboard interruption, stopping stream...")
				break

	def getNewSubmissions(self, numPosts=5):
		'''
		Will download and return a list of submissions for processing

		Tries to download numPosts new submissions within globalTimeout seconds
		Will return early if a post takes longer than globalTimeout to download any new post
		'''
		submissions = []
		
		print("Downloading "+str(numPosts)+" posts from /r/" + self.subreddit)
		#deauthorize the reddit instance until just before we want to post
		self.reddit.read_only = True

		#get the subreddit
		posts = self.reddit.subreddit(self.subreddit)

		i = 0
		gtfo = False #set to true once the stream returns a None submission, then used to exit the while loop
		while True:
			if i >= numPosts:
				print("Downloaded " + str(numPosts) + " submissions for processing.")
				break
			
			try:
				print("Trying to download more posts...")

				#loop through posts, this will give up to 100 historical submissions so its perfect for scheduled tasks to dl the most recent submissions every so often
				for submission in posts.stream.submissions(pause_after=0):
					if submission is None: #each time there is a null submission we will exit the loop and check for a global timeout
						print("No new posts - timeing out...")
						gtfo = True
						break
					if i >= numPosts:
						break
					if not self.submissionFilter(submission):
						continue

					if submission not in submissions:
						submissions.append(submission)
						print("success! " + str(i+1) + "/" + str(numPosts))
						i += 1
			except PrawcoreException:
				print("Prawcore exception, restarting stream...")
				continue
			except KeyboardInterrupt:
				print("Keyboard interruption, stopping stream...")
				break

			if gtfo:
				break
		return submissions

	def processSubmissions(self, submissions):
		'''
		Will process a list of submissions (download image and perform OCR) and make a post based on the output
		'''
		print("Processing " + str(len(submissions)) + " submissions...")
		for submission in submissions:
			#get the pics extension so we can open the correct type of file
			ext = submission.url[-4:]  
			fpath = self.image_fname + ext
			#download the image and copy it to a file
			response = requests.get(submission.url, stream=True)
			with open(fpath, "wb") as img_file:
				shutil.copyfileobj(response.raw, img_file)           

			#remove this data
			del response

			text = self.processImage(fpath)

			c = True #skip this image?
			for line in text.split('\n'):
				if len(line.replace(' ', '')) > 2:
					c = False #not if there are any long enough lines in it
					break

			if c:
				print("Text too short, skipping...")
				print(text)
				self.recordNewSubmission(submission.id)
				continue
			
			#create the reddit comment
			fulltext = self.fullFilterText(text, self.preText, self.postText)

			try:
				print("Finished processing " + str(submission.id) + " - " + str(submissions.index(submission)+1) + "/" + str(len(submissions)))
			except ValueError:
				print("submission not found in submissions list, this error should not occur!")
			#print("\nFull Post:\n")
			#print(fulltext)

			if self.runType is RunType.POSTING:
				#try to post and open the comment window
				try:
					self.makeComment(submission, fulltext)
				except PrawcoreException:
					print("There was an error posting, restarting stream...")
					break

	def doSingleBatch(self, numPostsToProcess=5):
		submissions = self.getNewSubmissions(numPosts=numPostsToProcess)
		self.processSubmissions(submissions)

if __name__ == "__main__": 
    #set up the database for the first time
    #run this next line by itself once, then comment it out:
    #db.recreateDatabase("<clientid>", "<secret>", "<username>", "<password>")

	a = bot()
	a.subreddit = "surrealmemes"
	a.runType = RunType.POSTING
	a.doSingleBatch(numPostsToProcess=15)
    #input("press enter to continue...")