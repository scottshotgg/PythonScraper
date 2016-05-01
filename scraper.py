# -*- coding: utf-8 -*-

from lxml import html
import requests
import time
import enchant

# This function strips out only the alphacharacters and the period
def stripAlphaChars(word):
	russianAlphaChars =['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 
						'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 
						'я', 'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 
						'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ' 'Ы', 'Ь', 'Э',
						'Ю', 'Я']
	x = 0
	while x < len(word):
		if not(word[x] in russianAlphaChars) or word[x] == u'.':
			word = word.replace(word[x], u'')
			x -= 1
		x += 1
	print "\"" + word + "\""
	return word

# Initialize the dictionary
d = enchant.Dict("ru_RU")

# Initialize a custom words array to hold words that are not in the dictionary, like names and other stuff
customWords = [u'ССР', u'Лахути', u'Яншина', u'Маяковского', u'Калигула', u'МТурсун-заде', u'Макбет']

# Terminal symbols
terminals = ['!', '?', u'…']

# Just some stuff that I am using during debug to test some words
print d.check(u'ученья..')
print u'Калигула' in customWords

if(u' ' == u' '):
	print "yss"

# Input news.tj article
page = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')
#page = requests.get('http://news.tj/ru/node/225178')

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
	#word = stripAlphaChars(totalInformationSplit[x])
	word = totalInformationSplit[x].replace(u'«', u'').replace(u'»', u'').replace(u' ', u'').replace(u' ', u'')

	# Get the length of the word
	lengthOfWord = len(word)

	# Get the last character by getting the [last - 1 : last] substring
	lastChar = word[lengthOfWord - 1 : lengthOfWord]
	word = word.replace('!', '').replace('?', '')
	# Check if that last char is a period
	if(lastChar == u'.'):
		# If its not a word the assume that it is not the end of a sentence
		if(not(d.check(word))):
			# If it does happen to be a word in the custom words then it is a word
			if((word.replace('.', u'').replace(u'…', u'') in customWords)):
				sentenceArray.append(sentence + totalInformationSplit[x])
				sentence = ""
			# If not just treat it as if it was not a word
			else:
				sentence += totalInformationSplit[x] + " "
		# Else it might be just a single letter, in which case for now we will assume 
		# that they are single letter representing the first initial of someones name
		else:
			# If it is just two characters, i.e, a letter and a period
			if(len(totalInformationSplit[x]) < 3):
				sentence += totalInformationSplit[x] + " "
			else:
			# Else assume that the terminal is the ending of a sentence
				sentenceArray.append(sentence + totalInformationSplit[x])
				sentence = ""
	# If it is an ! or a ? or an … then it is automatically the ending of a sentence
	elif(lastChar in terminals):
		sentenceArray.append(sentence + totalInformationSplit[x])
		sentence = ""
	# Else just add it to the sentence
	else:
		sentence += totalInformationSplit[x] + " "

# At this point, sentence should be empty


# Having problems with Russian abbreviated names and initials, maybe we can try looking at the last name
# or atleast analyzing a piece of it to see if it is similar structurally to name and then make some assumptions
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
