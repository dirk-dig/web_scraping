from bs4 import BeautifulSoup as b
import urllib2 as u

url = "http://www.nikkei.com/"
html = u.urlopen(url)
soup = b(html, "html5lib")

soup.find("img")

