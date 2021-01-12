#!/usr/bin/env python3
# coding:UTF-8
# -*- coding: utf-8 -*-
import re
import requests
import hashlib, time
from time import strftime, localtime
from bs4 import BeautifulSoup
import json
import sys
import hashlib
from time import strftime, localtime
import configparser
 
import configparser
import os
curpath = os.path.dirname(os.path.realpath(__file__))
cfgpath = os.path.join(curpath, "config.ini")
conf = configparser.ConfigParser()
conf.read(cfgpath, encoding="utf-8")
sections = conf.sections()
acco = conf.items('account')
username  = conf.get('account','username')
password  = conf.get('account','password')

xn         = conf.get('target','xuenian')        # 学年
xq         = conf.get('target','xueqi')          # 0 上学期 1 下学期
nj         = conf.get('target','nianji')         # 年级
yx         = 1                                   # 默认为1
zy         = int(conf.get('target','zhuanyecode'))    # 专业起始代码
threshhold = int(conf.get('target','threshhold') )    # 年级大概人数

isTesting = False



alternative_url_202 = 'http://202.202.1.41/'
alternative_url_jxgl = 'http://jxgl.cqu.edu.cn/'

url = alternative_url_202
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * #

#* 模拟登录
homeUrl = url+"home.aspx"
loginUrl = url+"_data/index_login.aspx"
scoreUrl = url+"/XSCJ/f_xscjtzd_rpt.aspx"
schoolcode = "10611"
url_google = 'http://translate.google.cn'
reg_text = re.compile(r'(?<=TRANSLATED_TEXT=).*?;')
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
         r'Chrome/44.0.2403.157 Safari/537.36'
last_file = ""

def checkPwd():
  p = hashlib.md5(password.encode()).hexdigest()
  p = hashlib.md5(( username + p[0:30].upper() + schoolcode).encode()).hexdigest()
  return p[0:30].upper()

def login():
  psw = checkPwd()
  datas = {
    'Sel_Type': 'SYS',
    'txt_dsdsdsdjkjkjc': username,
    'txt_dsdfdfgfouyy': password,
    'txt_ysdsdsdskgf': '',
    'pcInfo': '',
    'typeName': '',
    'aerererdsdxcxdfgfg': '',
    'efdfdfuuyyuuckjg': psw
    }
  headers = {
    'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.8, en-US; q=0.5, en; q=0.3',
    'Connection':'Keep-Alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14392'
    }
  html = requests.get(homeUrl, headers = headers)
  cookies = html.cookies
  requests.post(loginUrl, headers = headers, cookies = cookies, data = datas)
  return cookies

def getDirectScore(zy_del, class_, cookies):
  ZY = zy + zy_del
  cla = "{:0>2d}".format(class_)
  headers = {
    'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.8, en-US; q=0.5, en; q=0.3',
    'Connection':'Keep-Alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14392'
    }
  datas = {
    'sel_xnxq': f"{xn}{xq}",
    'sel_nj': nj,
    'sel_yx': yx,
    'sel_zy': ZY,
    'sel_bj': f"{nj}{ZY}{cla}"
  }
  html = requests.post(scoreUrl, headers = headers, cookies = cookies, data = datas)
  return html

def get(html):
  html.text.encode('utf-8')
  return html.text
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
def getJidian(is4, s, isReStudy = False):
  # 1. (PF)合格3.5与不合格0
  # 2. (五级)不及格0 及格1.5 中等2.5 良好3.5 优秀4/4.5
  # 2.      优 良 中 及格不及格
  # 3. (分数)分数
  # 4. 补考与重修通过：1
  
  # 先是四五分一样的
  if s == '合格': return 3.5
  if s == '不合格': return 0
  if s == '不及格': return 0
  if s == '及格': return 1.5
  if s == '中等': return 2.5
  if s == '良好': return 3.5
  if s == '中': return 2.5
  if s == '良': return 3.5
  if isReStudy and float(s)>=60: return 1
  if is4:
    # 四分制！
    if s == '优秀': return 4
    if s == '优': return 4
    # print(s)
    s = float(s)
    if s <= 60: return 0
    if s >= 90: return 4
    return (s-50)*0.1
  else:
    # 五分制！
    if s == '优秀': return 4.5
    if s == '优': return 4.5
    s = float(s)
    if s <= 50: return 0
    return (s-50)*0.1

