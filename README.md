
#简介
用于抓取知乎信息的小玩意

#功能
1. 抓取某个人的所有回答存入文本
2. 抓取某个答案下的回答点赞用户情况（四无)

#使用
`$ xx` 代表从命令行输入`xx`

```shell
$ python zhihu.py

===>

请选择功能:
1: 抓取知乎人的信息
2: 分析某个问题
```

###功能一：
```shell
$ 1
# 输入某个知友的主页地址
$ http://www.zhihu.com/people/lin-jun-zhu
```

此时便会在当前目录生成一个`知友名字.txt`的文本。

###功能二：
```shell
$ 2
# 输入要分析的问题地址
$ http://www.zhihu.com/question/26951402
# 输入要保存的文本名
$ answers
# 输入用户名和密码
......
```

(由于知乎更改了界面，功能二暂时失效，有空再更新)