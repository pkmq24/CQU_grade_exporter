#!/usr/bin/env python3
# coding:UTF-8
# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import json
from consts import *
from parseClassLists import *

isTesting = False
b网络找错 = False

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * #

def login():
  psw = 生成加密后密码()
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
    'User-Agent':user_agent
    }
  html = requests.get(urlHome, headers = headers)
  cookies = html.cookies
  requests.post(urlLogin, headers = headers, cookies = cookies, data = datas)
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
  html = requests.post(urlScores, headers = headers, cookies = cookies, data = datas)
  if b网络找错: print(html.text)
  return html

def 使用参数获取成绩(datas, cookies):
  headers = {
    'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.8, en-US; q=0.5, en; q=0.3',
    'Connection':'Keep-Alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14392'
    }
  html = requests.post(urlScores, headers = headers, cookies = cookies, data = datas)
  if b网络找错: print(html.text)
  return html

def isTextScore(s):
  if s == '合格': return True
  if s == '不合格': return True
  if s == '不及格': return True
  if s == '及格': return True
  if s == '中等': return True
  if s == '良好': return True
  if s == '中': return True
  if s == '良': return True
  if s == '优秀': return True
  if s == '优': return True
  return False

def 计算绩点(b四分制, s成绩文本, b重修 = False):
  # 1. (PF)合格3.5与不合格0
  # 2. (五级)不及格0 及格1.5 中等2.5 良好3.5 优秀4/4.5
  # 2.      优 良 中 及格不及格
  # 3. (分数)分数
  # 4. 补考与重修通过：1
  
  # 先是四五分一样的
  if s成绩文本 == '合格': return 3.5
  if s成绩文本 == '不合格': return 0
  if s成绩文本 == '不及格': return 0
  if s成绩文本 == '及格': return 1.5
  if s成绩文本 == '中等': return 2.5
  if s成绩文本 == '良好': return 3.5
  if s成绩文本 == '中': return 2.5
  if s成绩文本 == '良': return 3.5
  if b重修 and float(s成绩文本)>=60: return 1
  if b四分制:
    # 四分制！
    if s成绩文本 == '优秀': return 4
    if s成绩文本 == '优': return 4
    # print(s)
    s成绩文本 = float(s成绩文本)
    if s成绩文本 < 60: return 0
    if s成绩文本 >= 90: return 4
    return (s成绩文本-50)*0.1
  else:
    # 五分制！
    if s成绩文本 == '优秀': return 4.5
    if s成绩文本 == '优': return 4.5
    s成绩文本 = float(s成绩文本)
    if s成绩文本 <= 50: return 0
    return (s成绩文本-50)*0.1

class class成绩信息表:
  def __init__(self, a原生td):
    super().__init__()
    
    self.s原生课程名称 = a原生td[0].get_text()
    self.f学分      = float(a原生td[1].get_text())
    self.s课程类型   = a原生td[2 ].get_text()
    self.b重修标记   = a原生td[3 ].get_text() == '重修'
    self.s原生成绩   = a原生td[9 ].get_text()
    self.b辅修标记   = a原生td[10].get_text() == '辅修'
    self.b缓考标记   = a原生td[11].get_text() == '缓考'
    
    self.a原生td   = a原生td
    self.b选修课标记 = self.s课程类型 == '选修课'
    self.s原生课程名称 = '%s|%.2f'%(self.s原生课程名称,self.f学分)
    self.s课程代号 = self.s原生课程名称.split(']')[0].split('[')[1]
    # print(self.s原生课程名称, a原生td[2 ].get_text(), self.b选修课标记)
    
    
    
    
  
  def __getitem__(self, idx):
    return self.a原生td[idx].get_text()
  

