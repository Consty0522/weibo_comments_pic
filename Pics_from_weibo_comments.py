#!/usr/bin/env python3
#-*- coding = utf-8 -*-

'''
Modules needed:
1.selenium
2.requests

用来爬的页面是: https://weibo.com/1840483562/G48Ajgfhq?filter=hot&root_comment_id=0&type=comment
'''

__author__	=	'Consty'

targetUrl	=	"https://weibo.com/1840483562/G48Ajgfhq?filter=hot&root_comment_id=0&type=comment"
saveList	=	[]

from selenium import webdriver  
import time
import json
import os

#快速退出
def q():
	global browser
	browser.quit()
	quit()


#def login():
#	browser.get('https://weibo.com')
#	input("请在登陆完成后输入回车")
#	browser.get('https://weibo.com/1840483562/G48Ajgfhq?filter=hot&root_comment_id=0&type=comment')


#自动判断保存或读取cookies
def auto_cookies():
	if "cookies.txt" in os.listdir():
		load_cookies()
	else:
		print("未发现cookies.txt，请在登录完成之后在按回车...")
		input()
		save_cookies()

#保存cookies
def save_cookies():
	global browser
	cookies = browser.get_cookies()
	with open('cookies.txt', 'w') as f:
		json.dump(cookies,f)
	print("cookies存放完成")

#读取cookies并刷新
def load_cookies():
	global browser
	with open('cookies.txt','r') as f:
		cookies = json.load(f)
		for cookie in cookies:
			browser.add_cookie(cookie)
	#browser.refresh()
	print("cookies loaded")

#页面寻找xpath元素，默认刷新间隔为1秒
def detect_elment(xpath,refreshtime=1,maxtime=60):
	global browser
	totaltime = 0
	while 1:
		if totaltime >= maxtime:
			err = "Error: Searching time out, xpath = " + xpath
			return err
		temp = browser.find_elements_by_xpath(xpath)
		if len(temp) > 0:
			#print("'%s' found!" % xpath)
			return 1
		else:
			print("Unfound yet,%s -> %s" % (totaltime,maxtime))
			totaltime += refreshtime
			time.sleep(refreshtime)

#删除页面内多余元素
def delete_unneed_elements():
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('WB_frame_b'))		#删除右侧广告栏
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('webim_fold'))		#删除右下角聊天栏
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('W_gotop'))			#删除Top按键
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('WB_global_nav'))		#删除顶部导航栏

#删除Inner Comments
def delete_inner_comments():
	innerCommentsList = browser.find_elements_by_class_name('list_box_in')
	for i in range(len(innerCommentsList)):
		browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',innerCommentsList[i])

'''
缺少一个...跳过x个评论的函数，用来继承上次爬虫的进度
'''

#获取第一条评论的内容 --> 并在页面元素中删除当前第一条评论 --> 返回[userName,picUrl]  
def get_img():
	retList = []

	try:										#删除页面内所有小评论
		delete_inner_comments()					#
	except:										#??感觉每次都搜寻一遍小评论，是不是可以优化下??
		print("页面内已无小评论")					#

	try:
		firstComment	= browser.find_element_by_xpath('//div[@class="list_li S_line1 clearfix"]')									#获取第一个评论
		commentID		= firstComment.get_attribute('comment_id')																	#获取第一个评论的comment_id属性
		browser.find_element_by_xpath('//div[@comment_id="'+commentID+'"]//li[@class="WB_pic S_bg2 bigcursor"]').click()			#点击小缩略图，页面展示出大图
	except:
		print("获取评论[0]图片失败，即将删除该评论节点，并跳过本轮下载")
		browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',firstComment)									#删除该评论div
		return []

	print("本栏评论有图片，即将开始获取")
	#到这一步应该已经确认有照片了
	
	detect_elment('//div[@comment_id="'+commentID+'"]//div[@class="artwork_box"]//img')
	userName = browser.find_element_by_xpath('//div[@comment_id="'+commentID+'"]//div[@class="WB_text"]//a').text
	pic = browser.find_element_by_xpath('//div[@comment_id="'+commentID+'"]//div[@class="artwork_box"]//img')
	picUrl = pic.get_attribute('src')
	retList = retList + [userName,picUrl]		#这个是要返回的List,长度为2

	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',firstComment)	#删除该评论div
	
	return retList

def Main():
	global browser
	global saveList
	browser = webdriver.Firefox()								#加载浏览器
	browser.get('https://weibo.com')							#登陆weibo.com

	if detect_elment("//div[@class='input_wrap']") == 1:		#等待页面加载完成
		print("微博主页加载完成!")

	auto_cookies()												#读取cookies
	browser.get(targetUrl)										#到达目标页面

	while 1:
		if detect_elment("//div[@class='list_li_v2']") == 1:	#等待页面加载完成
			print("评论加载完成！")
			break
		else:
			print("评论加载失败，自动刷新页面")
			browser.refresh()

	delete_unneed_elements()									#删除多余页面元素

	count = 1
	while count < 50:
		tempRet = get_img()
		if len(tempRet) == 2:
			saveList.append(tempRet)
			print("目标已记录")
		tempRet = []
		count += 1



if __name__ == '__main__':							#我也不知道为什么都要加这一行判断，反正加就完事了!
	Main()

'''
微博评论先展示13条，下拉再出13条，再下拉再出13条，之后就必须要按“查看更多”了
'''