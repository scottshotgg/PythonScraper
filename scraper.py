# -*- coding: utf-8 -*-

from lxml import html
import requests
import time
import enchant

d = enchant.Dict("ru_RU")
print d.check(u'бесконечно')

customWords = [u'ССР', u'Лахути', u'Яншина', u'Маяковского', u'Калигула', u'М.Турсун-заде', u'Макбет']
variable = u'Калигула' in customWords
print variable

# Input news.tj article
page = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')

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

sentence = ""
lastWord = 0
# Reconstruct the sentences
#for x in range(len(totalInformationSplit)):
length = len(totalInformationSplit)
x = 0
while x < length:
	# Get the length of the word
	lengthOfWord = len(totalInformationSplit[x])
	# Get the last character by getting the [last - 1 : last] substring
	lastChar = totalInformationSplit[x][lengthOfWord - 1 : lengthOfWord]
	word = totalInformationSplit[x].replace(u'«', u'').replace(u'»', u'')
	print word
	# Check if that last char is a period
	if(lastChar == '.'):
		oneBeforeLastChar = word[lengthOfWord - 2 : lengthOfWord - 1]
		#twoBeforeLastChar = totalInformationSplit[x][lengthOfWord -3 : lengthOfWord - 2]
		#threeBeforeLastChar = totalInformationSplit[x][lengthOfWord -4 : lengthOfWord - 3]
		# do something with these later

		# cannot detect words that are not officially words but may be slang inside of quotes
		# for instance Калигула

		print totalInformationSplit[x]
		#if(oneBeforeLastChar.isupper()):
			# Instead of adding, check whether it is a named entity
			#sentence += totalInformationSplit[x] + " "
		if(not(d.check(word))):
			word = word.replace('.', u'').replace(u'…', u'')
			if((word in customWords)):
				sentenceArray.append(sentence + totalInformationSplit[x])
				sentence = ""
				lastWord = 1
				x += 1
			else:
			#sentence += totalInformationSplit[x] + " " + totalInformationSplit[x + 1] + " "
			# Sometimes this will trigger for initials like A, B, 
			#if(len(totalInformationSplit[x]) > 2):
				sentence += totalInformationSplit[x] + " "
				lastWord = 0
			#else:
			#	sentenceArray.append(sentence)
			#	sentence = ""
			#	sentence += totalInformationSplit[x] + " "
			#x += 2
			#scontinue
		# If is is a period then check if it is in the array of abbreviations
		#elif(len(word) == 2):
		#	sentence += totalInformationSplit[x] + " "
		elif(word in abbreviations):
			# If it is in the abbreviations array then add it to the sentence as a part of the sentence
			sentence += totalInformationSplit[x] + " "
			lastWord = 0
		else:
			if(len(totalInformationSplit[x]) < 3):
				sentence += totalInformationSplit[x] + " "
				lastWord = 0
			else:
			# Else assume that the terminal is the ending of a sentence
				sentenceArray.append(sentence + totalInformationSplit[x])
				sentence = ""
				lastWord = 1
	# If it is an ! or a ? then it is automatically the ending of a sentence
	elif(lastChar == '!' or lastChar == '?' or lastChar == u'…'):
		sentenceArray.append(sentence + totalInformationSplit[x])
		sentence = ""
		lastWord = 1
	# Else just add it to the sentence
	else:
		sentence += totalInformationSplit[x] + " "
		lastWord = 0

	x += 1
	#print sentence
	#print lastWord

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
