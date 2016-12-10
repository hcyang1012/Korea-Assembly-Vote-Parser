# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import json
from vec import Vec
import csv
from utils import listToSet
from utils import BillLog


billLog = BillLog()




def getAssemblyList():
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

def getVoteList(url):
	data = requests.get(url)
	js = json.loads(data.text);
	voteList = js['resListVo']
	requestURL = "http://likms.assembly.go.kr/bill/billVoteResultDetail.do?"
	urls = []
	for vote in voteList:
		resultURL = "%sidMaster=%s&billId=%s&billNo=%s" % (requestURL, vote["idmaster"], vote["billid"], vote["billno"])
		billLog.billList[vote['billno']] = vote['billname']
		urls.append(resultURL)
	return urls

def getVoteResults(assemblyList):
	result = []
	for url in assemblyList:
		result = result +  getVoteList(url)

	return result

def addMember(newMemberID, memberName, billNo, value):
	if newMemberID not in billLog.memberIDDict.keys():
		billSet = listToSet(billLog.billList.keys())
		billLog.members[newMemberID] = Vec(billSet,{})
		billLog.memberIDDict[newMemberID] = memberName

	billLog.members[newMemberID][billNo] = value;

def parseVote(url):
	data = requests.get(url)
	soup = BeautifulSoup(data.text.encode('utf-8'),'html.parser')
	p=re.compile('\d+')
	billNo = url[-7:]

	# approve
	for link in soup.select("#tbody > tr > td > a"):
		href = link.get('href')
		memberName = link.get_text()
		memberID = p.findall(href)[0]
		addMember(memberID, memberName, billNo, 1)

	# negative
	for link in soup.select("#tbody1 > tr > td > a"):
		href = link.get('href')
		memberName = link.get_text()
		memberID = p.findall(href)[0]
		addMember(memberID, memberName, billNo, -1)	
	# give up
	for link in soup.select("#tbody2 > tr > td > a"):
		href = link.get('href')
		memberName = link.get_text()
		memberID = p.findall(href)[0]
		addMember(memberID, memberName, billNo, 0)


def getVoteLog():
	voteList = getVoteResults(getAssemblyList())
	for vote in voteList:
		parseVote(vote)


def saveVoteLog(filename):
	with open(filename, 'w') as csv_file:
		writer = csv.writer(csv_file)
		for memberID in billLog.memberIDDict.keys():
			for billNo in billLog.billList.keys():
				writer.writerow([billLog.memberIDDict[memberID], memberID, billNo, billLog.billList[billNo], billLog.members[memberID][billNo]])

getVoteLog()
saveVoteLog('result.csv')