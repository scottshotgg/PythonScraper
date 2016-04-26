from lxml import html
import requests

page = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')
tree = html.fromstring(page.content)

title =  tree.xpath('//h1[@class="title"]/text()')
extraInformation = tree.xpath('//div[@class="over"]/div/text()')
pTag = tree.xpath('//div[@class="over"]/p')

p_content = [p.text_content() for p in pTag]

print '\n' + title[0]

print '\n\n'

for x in range(len(extraInformation)):
	print extraInformation[x] + '\n'

print '\n'

for x in range(len(p_content)):
	print p_content[x] + '\n'