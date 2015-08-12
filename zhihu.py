# coding: utf-8

import urllib
import urllib2
import re
import pdb
import os
import cookielib
from PIL import Image
import StringIO

# V0.2
# 1、抓取某个人的所有回答存入文本
# 2、抓取某个答案下的回答点赞用户情况（四无)

class Zhihu:

    def __init__(self):
        self.cookies = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36',
            'Referer' : 'http://www.zhihu.com/',
            'Origin' : 'http://www.zhihu.com/'
        }

    def input_identity(self):
        email = raw_input(u'请输入账号:'.encode('utf-8'))
        password = raw_input(u'请输入密码:'.encode('utf-8'))
        return {'email' : email, 'password' : password }

    # 登录
    def login(self):
        url = 'http://www.zhihu.com/login/email'
        base_url = "http://www.zhihu.com/#signin"
        content = "errcode"
        status = False
        while not status:
            status = self.judge_login(content)
            if status:
                print u'登录成功'
            else:
                print u'未登录 or 登录失败'
                identity = self.input_identity()
                content = self.get_page(base_url)
                # 获取验证码以及CSRF值重新登录
                verify_code = self.get_verify_code(content)
                csrf_token = self.get_csrf_token(content)
                data = urllib.urlencode({
                    'email' : identity['email'],
                    'password' : identity['password'],
                    'rememberme' : 'y',
                    '_xsrf' : csrf_token,
                    'captcha' : verify_code
                })
                content = self.get_page(url, data)
                print content


    def get_csrf_token(self, content):
        pattern = re.compile('<meta content="(.*?)" name="csrf-token"')
        item = re.search(pattern, content)
        if item:
            csrf_token = item.group(1).strip()
        else:
            csrf_token = ""

    def judge_login(self, content):
        pattern = re.compile(r'errcode', re.S)
        item = re.search(pattern, content)
        if item:
            return False
        else:
            return True

    def get_verify_code(self, content):
        # 提取内容页的验证码图片地址
        pattern = re.compile(r'<img class="js-captcha-img".*?src="(.*?)".*? />', re.S)
        item = re.search(pattern, content)
        if item:
            content = self.get_page(item.group(1).strip(), binary = True)
            img = Image.open(StringIO.StringIO(content));
            img.show()
            code = raw_input(u'请输入验证码：'.encode('utf-8'))
            return code
        else:
            return ""

    # 获取页面
    def get_page(self, url, data="", binary=False):
        try:
            print url
            if data:
                request = urllib2.Request(url, headers = self.headers, data = data)
            else:
                request = urllib2.Request(url, headers = self.headers)
            response = self.opener.open(request)
            content = response.read()
            if binary:
                return content
            else:
                return content.decode('utf-8')

        except urllib2.URLError, error:
            if hasattr(error, 'reason'):
                print('Something is wrong :' + error.reason)
            elif hasattr(error, 'code'):
                print('Something is wrong : ' + error.code)
            exit()

    # 获取用户信息
    def get_user_info(self, content):
        pattern = re.compile(r'<div class="title-section ellipsis">.*?<span class="name">(.*?)</span>.*?' +
                                r'<span class="zm-profile-header-user-agree".*?<strong>(.*?)</strong>.*?' +
                                r'<span class="zm-profile-header-user-thanks".*?<strong>(.*?)</strong>', re.S)
        result = re.search(pattern, content)
        # pdb.set_trace()
        return result

    # 保存成文本
    def save_for_file(self, info, answers):
        file = open("%s.txt" % info.group(1), "w+")
        file.write((u"Name: %s \nUser_agrees: %s\nUser_thanks: %s\n" % (info.group(1),info.group(2),info.group(3))).encode('utf-8'))
        for answer in answers:
            file.write((u"\nLink: %s \nQuestion: %s \nVotes: %s \nAnswer: %s" % (answer[0],answer[1],answer[2],answer[3])).encode('utf-8'))

    # 获取所有答案
    def get_answers(self, content, url):
        page = 1
        enable = True
        answers = []
        # 获取每一个的答案
        while enable:
            print("page:%d" % page)
            answer_url = url + "/answers?page=" + str(page)
            content = self.get_page(answer_url)
            pattern = re.compile(r'<div class="zm-item".*?<a.*?href="(.*?)">(.*?)</a>.*?</h2>' +
                                    r'.*?<a.*?class="zm-item-vote-count.*?>(.*?)</a>.*?<div class=' +
                                    r'"zh-summary.*?>(.*?)</div>', re.S)
            items = re.findall(pattern, content)
            if len(items) > 0:
                for item in items:
                    answers.append([item[0],item[1],item[2],item[3]])
                page += 1
            else:
                enable = False

        return answers

    def start_get_answers(self, url):
        content = self.get_page(url)
        info = self.get_user_info(content)
        answers = self.get_answers(content, url)
        self.save_for_file(info, answers)


    # 分析每个答案的点赞者,返回四无用户比例
    def analyze_voters(self, answer_id, count_agree):
        voter_url = "http://www.zhihu.com/answer/%s/voters_profile" % answer_id
        # 四无用户
        count_no_identity = 0
        voters_pattern = re.compile(r'<div class=\\"zm-profile-card[^>]*>.*?<ul class=\\"status\\">.*?<li>.*?<span>(\d).*?</span>' +
                                    r'.*?<li>.*?<span>(\d).*?</span>.*?<li.*?<a[^>]*>(\d).*?</a>.*?<li.*?<a[^>]*>(\d).*?</a>', re.S)
        next_agree_pattern = re.compile(r'{"paging":.*?"next": "(.*?)"}', re.S)
        enable = True
        while enable:
            content = self.get_page(voter_url)
            items = re.findall(voters_pattern, content)
            for item in items:
                if int(item[0]) == 0 and int(item[1]) == 0 and int(item[2]) == 0 and int(item[3]) == 0:
                    count_no_identity += 1
            # 判断是否还有下一页
            items = re.search(next_agree_pattern, content)
            # 下一页点赞情况
            next_agree = items.group(1)
            if next_agree:
                voter_url = "http://www.zhihu.com" + next_agree
            else:
                enable = False
        return float(count_no_identity)/float(count_agree)


    # 分析每个答案
    def anaylyze_answers(self, content):
        # 0 为答案ID 1 为总赞数 2 为答主
        pattern = re.compile(r'<div tabindex.*?class="zm-item-answer.*?data-aid="(.*?)"[^>]*>.*?<button class="up.*?class="count">(.*?)</span>' +
                                r'.*?<h3 class="zm-item-answer-author-wrap">(?:(?:\n\n\n<a[^>]*>.*?</a>.*?<a[^>]*>(.*?)</a>(?:(?!</h3>).)*)|((?:(?!</h3>).)*))</h3>', re.S)
        items = re.findall(pattern, content)
        results = []
        # 如果是为匿名用户，则值在item[3]
        for item in items:
            print(u"开始分析 %s ..." % self.show_author(item[2], item[3]))
            ratio = 0
            if int(item[1]) > 0:
                ratio = self.analyze_voters(item[0], item[1])
            results.append([self.show_author(item[2], item[3]), item[1], "%d%%" % int(ratio * 100)])
        return results

    # 返回作者
    def show_author(self, normal, anonymity):
        value =  normal if normal else anonymity
        return value

    # 将分析的情况保存成文本
    def save_for_file_by_analyze_question(self, filename, results):
        file = open("%s.txt" % filename, "w+")
        for result in results:
            file.write((u"回答者: %s 总赞数: %s 点赞中四无用户比例: %s\n" % (result[0],result[1],result[2])).encode('utf-8'))

    def start_analyze_question(self, url, filename):
        self.login()
        content = self.get_page(url)
        results = self.anaylyze_answers(content)
        self.save_for_file_by_analyze_question(filename, results)

select = raw_input(u'请选择功能:\n1: 抓取知乎人的信息\n2: 分析某个问题\n'.encode('utf-8'))
zhihu = Zhihu()

if int(select) == 1:
    url = raw_input(u'请输入要抓取的人的主页:'.encode('utf-8'))
    zhihu.start_get_answers(url)
elif int(select) == 2:
    url = raw_input(u'请输入要抓取的问题地址:'.encode('utf-8'))
    filename = raw_input(u'请输入要保存的文本名:'.encode('utf-8'))
    zhihu.start_analyze_question(url, filename)
