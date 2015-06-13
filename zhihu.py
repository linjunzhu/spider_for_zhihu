# coding: utf-8

import urllib
import urllib2
import re
import pdb
import os
import ssl

# V0.1
# 抓取某个人的所有回答存入文本

class Zhihu:

    def __init__(self, url):
        self.url = url

    def get_page(self, url):
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            content = response.read()
            return content.decode('utf-8')
        except urllib2.URLError, error:
            if hasattr(error, 'reason'):
                print('Something is wrong :' + error.reason)
            elif hasattr(error, 'code'):
                print('Something is wrong : ' + error.code)
            return None

    def get_user_info(self, content):
        pattern = re.compile(r'<div class="title-section ellipsis">.*?<span class="name">(.*?)</span>.*?' +
                                r'<span class="bio.*?>(.*?)</span>.*?<span class="zm-profile-header-user-agree"' +
                                r'.*?<strong>(.*?)</strong>.*?<span class="zm-profile-header-user-thanks".*?<strong>(.*?)</strong>', re.S)
        result = re.search(pattern, content)
        return result

    def save_for_file(self, info, answers):
        file = open("%s.txt" % info.group(1), "w+")
        file.write((u"Name: %s\nBio: %s \nUser_agrees: %s\nUser_thanks: %s" % (info.group(1),info.group(2),info.group(3),info.group(4))).encode('utf-8'))
        for answer in answers:
            file.write((u"\nLink: %s \nQuestion: %s \nVotes: %s \nAnswer: %s" % (answer[0],answer[1],answer[2],answer[3])).encode('utf-8'))

    def get_answers(self, content):
        page = 1
        enable = True
        answers = []
        # 获取每一个的答案
        while enable:
            print("page:%d" % page)
            url = self.url + "/answers?page=" + str(page)
            content = self.get_page(url)
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

    def start_get_answers(self):
        content = self.get_page(self.url)
        info = self.get_user_info(content)
        answers = self.get_answers(content)
        self.save_for_file(info, answers)

url = raw_input(u'请输入要抓取的人的主页:'.encode('utf-8'))
zhihu = Zhihu(url)
zhihu.start_get_answers()