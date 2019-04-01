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

#删除页面内多余元素，右侧广告栏，删除右下角聊天栏，删除Top按键，删除顶部导航栏
def delete_unneed_elements():
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('WB_frame_b'))
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('webim_fold'))
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('W_gotop'))
	browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',browser.find_element_by_class_name('WB_global_nav'))

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
	#删除页面内所有小评论
	#感觉每次都搜寻一遍小评论，是不是可以优化下?
	try:										
		delete_inner_comments()
	except:
		print("页面内已无小评论")

	try:
		#获取第一个评论，获取第一个评论的comment_id属性，点击小缩略图，页面展示出大图
		detect_elment('//div[@class="list_li S_line1 clearfix"]')
		firstComment	= browser.find_element_by_xpath('//div[@class="list_li S_line1 clearfix"]')
		commentID		= firstComment.get_attribute('comment_id')
		browser.find_element_by_xpath('//div[@comment_id="'+commentID+'"]//li[@class="WB_pic S_bg2 bigcursor"]').click()
		#到这一步应该已经确认有照片了
		print("本栏评论有图片，即将开始获取")
		#等待大图出现，以防止浏览器反应不过来
		detect_elment('//div[@comment_id="'+commentID+'"]//div[@class="artwork_box"]//img',0.5)
		#获取用户名userName，图片地址picUrl
		userName = browser.find_element_by_xpath('//div[@comment_id="'+commentID+'"]//div[@class="WB_text"]//a').text
		pic = browser.find_element_by_xpath('//div[@comment_id="'+commentID+'"]//div[@class="artwork_box"]//img')
		picUrl = pic.get_attribute('src')
		#这个是要返回的List,长度为2
		retList = retList + [userName,picUrl]
	except:
		print("第一个评论未包含图片，即将删除该评论节点，并跳过本轮下载")
	finally:
		#删除该评论div，并给出返回retList
		browser.execute_script('arguments[0].parentNode.removeChild(arguments[0])',firstComment)
		return retList

'''返回的retList为一个list，根据len(retList)判断是否添加到保存列表中'''

#询问是否继续，默认步长为50,设置步长为0则不再询问是否继续
def ask_for_continue(i,step=50):
	global continueFlag
	if step == 0:
		return 1
	if continueFlag == True:	#continueFlag = Ture
		return 1
	elif i%step==1 and i>step:	#continueFlag = False
		answer = input("已检索50楼，是否继续？[y/是, n/否, all/我全都要]").lower()
		if answer == 'all':
			continueFlag = True
			return 1
		if answer == 'y':
			return 1
		if answer == 'n':
			return 0

#搞快点！根据i的大小选择滑动页面获取更多或者点击更多
def GKD(i):
	global browser
	if i % 10 == 1 and i <= 30:
		comments = browser.find_elements_by_xpath('//div[@class="list_li S_line1 clearfix"]')
		browser.execute_script('arguments[0].scrollIntoView()',comments[len(comments)-1])
	elif i % 10 == 1:
		browser.find_element_by_xpath('//span[@class="more_txt"]').click()

#将saveList内的内容保存到txt中
def dump_json(i):
	if i % 100 == 1 and i > 100:
		with open("savelist.txt","a") as f:
			for i in saveList:
				json.dump(i,f)
		saveList.clear()

#主程序
def Main():
	global browser
	global saveList
	global continueFlag
	continueFlag = False
	i = 0
#========================================================================
	#加载浏览器，登陆weibo.com
	browser = webdriver.Firefox()
	browser.get('https://weibo.com')
	if detect_elment("//div[@class='input_wrap']") == 1:
		print("微博主页加载完成!")
	auto_cookies()
	browser.get(targetUrl)
	#等待页面加载完成，超时则刷新页面
	while 1:
		if detect_elment("//div[@class='list_li_v2']") == 1:	
			print("评论加载完成！")
			break
		else:
			print("评论加载失败，自动刷新页面")
			browser.refresh()
	#删除多余页面元素
	delete_unneed_elements()
#========================================================================
	while 1:
		#判断
		i += 1
		dump_json(i)
		GKD(i)
		if ask_for_continue(i) == 0:
			break
		#正式操作
		tempRet = get_img()
		if len(tempRet) == 2:
			saveList.append(tempRet)
			print("目标已记录")
		tempRet = []
	print(len(saveList))
#========================================================================
#主程序
#========================================================================
#我也不知道为什么都要加这一行判断，反正加就完事了!
if __name__ == '__main__':
	Main()

'''
微博评论先展示13条，下拉再出13条，再下拉再出13条，之后就必须要按“查看更多”了
'''
