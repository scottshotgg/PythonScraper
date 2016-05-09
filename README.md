#PythonScraper
This is a Python Scraper for news.tj.

You can use this by installing requests, lxml, enchant, and sqlite3:

"pip install " ,,,

Before running the program, we must include a Russian dictionary, and not just any, we need one that has the 'yo' (Ё, ё) included in the spelling
To do this, copy the included .dic and .aff files to "python2.7/site-packages/enchant/share/enchant/myspell"
If you are on OS X using the Brew installed version of Python, this directory will be "/usr/local/lib/python2.7/site-packages/enchant/share/enchant/myspell"

Then you are ready to run the program finally:
"python scraper.py"

For now, you will need to adjust in the code what parameters you want, these will be added later. If you just want to see one article, you can use the same command but also include a web address afterwards:
"python scraper.py http://www.news.tj/ru/news/match-tadzhikistan-bangladesh-rassudit-brigada-arbitrov-iz-sirii"

Afterwards, you should end up with a file called RussianWordNet.db - this is your database file that will serve as the keeper of all the data you have scraped.
You will also see a folder hierarchy starting with the root node of "Articles", this structure contains backups of all the articles that have been scraped.
