import os
import configparser
import hashlib

alternative_url_202 = 'http://202.202.1.41/'
alternative_url_jxgl = 'http://jxgl.cqu.edu.cn/'
url = alternative_url_202

urlHome = url+"home.aspx"
urlLogin = url+"_data/index_login.aspx"
urlScores = url+"/XSCJ/f_xscjtzd_rpt.aspx"
urlSelectPage = url + "/XSCJ/f_xscjtzd.aspx"
schoolcode = "10611"
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
    r'Chrome/44.0.2403.157 Safari/537.36'


curpath = os.path.dirname(os.path.realpath(__file__))
cfgpath = os.path.join(curpath, "config.ini")
conf = configparser.ConfigParser()
conf.read(cfgpath, encoding="utf-8")


sections = conf.sections()
acco = conf.items('account')
username = conf.get('account', 'username')
password = conf.get('account', 'password')

xn = conf.get('target', 'xuenian')        # 学年
xq = conf.get('target', 'xueqi')          # 0 上学期 1 下学期
nj = conf.get('target', 'nianji')         # 年级
yx = 1                                   # 默认为1
zy = int(conf.get('target', 'zhuanyecode'))    # 专业起始代码
threshhold = int(conf.get('target', 'threshhold'))    # 年级大概人数

b需要学分列 = int(conf.get('config', '需要学分列'))  # 是否需要学分
b转换文本成绩 = conf.get('config', '需要将文字成绩转化为分数') == '1'  # 文字成绩→数字成绩
a刷分课程名单 = conf.get('list', '刷分课程列表').split('|')  # 手动加入重修课程名
b合并选修 = conf.get('config', '需要合并选修课') == '1'  # 合并选修


a专业课程代码前缀 = conf.get('list', '专业课程代码前缀列表').split('|')
a体育课程代码前缀 = conf.get('others', '体育课程代码前缀列表').split('|')
a英语课程代码前缀 = conf.get('others', '英语课程代码前缀列表').split('|')


def 生成加密后密码():
  p = hashlib.md5(password.encode()).hexdigest()
  p = hashlib.md5((username + p[0:30].upper() +
                   schoolcode).encode()).hexdigest()
  return p[0:30].upper()


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



def 前缀属于数组(detectStr, detectArr):
  #   print(detectStr, detectArr)
  if detectArr[-1] == '':
    detectArr = detectArr[:-1]
#   print([detectStr.startswith(x) for x in detectArr])
  return sum([detectStr.startswith(x) for x in detectArr]) > 0

def dealName(name):
  if 前缀属于数组(name, a体育课程代码前缀):
    name = '体育|1.00'
  # 英语课程合并
  elif 前缀属于数组(name, a英语课程代码前缀):
    name = '英语|2.00'
  else: name = name.split(']')[1]
  return name
