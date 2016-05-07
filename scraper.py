# -*- coding: utf-8 -*-

from lxml import html
import requests
import time
import enchant
import sys
import sqlite3
import os
from multiprocessing import Pool
import threading
#import nltk

# Saving these
#article = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')
#article = requests.get('http://news.tj/ru/news/na-zadvorkakh-promyshlennogo-giganta-ili-v-kakikh-usloviyakh
	#-zhivut-tekstilshchiki')
#article = requests.get('http://news.tj/ru/news/aviakompaniya-somon-eir-otkryla-novyi-reis-dushanbe-kabul')
#article = requests.get('http://news.tj/ru/node/225178')
#article = requests.get('http://news.tj/ru/news/nochnaya-paskhalnaya-sluzhba-v-dushanbe-foto')



# Initialize a custom words array to hold words that are not in the dictionary, like names and other stuff
#not using this anymore
customWords = [
				u'ССР', u'Лахути', u'Яншина', u'Маяковского', u'Калигула', u'МТурсун-заде', 
				u'Макбет', u'Душанбе-Лахор-Душанбе', u'Эйр'
			  ]

pagesList = []
poolArray = []
poolSema = threading.BoundedSemaphore(value=1)

russianDictionary = enchant.Dict("ru_RU")

# Terminal symbols
terminals = ['!', '?', u'…', u'.']

def f(x): 
	return 'done scraping%s' % x

def getLinks(link):
	articleList = requests.get(link)
	tree = html.fromstring(articleList.content) 
	linkList = tree.xpath('//div[@id="content"]//div[@class="views-field-title"]//a/@href')

	return linkList

# This function strips out only the alphacharacters and the period
def stripAlphaChars(word):
	russianAlphaNumericChars = [
									u'а', u'б', u'в', u'г', u'д', u'е', u'ё', u'ж', u'з', u'и', u'й', 
									u'к', u'л', u'м', u'н', u'о', u'п', u'р', u'с', u'т', u'у', u'ф', 
									u'х', u'ц', u'ч', u'ш', u'щ', u'ъ', u'ы', u'ь', u'э', u'ю', u'я',

									u'А', u'Б', u'В', u'Г', u'Д', u'Е', u'Ё', u'Ж', u'З', u'И', u'Й', 
									u'К', u'Л', u'М', u'Н', u'О', u'П', u'Р', u'С', u'Т', u'У', u'Ф', 
									u'Х', u'Ц', u'Ч', u'Ш', u'Щ', u'Ъ', u'Ы', u'Ь', u'Э', u'Ю', u'Я',

									u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9',

									u'-'
							   ]
	x = 0
	while x < len(word):
		if word[x] not in russianAlphaNumericChars and word[x] not in terminals:
			word = word.replace(word[x], u'')
		else:
			x += 1
	#print "\"" + word + "\""
	return word

# Add a path to this
def saveArticleToFile(content, title, date):
	splitDate = date.split('/')
	filename = u'Articles/' + splitDate[2] + '/' + splitDate[1] + '/' + splitDate[0] + '/' + title.replace(u' ', '-') + '.html'

	if not os.path.exists(os.path.dirname(filename)):
		os.makedirs(os.path.dirname(filename))

	file = open(filename, 'w')
	print "wrote file"
	file.write(content)
	file.close()
	return filename


def hasNumbers(word):
	return any(char.isdigit() for char in word)

