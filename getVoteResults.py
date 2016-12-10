# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import json
from vec import Vec
import csv
from utils import listToSet


billList = {}
billSet = set({})
memberIDDict = {}
members = {}

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
		resultURL = "%sidMaster=%s&billNo=%s&billId=%s" % (requestURL, vote["idmaster"], vote["billno"], vote["billid"])
		billList[vote['billid']] = vote['billname']
		urls.append(resultURL)
	return urls

def getVoteResults(assemblyList):
	result = []
	for url in assemblyList:
		result = result +  getVoteList(url)

	return result

def addMember(newMemberID, memberName, billSet, billNo, value):
	if newMemberID not in memberIDDict.keys():
		newMember = Vec(billSet,{})
		memberIDDict[newMemberID] = memberName
		members[newMemberID] = newMember;		
	members[newMemberID][billNo] = value;


def parseVote(url, billSet):
	data = requests.get(url)
	soup = BeautifulSoup(data.text.encode('utf-8'),'html.parser')
	p=re.compile('\d+')
	billNo = url[-34:]

	# approve
	for link in soup.select("#tbody > tr > td > a"):
		href = link.get('href')
		memberName = link.get_text()
		memberID = p.findall(href)[0]
		addMember(memberID, memberName, billSet, billNo, 1)

	# negative
	for link in soup.select("#tbody1 > tr > td > a"):
		href = link.get('href')
		memberName = link.get_text()
		memberID = p.findall(href)[0]
		addMember(memberID, memberName, billSet, billNo, -1)	
	# give up
	for link in soup.select("#tbody2 > tr > td > a"):
		href = link.get('href')
		memberName = link.get_text()
		memberID = p.findall(href)[0]
		addMember(memberID, memberName, billSet, billNo, 0)


def getVoteLog():
	voteList = getVoteResults(getAssemblyList())
	billSet = listToSet(billList.keys())
	for vote in voteList:
		parseVote(vote,billSet)

def saveVoteLog(filename):
	with open(filename, 'w') as csv_file:
		writer = csv.writer(csv_file)
		for memberID in memberIDDict.keys():
			for billNo in billList.keys():
				writer.writerow([memberIDDict[memberID], memberID, billNo, billList[billNo], members[memberID][billNo]])

getVoteLog()
saveVoteLog('result.csv')