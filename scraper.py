from lxml import html
import requests

page = requests.get('http://news.tj/ru/news/teatr-mayakovskogo-za-chto-smertnaya-kazn')
tree = html.fromstring(page.content)

extraInformation = tree.xpath('//div[@class="over"]/div/text()')
pTag = tree.xpath('//div[@class="over"]/p')

p_content = [p.text_content() for p in pTag]
print '\n\n\n'

for x in range(len(extraInformation)):
	print extraInformation[x] + '\n'

print '\n\n\n'

for x in range(len(p_content)):
	print p_content[x] + '\n'