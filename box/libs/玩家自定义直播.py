#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import re
from urllib import request, parse
import urllib
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
class Spider(Spider):  # 元类 默认的元类 type
	# TvSource='https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/list.txt'#可根据自己需要换成其它影视仓直播源
	#本地源
	TvSource=r'file:/storage/emulated/0/box/lib/TV.txt'
	cateManual={}
	def getName(self):
		return "直播"
	def __init__(self,extend=""):
		htmlTxt=self.custom_readSource(self.TvSource)
		self.TvSourceTxt=htmlTxt.split('\n')
		self.cateManual=self.custom_classification()
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		classes = []
		for k in self.cateManual:
			classes.append({
				'type_name':k,
				'type_id':self.cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		result = {
			'list':[]
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		videos = self.custom_list(tid)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 1
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		result = {}
		aid = array[0].split('###')
		logo = aid[2]
		tid = aid[1]
		title = aid[0]
		vodItems=[]
		vod_play_from=['高级玩家线路',]
		vod_play_url=[]
		if tid=='0':
			joinStr = "#".join(self.custom_EpisodesList_1(title))
		else:
			joinStr = "#".join(self.custom_EpisodesList(tid,title))
		vodItems.append(joinStr)
		vod_play_url = "$$$".join(vodItems)

		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":tid,
			"vod_year":"",
			"vod_area":"",
			"vod_remarks":"",
			"vod_actor":"",
			"vod_director":"鸟叔玩家特许",
			"vod_content":''
		}
		vod['vod_play_from'] =  "$$$".join(vod_play_from)
		vod['vod_play_url'] = vod_play_url
		result = {
			'list':[
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		videos=self.custom_list_search(key)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		result["parse"] = 0#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = id.replace('井号','#')
		result['jx'] = 0#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result


	config = {
		"player": {},
		"filter": {}
		}
	header = {}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
	#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt

	#分类取结果
	def custom_list(self,key):
		videos = []
		index=self.grouping.get(key,0)
		if int(index)+1>len(self.TvSourceTxt):
			return videos
		img='http://photo.16pic.com/00/23/48/16pic_2348904_b.jpg'
		# img='/storage/emulated/0/tvbox/中央频道.jpg'
		temporary=[]
		for i in range(index+1,len(self.TvSourceTxt)):
			try:
				if self.TvSourceTxt[i].find('#genre#')>-1:
					break
				tem=self.TvSourceTxt[i].split(',')
				if len(tem)<2:
					continue
				title=tem[0]
				if temporary.count(title)==1:
					continue
				title=self.TvSourceTxt[i].split(',')[0]
				vod_id='{0}###{1}###{2}'.format(title,key,img)
				temporary.append(title)
				videos.append({
					"vod_id":vod_id,
					"vod_name":title,
					"vod_pic":img,
					"vod_remarks":''
				})
			except:
				pass
		return videos
		#访问网页
	def custom_webReadFile(self,urlStr,header=None,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName,'ignore')
		return html
	#取集数
	def custom_EpisodesList(self,tid,title):
		videos = []
		index=self.grouping.get(tid,-1)
		temporary=[]
		for i in range(index+1,len(self.TvSourceTxt)):
			try:
				if self.TvSourceTxt[i].find('#genre#')>-1:
					break
				tem=self.TvSourceTxt[i].split(',')
				if len(tem)<2:
					continue
				name=tem[0]
				url=tem[1].replace('\r','')
				if len(url) == 0 or temporary.count(url)==1 or name!=title or url.find('video://')>-1:
					continue
				temporary.append(url)
				videos.append(title+"$"+url.replace('#','井号'))
			except:
				pass
		return videos
	#取集数
	def custom_EpisodesList_1(self,title):
		videos = []
		temporary=[]
		for v in self.TvSourceTxt:
			try:
				if v.find('#genre#')>-1:
					continue
				tem=v.split(',')
				if len(tem)<2:
					continue
				name=tem[0]
				url=tem[1].replace('\r','')
				if len(url) == 0 or temporary.count(url)==1 or name!=title or url.find('video://')>-1:
					continue
				temporary.append(url)
				# print(url)
				videos.append(title+"$"+url.replace('#','井号'))
			except:
				pass
		return videos
	def custom_list_search(self,key):
		videos = []
		img='http://photo.16pic.com/00/23/48/16pic_2348904_b.jpg'
		for v in self.TvSourceTxt:
			temporary=v.split(',')
			if len(temporary)<2 or temporary[0].upper().find(key.upper())<0 or v.find('#genre#')>-1:
					continue
			title =temporary[0]
			videos.append({
				"vod_id":"{0}###{1}###{2}".format(title,'0',img),
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		return videos
	TvSourceTxt=[]
	grouping={}
	#取分类
	def custom_classification(self):
		temporary=[v for v in self.TvSourceTxt if re.search('#genre#', v)]
		temporaryClass={}
		for vod in temporary:
			if vod.find('#genre#')>0:
				
				i=self.TvSourceTxt.index(vod)
				t=self.custom_emoji(vod.replace('\r','')).replace(',#genre#','')
				self.grouping[t]=i
				
				temporaryClass[t]=t
		return temporaryClass
	def custom_emoji(self,desstr, restr=''):
	    # 过滤表情
	    try:
	        co = re.compile(u'[\U00010000-\U0010ffff]')
	    except re.error:
	        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
	    return co.sub(restr, desstr)
	def custom_readSource(self,sourcePath):
		if sourcePath.find('file:')==0:
			return self.custom_readLocalFile(sourcePath[5:])
		else:
			return self.custom_webReadFile(urlStr=sourcePath)
	def custom_readLocalFile(self,filePath):
		fileTarget = open(filePath,'r',encoding='utf-8')#encoding='utf-8'
		sourceTxt = fileTarget.read(-1)
		fileTarget.close()
		return sourceTxt
