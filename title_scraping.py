# -*- coding: utf-8 -*-

import urllib
from bs4 import BeautifulSoup

url = "https://arxiv.org/abs/1312.6199"
f = urllib.urlopen(url)
html = f.read().decode('utf-8')

soup = BeautifulSoup(html, "html.parser")

print(soup.title)        #<title>Remrinのpython攻略日記</title>