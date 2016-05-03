# -*- coding: utf-8 -*-

from lxml import html
import requests
import time
import enchant
import sys
#import nltk

# Saving these
	#article = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')
	#article = requests.get('http://news.tj/ru/news/na-zadvorkakh-promyshlennogo-giganta-ili-v-kakikh-usloviyakh-zhivut-tekstilshchiki')
	#article = requests.get('http://news.tj/ru/news/aviakompaniya-somon-eir-otkryla-novyi-reis-dushanbe-kabul')
	#article = requests.get('http://news.tj/ru/node/225178')
	#article = requests.get('http://news.tj/ru/news/nochnaya-paskhalnaya-sluzhba-v-dushanbe-foto')



# Initialize a custom words array to hold words that are not in the dictionary, like names and other stuff
#not using this anymore
customWords = [
				u'ССР', u'Лахути', u'Яншина', u'Маяковского', u'Калигула', u'МТурсун-заде', 
				u'Макбет', u'Душанбе-Лахор-Душанбе', u'Эйр'
			  ]

# Terminal symbols
terminals = ['!', '?', u'…', u'.']

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

def hasNumbers(word):
	return any(char.isdigit() for char in word)

def stripArticle(article):
	# Initialize the dictionary
	russianDictionary = enchant.Dict("ru_RU")

	#e = enchant.Dict("en_US")
	#print e.check(u'Lahore')

	# Just some stuff that I am using during debug to test some words
	#print russianDictionary.check(u'Эйр')
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
	title =  tree.xpath('//h1[@class="title"]/text()')

	# Get the author, date, and time that it was published
	extraInformation = tree.xpath('//div[@class="over"]/div/text()')

	# Get all the tags that start with <p> and end with </p> inside of the over class 
	pTag = tree.xpath('//div[@class="over"]/p')

	# Array of words
	totalInformationSplit = []

	# Extract the text content within those tags, no matter how nested, split it by spaces, then dump it into an array
	for x in range(len(pTag)):
		split = pTag[x].text_content().split(' ')
		for y in range(len(split)):
			totalInformationSplit.append(split[y])

	# If there is no information on the article then just back out
	#make this do something later
	if len(extraInformation) == 0:
		print "No article found"
		return

	# Split the time and date
	timeDate = extraInformation[0].split(' ')

	# Assign to an easy to use map
	preliminaryInformation = {	
								'title': title[0],  
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

	# Honorifics array to hold abbreviations and abbreviations that we will need to analyze sentence terminals
	abbreviations = [u'гг.']

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

				if len(word.replace(u'.', u'')) < 3 and not hasNumbers(word):
					sentence += totalInformationSplit[x] + " "
				else:
					sentenceArray.append(sentence + totalInformationSplit[x])
					sentence = ""

			# Else it might be just a single letter, in which case for now we will assume 
			# that they are single letter representing the first initial of someones name
			else:
				# If it is just two characters, i.e, a letter and a period
				# Grammatical stucture of Russian does not allow the sentence to be terminated with a singular character
				# and thus this means it must be an initial
				if len(totalInformationSplit[x]) < 3:
					sentence += totalInformationSplit[x] + " "
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

	# Print out the entire array of reconstructed sentences
	print "\n\n"
	for x in range(len(sentenceArray)):
		print sentenceArray[x]
		print "\n"

	print len(sentenceArray), "sentences found.\n"


# Start of program


#make Input news.tj article

if len(sys.argv) == 1:
	x = 225083
	while x < 225183:
		print 'http://news.tj/ru/node/%d' % x
		stripArticle('http://news.tj/ru/node/%d' % x)
		print '\n------------------------------------------------------------------------------------------------'
		x += 1
else:
	print '\n------------------------------------------------------------------------------------------------'
	print str(sys.argv[1])
	stripArticle(str(sys.argv[1]))
	print '\n------------------------------------------------------------------------------------------------'