def stripArticle(article):
	# Initialize the dictionary
	#print russianDictionary.check(u'кВт.ч.')
	print "New thread spawned on", article
	#englishDictionary = enchant.Dict("en_US")
	#print englishDictionary.check(u'Lahore')

	# Just some stuff that I am using during debug to test some words
	#print russianDictionary.check(u'млрд')
	#print u'Калигула' in customWords


	# Right here we can iterate through the articles and profile them in a database extracting meta data and looping easily
	# It will even get resolved articles
	#article = requests.get('http://news.tj/ru/node/225180')

	# need to detect quotes before the end of a sentence
	# detect when a sentence is numbered
	# Things like this can get really messed up: http://news.tj/ru/node/225126

	page = requests.get(article)

	# If we get a 404 then just back out
	if page.status_code == 404:
		print "404 Link"
		return


	# De-stringify it into a tree form
	tree = html.fromstring(page.content) 

	# Get the title
	title = tree.xpath('//h1[@class="title"]/text()')

	# Get the author, date, and time that it was published
	extraInformation = tree.xpath('//div[@class="over"]/div/text()')

	# Get all the tags that start with <p> and end with </p> inside of the over class 
	pTag = tree.xpath('//div[@class="over"]/p')

	#this was for the fotoreportazhi articles
	'''
	if len(pTag) == 0:
		pTag = tree.xpath('//div[@class="over"]/div[@class="photo_body"]/p')
	'''
	# Array of words
	totalInformationSplit = []

	# Extract the text content within those tags, no matter how nested, split it by spaces, then dump it into an array
	for x in range(len(pTag)):
		split = pTag[x].text_content().split(' ')
		for y in range(len(split)):
			totalInformationSplit.append(split[y])

	# If there is no information on the article then just back out and assume there isn't an article to process
	#make this do something later
	if len(extraInformation) == 0:
		print "No article found"
		return

	# Split the time and date
	timeDate = extraInformation[0].split(' ')

	# Strip out the ending white space characters, for some reason some articles that were technically the same name has whitespaces at the end

	while title[0][-1] == u' ' or title[0][-1] == u' ':
		title[0] = title[0][:-1]

	# Assign to an easy to use map
	preliminaryInformation = {	
								'title':  u''.join(title[0]),  
								'author': extraInformation[1],
								'p_date': timeDate[0], 
								'p_time': timeDate[1],
								'a_date': time.strftime("%d/%m/%Y"), 
								'a_time': time.strftime("%H:%M")
							 }

	print "\n"
	print "Title          : " + preliminaryInformation['title']
	print "Author         : " + preliminaryInformation['author'] + "\n"
	print "Date Published : " + preliminaryInformation['p_date']
	print "Time Published : " + preliminaryInformation['p_time'] + "\n"
	print "Date Accessed  : " + preliminaryInformation['a_date']
	print "Time Accessed  : " + preliminaryInformation['a_time'] + "\n"

	poolSema.acquire()
	connection = sqlite3.connect('RussianWordNet.db')
	db = connection.cursor()
	db.execute("SELECT ID FROM Articles WHERE Title = ?", [preliminaryInformation["title"]])
	#check for names already take
	fetch = db.fetchone()
	if fetch is not None:
		poolSema.release() 
		connection.close()
		return
	poolSema.release() 
	connection.close()

	# Save the article for internal archiving 
	filename = saveArticleToFile(page.content, preliminaryInformation["title"], preliminaryInformation["p_date"])

	#i don't think this is being used anymore, but I don't want to remove it prematurely
	# Honorifics array to hold abbreviations and abbreviations that we will need to analyze sentence terminals
	abbreviations = [u'гг.', u'кВт.ч.', u'МВт.', u'млрд.', u'млн.', u'тонн.', u'тыс.']

	# This will hold all of our sentences
	sentenceArray = []

	# Initialize the sentence variable and the lastWord ()
	sentence = ""

	# Reconstruct the sentences
	for x in range(len(totalInformationSplit)):
		# This needs to be done by stripping out only alpha chars and then have those
		word = stripAlphaChars(totalInformationSplit[x])
		#word = totalInformationSplit[x].replace(u'«', u'').replace(u'»', u'').replace(u' ', u'').replace(u' ', u'')

		# Get the length of the word
		lengthOfWord = len(word)

		# Get the last character by getting the [last - 1 : last] substring
		lastChar = word[lengthOfWord - 1 : lengthOfWord]

		# Replace the '!', and '?' that may have been before a '.'
		word = word.replace('!', '').replace('?', '')
		# Check if that last char is a period
		if lastChar == u'.':
			# If it isnt a word then assume that it is not the end of a sentence
			if not russianDictionary.check(word):
				
				# This was producing some unwanted and unexpected results
				'''
				# If it does happen to be a word in the custom words then it is a word
				if word.replace('.', u'').replace(u'…', u'') in customWords:
					sentenceArray.append(sentence + totalInformationSplit[x])
					sentence = ""
				# If not just treat it as if it was not a word
				else:
					sentence += totalInformationSplit[x] + " "
				'''

				if word in abbreviations:
					print word

				# make something more general for the customWords detection later
				if word in abbreviations or (len(word.replace(u'.', u'')) < 3 and not hasNumbers(word)):
					sentence += totalInformationSplit[x] + " "
				else:
					sentenceArray.append(sentence + totalInformationSplit[x])
					sentence = ""

			elif word in abbreviations:
				sentence += totalInformationSplit[x] + " "
			# Else it might be just a single letter, in which case for now we will assume 
			# that they are single letter representing the first initial of someones name
			else:
				# If it is just two characters, i.e, a letter and a period
				# Grammatical stucture of Russian does not allow the sentence to be terminated with a singular character
				# and thus this means it must be an initial
				if len(totalInformationSplit[x]) < 3:
					sentence += totalInformationSplit[x] + " "
				#need an elif to help with the logic here when we get something that is an abbreviation for 
				#something that is a word but isn't denoting the end of the sentence 
				else:
				# Else assume that the terminal is the ending of a sentence
					sentenceArray.append(sentence + totalInformationSplit[x])
					sentence = ""
		# If it is one of the terminals then it is automatically the ending of a sentence
		elif lastChar in terminals:
			sentenceArray.append(sentence + totalInformationSplit[x])
			sentence = ""
		# Else just add it to the sentence
		else:
			sentence += totalInformationSplit[x] + " "
			
	# At this point, sentence should be empty, but there could be something in it, if I figure out that we want the end
	# of the sentence that doesn't close with a terminal then I'll add it back
	#sentenceArray.append(sentence + totalInformationSplit[x])


	# Analyze a piece of it to see if it is similar structurally to name and then make some assumptions
	# Machine learning?

	# Have a problem with sentences like the below
	'''
	Problems with sentences like:

	Уважаемый Президент! Зная о Вашем особом отношении к театральному искусству, русскому языку и русской 
	культуре, мы обращаемся к Вам, ибо Вы -наша последняя надежда: не дайте умереть 
	нашему любимому театру, который делал и продолжает делать так много для развития 
	как русской, так и национальной драматургии.
	'''

	#check if we already have the title in there for the photoreportazh
	poolSema.acquire()
	connection = sqlite3.connect('RussianWordNet.db')
	db = connection.cursor()
	db.execute("INSERT INTO Articles (Title, Author, PublishDate, PublishTime, AccessDate, AccessTime, SentenceCount, File, Link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [preliminaryInformation["title"], preliminaryInformation['author'], preliminaryInformation['p_date'], preliminaryInformation['p_time'], preliminaryInformation['a_date'], preliminaryInformation['a_time'], len(sentenceArray), filename, article])
	#connection.commit()
	# Print out the entire array of reconstructed sentences
	#print "\n\n"
	#db.execute("SELECT ID FROM Articles WHERE Title=?", [preliminaryInformation["title"]])
	#ID = db.fetchone()
	#print ID

	for x in range(len(sentenceArray)):
		print sentenceArray[x]
		print x
		
		db.execute("INSERT INTO Sentences VALUES ((SELECT ID FROM Articles WHERE Title=?), ?, ?)", [preliminaryInformation["title"], x, sentenceArray[x]])
		#db.execute("INSERT INTO Sentences VALUES (?, ?, ?)", [ID, x, sentenceArray[x]])
		
		print "\n"

	print "\n\n", len(sentenceArray), "sentences found.\n"
	connection.commit()
	connection.close()
	poolSema.release()

	
# node method, this will not be used for awhile, possibly deprecated in favor of the page method
'''
if len(sys.argv) == 1:
	x = 225083
	while x < 225183:
		print 'http://news.tj/ru/node/%d' % x
		stripArticle('http://news.tj/ru/node/%d' % x)
		print '\n------------------------------------------------------------------------------------------------\n'
		x += 1
else:
	print '\n------------------------------------------------------------------------------------------------'
	print str(sys.argv[1])
	stripArticle(str(sys.argv[1]))
	print '\n------------------------------------------------------------------------------------------------'
'''

# http://www.news.tj/ru/news?page=2868
# is the last page that we can fetch


# Start of program

#need to check whether it exists or not
connection = sqlite3.connect('RussianWordNet.db')
db = connection.cursor()
db.execute("CREATE TABLE Articles (ID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT, Author TEXT, PublishDate TEXT, PublishTime TEXT, AccessDate TEXT, AccessTime TEXT, SentenceCount INTEGER, File TEXT, Link TEXT)")
#we need to have jagged stuff but idk how to think right now
#also need a unique id
db.execute("CREATE TABLE Sentences (A_ID INTEGER, S_ID INTEGER, Sentence TEXT, FOREIGN KEY (A_ID) REFERENCES Articles(ID), PRIMARY KEY (A_ID, S_ID))")
connection.commit()
#connection.close()
# Page method of retrieving the articles, this will be ther preferred method from now on
x = 0
# make that read from a file to load the last page that was fetched
threadPool = Pool(10)

if len(sys.argv) == 1:
	#while True:

	linkPages = []

	for x in range(0, 35):
		linkPages.append("http://www.news.tj/ru/news?page=%d" % x)


	results = threadPool.map(getLinks, linkPages)
	threadPool.close()
	threadPool.join()

	for y in range(len(results)):
		for z in range(len(results[y])):
			pagesList.append('http://www.news.tj' + results[y][z])

	'''
	print "http://www.news.tj/ru/news?page=%d" % x
	articleList = requests.get("http://www.news.tj/ru/news?page=%d" % x)
	tree = html.fromstring(articleList.content) 
	title = tree.xpath('//div[@id="content"]//div[@class="views-field-title"]//a/@href')

		for y in range(len(title)):
			poolArray.append('http://news.tj' + title[y])

		y = 0
		print len(title)
		while y < len(title):
			print y
			print 'http://news.tj' + title[y]
			#stripArticle('http://news.tj' + title[y])
			poolArray = ['http://news.tj' + title[y]]
			for z in range(0, 10):
				if (y + 1) < len(title):
					poolArray.append('http://news.tj' + title[y + 1])
					print y
					y += 1
				else:
					y += 1
			threadPool.map(stripArticle, poolArray)
		
			print '\n------------------------------------------------------------------------------------------------\n'
			

		#x += 1
	'''
	threadPool = Pool(8)
	threadPool.map(stripArticle, pagesList)
	threadPool.close()
	threadPool.join()

else:
	print '\n------------------------------------------------------------------------------------------------'
	print str(sys.argv[1])
	stripArticle(str(sys.argv[1]))
	print '\n------------------------------------------------------------------------------------------------'
	#connection.commit()
connection.close()

