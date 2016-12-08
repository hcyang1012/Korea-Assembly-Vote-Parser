# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import json
from vec import Vec
import csv


billList = set([])
memberIDSet = set([])
members = {}

def getVoteList():
	targetURL = "http://likms.assembly.go.kr/bill/billVoteResult.do"
	data = requests.get(targetURL)
	soup = BeautifulSoup(data.text.encode('utf-8'),'html.parser');
	urls = []
	requestURL = "http://likms.assembly.go.kr/bill/billVoteResultListAjax.do"
	p=re.compile('\d+')
	for link in soup.select('.s3depth'):
		funcCall = link.get('onclick')
		params = p.findall(funcCall)
		resultURL = "%s?currentsCd=%s&currentsCt=%s&searchYn=ABC" % (requestURL,params[2],params[3])
		urls.append(resultURL)
	return urls

def parseVoteList(url):
	data = requests.get(url)
	js = json.loads(data.text);
	voteList = js['resListVo']
	requestURL = "http://likms.assembly.go.kr/bill/billVoteResultDetail.do?"
	urls = []
	for vote in voteList:
		resultURL = "%sidMaster=%s&billId=%s&billNo=%s" % (requestURL, vote["idmaster"], vote["billid"], vote["billno"])
		billList.add(vote['billno'])
		urls.append(resultURL)
	return urls

def getVoteResultList(urls):
	result = []
	for url in urls:
		result = result +  parseVoteList(url)
	return result

def addMember(newMemberID, billNo, value):
	if newMemberID not in memberIDSet:
		newMember = Vec(billList,{})
		memberIDSet.add(newMemberID)
		members[newMemberID] = newMember;
	members[newMemberID][billNo] = value;


def parseVote(url):
	data = requests.get(url)
	soup = BeautifulSoup(data.text.encode('utf-8'),'html.parser')
	p=re.compile('\d+')
	billNo = url[-7:]

	# approve
	for link in soup.select("#tbody > tr > td > a"):
		href = link.get('href')
		memberID = p.findall(href)[0]
		addMember(memberID,billNo, 1)

	# negative
	for link in soup.select("#tbody1 > tr > td > a"):
		href = link.get('href')
		memberID = p.findall(href)[0]
		addMember(memberID,billNo, -1)	
	# give up
	for link in soup.select("#tbody2 > tr > td > a"):
		href = link.get('href')
		memberID = p.findall(href)[0]
		addMember(memberID,billNo, 0)
	


voteURLList = getVoteResultList(getVoteList())
for vote in voteURLList:
	parseVote(vote)
with open('dict.csv', 'w') as csv_file:
	writer = csv.writer(csv_file)
	for memberID in memberIDSet:
		for billNo in billList:
			writer.writerow([memberID, billNo, members[memberID][billNo]])
#parseVote("http://likms.assembly.go.kr/bill/billVoteResultDetail.do?billId=PRC_M1E6M0C9J0Z6Z1Y1X0F3Y4I8J8D2R2&idMaster=103186&billNo=2002157")
#data = requests.get(voteURLList[0])
#print(data.text.encode('utf-8'))
