#!/usr/bin/env python
# coding:utf-8

import requests
from bs4 import BeautifulSoup
import pymysql.cursors
import time
import re
from openpyxl import Workbook
import xlwt
import mysqllib #数据库sql 模块



# 采集湖北采购中心数据库写入 excel

def main():	
	for a in range(1,4):
		print('开始第页：',a)
		link='http://www.ccgp-hubei.gov.cn/pages/html/xzbnotice'+str(a)+'.html'
		r = requests.get(link)
		# 获取列表
		#r = requests.get('http://www.ccgp-hubei.gov.cn/pages/html/xzbnotice.html')
		r.encoding='utf-8'
		soup = BeautifulSoup(r.text,'html.parser')
		lists=soup.select("#ulNo > li > a")

		#strinfo = re.compile()

		for link in lists:
			print(link.get('href'))
			getcontent(link.get('href'))
	
	
	
		#print(link.string)
	#getparam('ss')
	#wtexcel(lists)
	#getcontent('www.ccgp-hubei.gov.cn/fnoticeAction!findFNoticeInfoByGgid_n.action?queryInfo.GGID=c291Cb60aeVqJ5n3&queryInfo.isHtmlPage=htmlPage//201708//c291Cb60aeVqJ5n3.html')
	
# 保存exec
def wtexcel(lists):
	#创建workbook和sheet对象
	workbook = xlwt.Workbook() #注意Workbook的开头W要大写
	sheet1 = workbook.add_sheet('sheet1',cell_overwrite_ok=True)
	#sheet2 = workbook.add_sheet('sheet2',cell_overwrite_ok=True)
	#向sheet页中写入数据
	for i in range(len(lists)):
		#getcontent(lists[i].get('href'))
		print(i,lists[i].string)
		sheet1.write(i,0,lists[i].string)
		sheet1.write(i,1,lists[i].get('href'))

	#sheet1.write(0,0,'this should overwrite1')
	#sheet1.write(0,1,'aaaaaaaaaaaa') # 行，列
	#sheet2.write(0,0,'this should overwrite2')
	#sheet2.write(1,2,'bbbbbbbbbbbbb')
	#保存该excel文件,有同名文件时直接覆盖
	workbook.save('test2.xls')
	print('创建excel文件完成！')

# 采集内容
def getcontent(urls):
	id,htmls=getparam(urls)
	url='http://www.ccgp-hubei.gov.cn/fnoticeAction!findFNoticeInfoByGgid_n.action?queryInfo.GGID='+id+'&queryInfo.isHtmlPage='+htmls

	r = requests.get(url)
	r.encoding='utf-8'
	soup = BeautifulSoup(r.text,'html.parser')
	#lists=soup.find_all('table')

	title=soup.find_all('h1')
	content=soup.select('.notic_show_content')
	cinfo=soup.select('.notic_show_title_line1 > span')

	#print(title[0].string,':',content[0],':',cinfo[0].string,cinfo[1].string,cinfo[2].string,cinfo[3].string,cinfo[4].string)
	try:
		dictstr1={
		"title":title[0].string,
		"content":content[0],
		"dates":time.strftime('%Y-%m-%d',time.localtime(time.time())),
		'fabudate':cinfo[0].string,
		'kaibiaodate':cinfo[1].string,
		'location':cinfo[3].string,
		'fauser':cinfo[4].string
		}
	except Exception as e:
		print(e)
		dictstr1={
		"title":title[0].string,
		"content":content[0],
		"dates":time.strftime('%Y-%m-%d',time.localtime(time.time())),
		'fabudate':cinfo[0].string,
		'kaibiaodate':cinfo[1].string,
		'location':cinfo[3].string,
		'fauser':0
		}
	
	sql=mysqllib.get_i_sql('bs_data',dictstr1)
	print(sql)
	savemysql(sql)

# 分析uri 放回 两个参数 供内容采集组合
def getparam(str):
	#str='fnoticeAction!findFNoticeInfoByGgid_n.action?queryInfo.GGID=c291Cb60aeVqJ5n3&queryInfo.isHtmlPage=htmlPage//201708//c291Cb60aeVqJ5n3.html'
	id=re.findall(r"GGID=(.+?)&",str)
	html=re.findall(r"HTMLPATH=(.*)",str)
	
	#print(id[0],':',html[0])
	return id[0],html[0]
# 存数据库
# -- sql   
def savemysql(sql):
	
	try:
		#获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
		conn=pymysql.connect(host='www.1xxxx.me',user='root',passwd='xxxxx',db='fabiao',port=3306,charset='utf8')
		cur=conn.cursor()#获取一个游标
		cur.execute(sql)
		cur.close()#关闭游标
		conn.commit()
		conn.close()#释放数据库资源
		print('保存成功！')
	except  Exception :print("失败")
   
if __name__ == '__main__':
	main()