def work(result,grade_arr):
  soup = BeautifulSoup(result, 'html.parser')
  s = soup.findAll('table',attrs={'id':'ID_Table', 'border': 0})
  s_score =  soup.findAll('table',attrs={'id':'ID_Table', 'border': 1})
  for k in range(len(s)):
    stuEach = s[k]
    gradeEach = s_score[k]
    scoresTable = gradeEach.findAll('tr')
    infoTable = stuEach.findAll('td')
    stuId = infoTable[0].get_text().split('：')[1]
    stuName = infoTable[1].get_text().split('：')[1]
    stuGen = infoTable[2].get_text().split('：')[1]
    stuCla = infoTable[3].get_text().split('：')[1]
    scoresObj = []
    grades = {
      'sum4': 0,
      'sum5': 0,
      'sumXuefen': 0,
      'fail': False
    }
    huankaoList = {}
    for i in range(len(scoresTable)):
      score_tds = scoresTable[i].findAll('td')
      claName = score_tds[0].get_text()
      claXuefen = float(score_tds[1].get_text())
      claName = '%s|%.2f'%(claName,claXuefen)
      if claXuefen == 0.0:
        claXuefen = 0.01
      isPushedBack = score_tds[11].get_text()
      score = score_tds[9].get_text()
      if isPushedBack == '缓考':
        scoresObj.append({'name': claName, 'isHuan':True, 'xuefen': claXuefen, 'score': 0,  'jidian4':0, 'jidian5': 0})
        grades['fail'] = True
        huankaoList[claName] = huankaoList.get(claName,True)
        continue
      if score == '':
        scoresObj.append({'name': claName, 'isHuan':True, 'xuefen': claXuefen, 'score': '异常空',  'jidian4':0, 'jidian5': 0})
        grades['fail'] = True
        huankaoList[claName] = huankaoList.get(claName,True)
        continue
      if huankaoList.get(claName) == True:
        scoresObj.pop(-1)
      # print(stuName)
      jidian4 = getJidian(True, score)
      jidian5 = getJidian(False, score)
      scoresObj.append({'name': claName, 'isHuan':False, 'xuefen': claXuefen, 'score': score,  'jidian4':jidian4, 'jidian5': jidian5})
      grades['sum4'] += jidian4*claXuefen
      grades['sum5'] += jidian5*claXuefen
      grades['sumXuefen'] += claXuefen
      if is_number(score) and float(score) < 60.0:
        grades['fail'] = True

    stuObj = {
      'stuId':stuId,
      'stuName':stuName,
      'stuGen':stuGen, 
      'stuClass':stuCla, 
      'scores': scoresObj, 
      'gpa4': grades['sum4']/grades['sumXuefen'], 
      'gpa5': grades['sum5']/grades['sumXuefen'],
      'hasFail': grades['fail']}
    grade_arr.append(stuObj)

def monitor():
  global isTesting
  grade_arr    = []
  if isTesting == True:
    with open('offlineRes.html', 'r', encoding='utf-8') as f:
      result   = f.read()
      work(result,grade_arr)
      print(f'已爬取{len(grade_arr)}名学生成绩')
    with open('data.json', 'w',encoding='utf-8') as f1:
      f1.write(json.dumps(grade_arr, ensure_ascii=False))
    return False
  
  cookies   = login()
  zy_delta = -1
  cl_no = 0
  while(1):
    zy_delta += 1
    cl_no = 0
    flag = False
    print(0,cl_no, zy_delta)
    while(1):
      cl_no += 1
      result = getDirectScore(zy_delta, cl_no, cookies)
      res = get(result)
      soup = BeautifulSoup(res, 'html.parser')
      if len(soup.findAll('table')) == 0:
        break
      work(res,grade_arr)
      print(f'完成爬取{zy_delta}:{cl_no},已爬取{len(grade_arr)}名学生成绩')
    print(1,cl_no, zy_delta)
    if len(grade_arr) >= threshhold:
      print(cl_no, zy_delta)
      break
  
  with open('data.json', 'w',encoding='utf-8') as f:
    f.write(json.dumps(grade_arr, ensure_ascii=False))

  只记录必修课 = False
  必修课人数阈值 = 100
  mergeSports = True  #PESS
  mergeEnglish = True #EUS

  with open('data.json','r') as f:
    content = f.read()

  content = json.loads(content,encoding='utf-8')
  # 生成一份课程列表，自动归并英语和体育，然后每个学生都在对应课程的dict里加入自己的成绩

  def dealName(name):
    if name.startswith('[PESS'): name = '[]体育|1.00'
    if name.startswith('[EUS'): name = '[]英语|2.00'
    name=name.split(']')[1]
    return name

  classList = {}
  # {key:name,value:cnt}
  for x in content:
    for item in x['scores']:
      claName = item['name']
      claName=dealName(claName)
      classList[claName] = classList.get(claName,0)+1

  classArr = [[x[0],x[1]] for x in classList.items()]
  classArr = sorted(classArr,key=lambda x:x[1],reverse=True)
  classNameList = [x[0] for x in classArr]

  # 生成csv头
  headList = ['学号','姓名','性别','班级','gpa4','gpa5','有挂科'] #,'总学分']
  for x in classNameList:
    headList.append(x)

  res = [headList]
  for x in content:
    stuArr = [x['stuId'], x['stuName'], x['stuGen'], x['stuClass'], x['gpa4'], x['gpa5'], x['hasFail']]
    for j in classNameList:
      flag = False
      for p in x['scores']:
        if dealName(p['name']) == j:
          stuArr.append(p['score'])
          flag=True
          break
      if flag == False:
        stuArr.append('')
    res.append(stuArr)

  output = ''
  for x in res:
    output += json.dumps(x,ensure_ascii=False).replace('[','').replace(']','').replace('"','').replace(' ','')+'\n'

  with open('data.csv','w') as f:
    f.write(output)

if __name__ == "__main__":
  monitor()

