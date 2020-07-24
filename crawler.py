from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import requests
import json
import regex as re


class Crawler:
    def __init__(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }

        # url = "https://www.sciencedirect.com/journal/water-research/vol/180/suppl/C"
        self.url = url
        self.html = requests.get(self.url, headers=self.headers)

        self.soup = BeautifulSoup(self.html.content, features='lxml')

        self.title = self.soup.find_all('span', {'class': 'js-article-title'})
        self.name = self.soup.find_all('div', {'class': 'text-s u-clr-grey8 js-article__item__authors'})
        self.link = self.soup.find_all('a', {'class': 'anchor article-content-title u-margin-xs-top u-margin-s-bottom'},
                             href=True)
        self.i = 0
        self.count = 0

        # 提取网页中存储各paper附属信息的内容并用正则化提取所需片段，主要提取authors这个字典
        self.otherinfo = self.soup.find_all(type="application/json")
        self.auth = self.soup.find_all('auth')
        self.soup2 = self.otherinfo[0]
        self.soup2_str = self.soup2.contents[0].replace('\\', '')
        self.soup2_str = self.soup2_str[1:-1]

        # results = 正则化得到一个list，各元素对应每篇文章的信息
        self.regex0 = '\"totalResults\":\d+'
        self.regex1 = '\"title\".*?\"authors\"\:\[\{.*?\}\]'
        self.regex2 = '\"authors\"\:\[\{.*\}'
        self.number = re.findall(self.regex0, self.soup2_str)
        self.number = int(re.findall('\d+', self.number[0])[0])
        self.results = re.findall(self.regex1, self.soup2_str)

    def author_info(self, result):
        authors = {'一作': [], '通讯': [], '其他': []}
        while True:
            test = re.findall(self.regex1, result[2:])
            if not test:
                break
            else:
                result = test[0]
        # print(result)
        auths = re.findall(self.regex2, result)
        auths_str = auths[0][11:]
        refs = re.findall('\{.*?\}', auths_str)

        # 提取每个作者的信息dict并print
        for i in range(len(refs)):
            refs[i] = json.loads(refs[i])  # 使refs[i]从str->dict
            name = refs[i]['givenName'] + ' ' + refs[i]['surname']

            if 'cor1' in refs[i]['refs'] or 'cor2' in refs[i]['refs']:
                authors['通讯'].append(name)

            if refs[i]['id'] == 'auth-0':
                authors['一作'].append(name)

            authors['其他'].append(name)

        for auth in authors['其他']:
            if auth in authors['一作'] or auth in authors['通讯']:
                authors['其他'].remove(auth)

        return authors

    def get_results(self):
        res = {'标题': [], '中文标题': [], '作者': [], '链接': []}
        for title, link in zip(self.title, self.link):
            res['标题'].append(title.get_text())
            url = 'http://fanyi.youdao.com/translate?smartresult=' \
                       'dict&smartresult=rule&sessionFrom=https://www.baidu.com/link'

            data = {'from': 'AUTO', 'to': 'AUTO', 'smartresult': 'dict', 'client': 'fanyideskweb',
                    'salt': '1500092479607',
                    'sign': 'c98235a85b213d482b8e65f6b1065e26', 'doctype': 'json', 'version': '2.1',
                    'keyfrom': 'fanyi.web',
                    'action': 'FY_BY_CL1CKBUTTON', 'typoResult': 'true', 'i': title.get_text()}

            data = urllib.parse.urlencode(data).encode('utf-8')
            response = urllib.request.urlopen(url, data)
            html = response.read().decode('utf-8')
            ta = json.loads(html)

            res['中文标题'].append(ta['translateResult'][0][0]['tgt'])

            if title.get_text() == 'Editorial Board':
                res['作者'].append('None')
                self.count += 1
            elif title.get_text() == 'Publisher\'s Note':  # 不是note
                res['作者'].append('None')
                self.count += 1
            else:
                # print('作者：', name[i-count].get_text())
                res['作者'].append(self.author_info(self.results[self.i - self.count]))

            res['链接'].append('https://www.sciencedirect.com{}'.format(link['href']))

            self.i += 1

        return res


crawler = Crawler("https://www.sciencedirect.com/journal/water-research/vol/180/suppl/C")
crawler.get_results()
