from lxml import html
import requests

page = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')
tree = html.fromstring(page.content)

title =  tree.xpath('//h1[@class="title"]/text()')
extraInformation = tree.xpath('//div[@class="over"]/div/text()')
pTag = tree.xpath('//div[@class="over"]/p')

p_content = [p.text_content() for p in pTag]

totalInformation = [title[0]]

'''
print '\n' + title[0]

print '\n\n'
'''
# add that in to see if we can detect that

for x in range(len(extraInformation)):
	totalInformation.append(extraInformation[x])
	#print extraInformation[x] + '\n'

print '\n'

for x in range(len(p_content)):
	totalInformation.append(p_content[x])
#print p_content[x] + '\n' 

#print totalInformation



#print totalInformation

#layer = title[0].split(' ')
totalInformationSplit = []
z = 0

for x in range(len(totalInformation)):
	#print totalInformation[x]
	split = totalInformation[x].split(' ')
	for y in range(len(split)):
		totalInformationSplit.append(split[y])
		'''
		print '\n'
		print y
		print z
		z += 1
		print '\n'
		'''

for x in range(len(totalInformationSplit)):
	print totalInformationSplit[x]