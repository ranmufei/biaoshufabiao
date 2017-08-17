#!/usr/bin/env python
# coding:utf-8

import requests
from bs4 import BeautifulSoup
import pymysql.cursors
import time
import re
from openpyxl import Workbook
import xlwt
import hashlib
import mysqllib #数据库sql 模块
import time, os, sched 



# 采集湖北采购中心数据库写入 excel

def main():
		list=('http://www.ccgp-hubei.gov.cn/pages/html/szbnotice.html','http://www.ccgp-hubei.gov.cn/pages/html/xzbnotice.html')
		
		
		'''
		for ls in range(len(list)):
			print(ls,list[ls])
			
		'''
		#return
		#for a in range(1,4):
		for a in range(len(list)):
			print('开始第页：',a)
			link=list[a]   #'http://www.ccgp-hubei.gov.cn/pages/html/szbnotice'+str(a)+'.html' 
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
	hash1=hashlib.md5()
	hash1.update(url.encode('utf-8'))
	hash_num=hash1.hexdigest()
	
	#print(hash_num)
	#return 0
	if isInto(hash_num) > 0 :
		print('已经采集过过了')
		return 
		
	try:
		r = requests.get(url,timeout=6)
		r.encoding='utf-8'
		soup = BeautifulSoup(r.text,'html.parser')
	except requests.RequestException as e:
		print(e)
		return
	
	#lists=soup.find_all('table')

	title=soup.find_all('h1')
	content=soup.select('.notic_show_content')
	cinfo=soup.select('.notic_show_title_line1 > span')

	#print(title[0].string,':',content[0],':',cinfo[0].string,cinfo[1].string,cinfo[2].string,cinfo[3].string,cinfo[4].string)
	try:
		dictstr1={
		"hash":hash_num,
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
		"hash":hash_num,
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
	
# 检查url hash是否存在
# 返回 int
def isInto(hashstr):
	sql='SELECT id,hash,title FROM bs_data WHERE hash = "'+str(hashstr)+'"'
	
	try:
		#获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
		conn=pymysql.connect(host='www.17ni.me',user='root',passwd='^%cqsyy@#1xyd2xsyc6z',db='fabiao',port=3306,charset='utf8')
		cur=conn.cursor()#获取一个游标
		cur.execute(sql)
		ret = cur.fetchall()
		cur.close()#关闭游标
		conn.commit()
		conn.close()#释放数据库资源
		#print(len(ret))
		return len(ret)
	except  Exception as err:print(err)
		
	
	
	
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
		conn=pymysql.connect(host='www.17ni.me',user='root',passwd='^%cqsyy@#1xyd2xsyc6z',db='fabiao',port=3306,charset='utf8')
		cur=conn.cursor()#获取一个游标
		cur.execute(sql)
		cur.close()#关闭游标
		conn.commit()
		conn.close()#释放数据库资源
		print('保存成功！')
	except  Exception :print("失败")

# 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数 
# 第二个参数以某种人为的方式衡量时间 
schedule = sched.scheduler(time.time, time.sleep)     
def perform_command(cmd, inc): 
    # 安排inc秒后再次运行自己，即周期运行 
    schedule.enter(inc, 0, perform_command, (cmd, inc)) 
    #os.system(cmd) 
    print('定时任务开始')
    main()
        
def timming_exe(cmd, inc = 60): 
    print('周期任务开始准备~~~~%s秒后开始执行'%(inc))
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动 
    schedule.enter(inc, 0, perform_command, (cmd, inc)) 
    # 持续运行，直到计划时间队列变成空为止 
    schedule.run() 
   
if __name__ == '__main__':
	#main()
	timming_exe("echo %time%", 7200)