def work(result, grade_arr):
  # 思路是
  soup = BeautifulSoup(result, 'html.parser')
  s =        soup.findAll('table',attrs={'id':'ID_Table', 'border': 0})
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
    上一行的课程名称 = ""
    lastScore = 0
    上一行是辅修 = False
    xuanxiuCnt = 0
    for i in range(len(scoresTable)):
      a原生td = scoresTable[i].findAll('td')
      cobj = class成绩信息表(a原生td)
      s不经处理的课程名称 = a原生td[0].get_text()
      # 处理刷分
      """
        逻辑：
        1. 不在a刷分课程名单里
        2. 没有标记重修（标记重修要另外处理）
      """
      b在刷分名单 = sum([x in cobj.s原生课程名称 for x in a刷分课程名单]) > 0
      if b在刷分名单 and\
        not cobj.b重修标记: continue
      
      # 处理合并成绩
      # 体育课程合并
      if 前缀属于数组(cobj.s课程代号, a体育课程代码前缀): 
        cobj.s原生课程名称 = '[]体育|1.00'
      # 英语课程合并
      elif 前缀属于数组(cobj.s课程代号, a英语课程代码前缀):
        cobj.s原生课程名称 = '[]英语|2.00'
      # 选修课程合并
      elif b合并选修\
         and cobj.b选修课标记\
         and not 前缀属于数组(cobj.s课程代号, a专业课程代码前缀):
        cobj.s原生课程名称 = f'[]选修课{xuanxiuCnt}|'
        xuanxiuCnt += 1

      # 处理形势与政策学分
      if cobj.f学分 == 0.0:
        cobj.f学分 = 0.01
      
      # 处理辅修
      # 两行一样的名字 且上一行不是辅修 并且这行是辅修
      # 那本行是辅修的补考，并删除前一个成绩
      if 上一行的课程名称 == s不经处理的课程名称\
        and not 上一行是辅修\
        and cobj.b辅修标记:
        last1 = scoresObj.pop(-1)
        jidian4 = last1['jidian4']
        jidian5 = last1['jidian5']
        continue
      if 上一行的课程名称 == s不经处理的课程名称 and 上一行是辅修:
        continue
      if cobj.b辅修标记:
        上一行的课程名称 = s不经处理的课程名称
        上一行是辅修 = True
        continue
      
      # 处理缓考
      if cobj.b缓考标记\
         or cobj.s原生成绩 == '':
        scoresObj.append({'课程名称': cobj.s原生课程名称, '缓考标记':True, '单科学分': cobj.f学分, 'score': 0,  'jidian4':0, 'jidian5': 0})
        grades['fail'] = True
        huankaoList[cobj.s原生课程名称] = huankaoList.get(cobj.s原生课程名称,True)
        continue
      if huankaoList.get(cobj.s原生课程名称) == True:
        scoresObj.pop(-1)
        # 两行相邻，前一行是缓考时，此行为缓考后成绩
        # 所以删除前面的0分，减去学分

      # 正常计算
      jidian4 = 计算绩点(True, cobj.s原生成绩)
      jidian5 = 计算绩点(False, cobj.s原生成绩)

      # 处理重修
      if a原生td[3].get_text() == '重修':
        if jidian4>=1: jidian4 = 1
        if jidian5>=1: jidian5 = 1

      # 处理补考
      if 上一行的课程名称 == s不经处理的课程名称:
        # 这里是补考
        if isTextScore(cobj.s原生成绩):
          jidian5 = 计算绩点(False, cobj.s原生成绩)
          cobj.s原生成绩 = jidian5 * 10 + 50
        if isTextScore(lastScore):
          lastScore = 计算绩点(False, lastScore) * 10 + 50
        # print([lastScore, cobj.s原生成绩])
        两次中更高的成绩 = max([float(lastScore), float(cobj.s原生成绩)])
        jidian4 = 计算绩点(True, 两次中更高的成绩)
        jidian5 = 计算绩点(False, 两次中更高的成绩)
        last1 = scoresObj.pop(-1)
        # 看到这里！TODO:
        if is_number(两次中更高的成绩) and float(两次中更高的成绩) > 60.0:
          jidian4 = 1
          jidian5 = 1
        scoresObj.append({'课程名称': cobj.s原生课程名称, '缓考标记':False, '单科学分': cobj.f学分, 'score': f"{两次中更高的成绩}",  'jidian4':jidian4, 'jidian5': jidian5})
      else:
        if b转换文本成绩 and isTextScore(cobj.s原生成绩):
          cobj.s原生成绩 = jidian5 * 10 + 50
        scoresObj.append({'课程名称': cobj.s原生课程名称, '缓考标记':False, '单科学分': cobj.f学分, 'score': cobj.s原生成绩,  'jidian4':jidian4, 'jidian5': jidian5})
      
      if is_number(cobj.s原生成绩) and float(cobj.s原生成绩) < 60.0:
        grades['fail'] = True
      上一行的课程名称 = s不经处理的课程名称
      上一行是辅修 = False
      lastScore = cobj.s原生成绩
    
    
    
    
    
    
    
    # if grades['sumXuefen'] == 0:
    #   print({
    #   'stuId':stuId,
    #   'stuName':stuName})
    #   print(grades)
    #   continue
    
    gpa4 = sum([x['jidian4'] * x['单科学分'] for x in scoresObj]) / sum([x['单科学分'] for x in scoresObj])
    gpa5 = sum([x['jidian5'] * x['单科学分'] for x in scoresObj]) / sum([x['单科学分'] for x in scoresObj])
    
    stuObj = {
      'stuId':stuId,
      'stuName':stuName,
      'stuGen':stuGen, 
      'stuClass':stuCla, 
      'scores': scoresObj, 
      'gpa4': gpa4, 
      'gpa5': gpa5,
      'info': [sum([x['jidian4'] * x['单科学分'] for x in scoresObj]),sum([x['jidian4'] * x['单科学分'] for x in scoresObj]), sum([x['单科学分'] for x in scoresObj])],
      'hasFail': grades['fail']}
    grade_arr.append(stuObj)


