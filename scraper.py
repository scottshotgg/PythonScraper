# -*- coding: utf-8 -*-

from lxml import html
import requests
import time

# Input news.tj article
page = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')

# De stringify it into a tree form
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
							'a_date': time.strftime("%d/%m/%Y"), 
							'a_time': time.strftime("%H:%M"), 
							'p_date': timeDate[0], 
							'p_time': timeDate[1], 
							'author': extraInformation[1]
						 }

print "\n"
print "Title          : " + preliminaryInformation['title']
print "Author         : " + preliminaryInformation['author']+ "\n"
print "Date Published : " + preliminaryInformation['p_date']
print "Time Published : " + preliminaryInformation['p_time'] + "\n"
print "Date Accessed  : " + preliminaryInformation['a_date']
print "Time Accessed  : " + preliminaryInformation['a_time'] + "\n"
print "\n\n-------------------------------------------------------------------------------"


# Honorifics array to hold honorifics and abbreviations that we will need to analyze sentence terminals
honorificsArray = []

# This will hold all of our sentences
sentenceArray = []

sentence = ""

# Here is where we comb through and check the terminals
for x in range(len(totalInformationSplit)):
	# Get the length of the word
	lengthOfWord = len(totalInformationSplit[x])
	# Get the last character by getting the [last - 1 : last] substring
	lastChar = totalInformationSplit[x][lengthOfWord - 1 : lengthOfWord]
	# Check if that last char is a period
	if(lastChar == '.'):
		# If is is a period then check if it is in the array of honorifics
		if(totalInformationSplit[x] in honorificsArray):
			# If it is in the honorifics array then add it to the sentence as a part of the sentence
			sentence += totalInformationSplit[x] + " "
		else:
			# Else assume that the terminal is the ending of a sentence
			sentenceArray.append(sentence + totalInformationSplit[x])
			sentence = ""
	# If it is an ! or a ? then it is automatically the ending of a sentence
	elif(lastChar == '!' or lastChar == '?'):
			sentenceArray.append(sentence + totalInformationSplit[x])
			sentence = ""
	# Else just add it to the sentence
	else:
			sentence += totalInformationSplit[x] + " "

# At this point, sentence should be empty


'''
Problems with sentences like:

Уважаемый Президент! Зная о Вашем особом отношении к театральному искусству, русскому языку и русской 
культуре, мы обращаемся к Вам, ибо Вы -наша последняя надежда: не дайте умереть 
нашему любимому театру, который делал и продолжает делать так много для развития 
как русской, так и национальной драматургии.
'''


# Print out the entire array
print "\n\n"
for x in range(len(sentenceArray)):
	print sentenceArray[x]
	print "\n"
