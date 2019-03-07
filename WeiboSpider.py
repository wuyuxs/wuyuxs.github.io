
import os
import re
import requests
import sys
import traceback
import time
import json
import csv
from datetime import datetime
from datetime import timedelta
from lxml import etree

class Spider():
	def __init__(self):  #初始化
		# 后半段加入自己的cookies
		yourCookies = 'SINAGLOBAL=3369970715997.819.1506023482040; _ga=GA1.2.1441703059.1524549590; login_sid_t=3aae7ea50a6b1609a6156e3cee05c03b; cross_origin_proto=SSL; Ugrow-G0=968b70b7bcdc28ac97c8130dd353b55e; _s_tentry=-; Apache=9546625150565.959.1551648287916; ULV=1551648287931:21:1:1:9546625150565.959.1551648287916:1546444676335; SSOLoginState=1551648290; un=18792566187; TC-Page-G0=1e758cd0025b6b0d876f76c087f85f2c; YF-Page-G0=0f25bf37128de43a8f69dd8388468211; YF-V5-G0=f0aa2e6d566ccd1c288fae19df01df56; WBtopGlobal_register_version=ae9a9ec008078a68; wvr=6; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF_E4MIHRogX9SQpkHRnmGu5JpX5KMhUgL.Fozc1hqfSonfSKz2dJLoI0YLxKqL1KMLBK5LxKnLB-qLB-BLxK-LBo5L12qLxKML1KBL1-qLxKnLBKqL1h2LxK-L122LBK5LxKqLBozLBo.t; ALF=1583516190; SCF=AoSwAFwtuPuWp1D92s1l5h0IykLPhl4OYOnZGEowOEtmFF4RbWZGoZwYhBX24bY82hS2HyfEP2XUoPtdW2wciBQ.; SUB=_2A25xhSbzDeRhGeRI41QU9ibJzj6IHXVS8x87rDV8PUNbmtBeLRGmkW9NUsuUYX6d_pxWwHEKaWNMpBqiSakFDY80; SUHB=0HTglA8Q6fqWuC; wb_view_log_2686568552=1440*9001; webim_unReadCount=%7B%22time%22%3A1551980264324%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A0%7D'
		self.cookies = {"Cookie": yourCookies}  # 将your cookie替换成自己的cookie
		self.id = 0				#微博ID
		self.target = {}		#同行微博
		self.read_num = 0		#阅读数
		self.retweet_num = 0	#转发数
		# Can't find these status
		# self.tweet_num = 0
		# self.liked_num = 0
		# self.comment_num = 0
		self.fans_increase = 0	#粉丝增加
		self.fans_decrease = 0	#粉丝减少
		self.fans_overall = 0	#粉丝净增
		self.comment_sent = 0	#发出评论数
		self.date = datetime.now()		#日期
		self.time = time.time()	#时间
		self.other_account = {}	#用于存储他人信息

	def get_target(self):
		#Hardcoded
		self.target['壹心理		'] = 1006061894475142
		self.target['简单心理	'] = 1006065365696604
		self.target['青杏酱		'] = 1006063899965802
		self.target['迟毓凯		'] = 1005051657642437
		self.target['李松蔚PKU	'] = 1005051680738027
		
		self.target['推理心理学	'] = 1006062481337691
		self.target['博物杂志	'] = 1002061195054531
		self.target['荒野气象台	'] = 1005055856594348
		self.target['混乱博物馆	'] = 1005056174606644
		self.target['阿尔法小队教课组'] = 1005052245349133


	def get_target_info(self):
		for i in self.target:
			try:
				url = 'https://www.weibo.com/p/'+str(self.target[i])+'/' #获取地址
				html_file = requests.get(url, cookies=self.cookies).content 	#获取内容
				pattern = re.compile(r'<strong class=\\\"W_f[0-9]*\\\">([0-9]*)<\\/strong>')#解析
				parse_result = pattern.findall(html_file.decode('utf-8'))
				self.other_account[i] = parse_result[1]#写入内存并输出
				print(i + u'有' + parse_result[1] + u'个粉丝')
				time.sleep(1)

			except Exception as e:
				print("Error: ", e)
				traceback.print_exc()
				break

	def get_MyPost_data(self):
		try:
			url = 'https://www.weibo.com/p/'+ str(self.id) + '/manage'	#获取控制页地址
			requests.get(url, cookies=self.cookies)	#提交请求
			last_day_MyPost_url = 'https://dss.sc.weibo.com/pc/aj/chart/overview/last7DayMypost'#向不同API提出请求
			last_day_MyPost = requests.get(last_day_MyPost_url, cookies=self.cookies).content
			last_day_MyPost_raw = json.loads(last_day_MyPost.decode('UTF-8')) #倒入至json文件
			last_day_data = last_day_MyPost_raw['data']['chart']['last7DayMypost']	#解析文件
			self.tweet_num = last_day_data['weiboArr'][0]
			print('发博数：' + str(self.tweet_num))
			print('------------------------------------------------------------------------')
			self.comment_sent = last_day_data['commentArr'][0]
			print('发出评论数：' + str(self.tweet_num))
			print('------------------------------------------------------------------------')
			
		except Exception as e:
			print("Error: ", e)
			traceback.print_exc()

	def get_fans_data(self):
		try:
			fans_info_url = 'https://dss.sc.weibo.com/pc/aj/chart/overview/last7DayFans'#同上
			fans_info = requests.get(fans_info_url, cookies=self.cookies).content
			fans_info_raw = json.loads(fans_info.decode('UTF-8'))
			fans_info_data = fans_info_raw['data']['chart']['last7DayFans']
			self.fans_increase = fans_info_data['incr'][0]
			print('新增粉丝数：' + str(self.fans_increase))
			print('------------------------------------------------------------------------')
			self.fans_decrease = fans_info_data['decr'][0]
			print('减少粉丝数：' + str(self.fans_decrease))
			print('------------------------------------------------------------------------')
			self.fans_overall = fans_info_data['tincr'][0]
			print('净增粉丝数数：' + str(self.fans_overall))
			print('------------------------------------------------------------------------')
				
		except Exception as e:
			print("Error: ", e)
			traceback.print_exc()
	
	def get_inter_data(self):
		try:
			inter_info_url = 'https://dss.sc.weibo.com/pc/aj/chart/overview/last7DayInter'#同上
			inter_info = requests.get(inter_info_url, cookies=self.cookies).content
			inter_info_raw = json.loads(inter_info.decode('UTF-8'))
			inter_info_data = inter_info_raw['data']['chart']['last7DayInter']
			self.read_num = inter_info_data['readArr'][0]
			print('阅读数：' + str(self.read_num))
			print('------------------------------------------------------------------------')
			self.retweet_num = inter_info_data['interArr'][0]
			print('转发评论赞：' + str(self.retweet_num))
			print('------------------------------------------------------------------------')
		except Exception as e:
			print("Error: ", e)
			traceback.print_exc()

	def document(self):
		try:
			date_string = str(self.date)#日期
			file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
			if not os.path.isdir(file_dir):
				os.mkdir(file_dir)
			file_path = file_dir + os.sep +"今日数据"+date_string+ ".csv"
			f = open(file_path, "w")
			csv_writer = csv.writer(f,dialect='excel')
			header = [
				u'日期',
				u'每日条数',
				u'阅读数',
				u'转发数',
				u'评论数',
				u'点赞数',
				u'新增粉丝数',
				u'减少粉丝数',
				u'净增粉丝数',
				u'发出评论数'
			]
			
			csv_data = [
				date_string,
				self.tweet_num,
				self.read_num,
				self.retweet_num,
				0,
				0,
				self.fans_increase,
				self.fans_decrease,
				self.fans_overall,
				self.comment_sent
			]

			csv_writer.writerow(header)
			csv_writer.writerow(csv_data)
			csv_writer.writerow([])
			csv_writer.writerow([u'账号', u'粉丝数'])
			account_row = list()
			fan_row = list()
			for item in self.target:
				account_row.append(item)
				account_row.append('')
				fan_row.append(self.other_account[item])
				fan_row.append('')
			csv_writer.writerow(account_row)
			csv_writer.writerow(fan_row)
			f.close()
		except Exception as e:
			print("Error: ", e)
			traceback.print_exc()

def main():
	print(u'初始化…………')
	web_spider = Spider()
	print(u'获取昨日统计数据…………')
	web_spider.get_MyPost_data()
	web_spider.get_fans_data()
	web_spider.get_inter_data()
	print(u'获取同行粉丝数……')
	web_spider.get_target()
	web_spider.get_target_info()
	print(u'写入文档……')
	web_spider.document()
	print(u'完成!')
	
if __name__ == "__main__":
	main()