def monitor():
  grade_arr    = []
  if isTesting == True:
    with open('offlineRes.html', 'r', encoding='utf-8') as f:
      result   = f.read()
      work(result,grade_arr)
      print(f'已爬取{len(grade_arr)}名学生成绩')
    with open('data.json', 'w',encoding='utf-8') as f1:
      f1.write(json.dumps(grade_arr, ensure_ascii=False))
    return False
  
  cookies = login()
  
  a班级参数列表 = 获取专业班级列表(nj, cookies)
  for i in a班级参数列表:
    result = 使用参数获取成绩(i, cookies)
    res = get(result)
    soup = BeautifulSoup(res, 'html.parser')
    if len(soup.findAll('table')) == 0:
      continue
    work(res,grade_arr)
    print(f'完成爬取{i["sel_bj"]},已爬取{len(grade_arr)}名学生成绩')

  
  with open('data.json', 'w',encoding='utf-8') as f:
    f.write(json.dumps(grade_arr, ensure_ascii=False))

  只记录必修课 = False
  必修课人数阈值 = 100
  mergeSports = True  #PESS
  mergeEnglish = True #EUS

  with open('data.json','r',encoding='utf-8') as f:
    content = f.read()

  content = json.loads(content,encoding='utf-8')
  # 生成一份课程列表，自动归并英语和体育，然后每个学生都在对应课程的dict里加入自己的成绩

  

  classList = {}
  classXuefenList = {}
  # {key:name,value:cnt}
  for x in content:
    for item in x['scores']:
      s该条课程名称 = item['课程名称']
      f该条课程学分 = item['单科学分']
      classXuefenList[s该条课程名称] = classXuefenList.get(s该条课程名称, f该条课程学分)
      s该条课程名称=dealName(s该条课程名称)
      classList[s该条课程名称] = classList.get(s该条课程名称,0)+1

  classArr = [[x[0],x[1]] for x in classList.items()]
  classArr = sorted(classArr,key=lambda x:x[1],reverse=True)
  classNameList = [x[0] for x in classArr]

  # 生成csv头
  headList = ['学号','姓名','性别','班级','gpa4','gpa5','有挂科'] #,'总学分']
  for x in classNameList:
    headList.append(x)
    if b需要学分列: headList.append('学分')
    if b需要学分列: headList.append('')

  res = [headList]
  for x in content:
    stuArr = [x['stuId'], x['stuName'], x['stuGen'], x['stuClass'], x['gpa4'], x['gpa5'], x['hasFail']]
    for j in classNameList:
      flag = False
      for p in x['scores']:
        if dealName(p['课程名称']) == j:
          stuArr.append(p['score'])
          if b需要学分列: stuArr.append(p['单科学分'])
          if b需要学分列: stuArr.append('')
          flag=True
          break
      if flag == False:
        stuArr.append('')
        if b需要学分列: stuArr.append('')
        if b需要学分列: stuArr.append('')
    res.append(stuArr)

  output = ''
  for x in res:
    output += json.dumps(x,ensure_ascii=False).replace('[','').replace(']','').replace('"','').replace(' ','')+'\n'

  with open('data.csv','w',encoding='utf-8') as f:
    f.write(output)

if __name__ == "__main__":
  monitor()

