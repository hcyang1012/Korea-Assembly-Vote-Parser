# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re


def getVoteList():
	targetURL = "http://likms.assembly.go.kr/bill/billVoteResult.do"
	data = requests.get(targetURL)
	soup = BeautifulSoup(data.text.encode('utf-8'),'html.parser');
	urls = []
	requestURL = "http://likms.assembly.go.kr/bill/billVoteResultListAjax.do"
	for link in soup.select('.s3depth'):
		funcCall = link.get('onclick')
		p=re.compile('\d+')
		params = p.findall(funcCall)
		resultURL = requestURL + "?currentsDt=" + str(params[3])
		urls.append(resultURL)
	return urls
"""
def getVoteResultList(urls):
	for vote in urls:
		data = requests.get(vote)
		soup = BeautifulSoup(data.text.encode('utf-8'),'html.parser')
		urls = []
		for link in soup.select('.alignL'):
			print(link)
			#funcCall = link.get('href')
			#print(funcCall)
"""


voteList = getVoteList()
print(voteList)
#getVoteResultList(voteList)