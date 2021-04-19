import re
import requests
from bs4 import BeautifulSoup
import json
from consts import *

def 获取专业班级列表(年级, cookies):
  headers = {
    'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.8, en-US; q=0.5, en; q=0.3',
    'Connection':'Keep-Alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14392'
    }
  html = requests.get(urlSelectPage, headers = headers, cookies = cookies)
  res = get(html)
  soup = BeautifulSoup(res, 'html.parser')
  script_list = soup.findAll('script')

  s专业列表 = ''
  s班级列表 = ''

  for i in script_list:
    if i.string == None: continue
    if i.string.startswith('function LetInner'):
      if s专业列表 == '': s专业列表 = i.string
      else: s班级列表 = i.string
      
  a专业列表 = []
  pattern = re.compile(r"]='(.*?)';", re.MULTILINE | re.DOTALL)
  for i in re.finditer(pattern,s专业列表):
    value = i.group().split('\'')[1]
    a专业列表.append(value)

  a班级列表 = []
  pattern = re.compile(r"]='(.*?)';", re.MULTILINE | re.DOTALL)
  for i in re.finditer(pattern,s班级列表):
    value = i.group().split('\'')[1]
    a班级列表.append(value)
    
  # 年级与班级列表去匹配，其实专业列表都不需要了。。
  a返回值 = []
  
  for k in range(int(len(a班级列表)/4)):
    if a班级列表[k*4+3] == 年级:
      a返回值.append({
        'sel_xnxq': f"{xn}{xq}",
        'sel_nj': 年级,
        'sel_yx': a班级列表[k*4][0:2],
        'sel_zy': a班级列表[k*4],
        'sel_bj': a班级列表[k*4+1],
        'chkrad': 1,
        'btn_search': '%BC%EC%CB%F7'
      })
      
  return a返回值
  