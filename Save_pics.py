#!/usr/bin/env python3
#-*- coding = utf-8 -*-

'''
download pictures from savelist.txt
'''

import requests , os , json

startLine = int(input("请输入开始下载的行数:"))
print('默认保存路径为e:\\wb_download')

#focusList = [userName,picUrl]
def read_text():
	global startLine
	i = 1
	if "savelist.txt" not in os.listdir():
		print("未找到savelist.txt文件，请确认savelist.txt在根目录中")
		return "error: file(savelist.txt) not found"
	else:
		with open("savelist.txt","r") as f:
			while i < startLine:
				f.readline()
				i += 1
			while 1:
				rl = f.readline()
				if rl == "":
					return "done"
				else:
					focusList = json.loads(rl.replace("\n",""))
					#返回值[userName,picUrl,i]
					yield focusList + [i]
					i += 1
	pass		

def jgtfp(picUrl):
	pic = None
	try:
		pic = requests.get(picUrl).content
	except:
		jgtfp(picUrl)
	return pic
	pass

def request_and_save(userName,picUrl,address="e:\\wb_download"):
	if os.path.exists("e:\\wb_download") == False:
		os.mkdir(address)
	#组装文件名
	fName = userName + picUrl[(-picUrl[::-1].find(".") - 1):]
	abAdd = address + "\\" + fName
	if os.path.exists(abAdd) == False:
		#获得图片
		pic = jgtfp(picUrl)
		with open(abAdd,"wb") as f:
			f.write(pic)
		return "OK"
	else:
		return "existed"

def Main():
	gen = read_text()
	while 1:
		getList = next(gen)
		if getList == "done":
			print("所有数据下载完成！")
		else:
			ret = request_and_save(getList[0],getList[1])
			if ret == "OK":
				print("第 %s 行数据下载完成" % getList[2])
			elif ret == "existed":
				print("第 %s 行数据已存在" % getList[2])
	pass

Main()
