from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import requests
import json
import regex as re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}

url = "https://www.sciencedirect.com/journal/water-research/vol/180/suppl/C"

html = requests.get(url, headers=headers)

soup = BeautifulSoup(html.content, features='lxml')

title = soup.find_all('span', {'class': 'js-article-title'})
name = soup.find_all('div', {'class': 'text-s u-clr-grey8 js-article__item__authors'})
link = soup.find_all('a', {'class': 'anchor article-content-title u-margin-xs-top u-margin-s-bottom'}, href=True)
i = 0
count = 0

# 提取网页中存储各paper附属信息的内容并用正则化提取所需片段，主要提取authors这个字典
otherinfo = soup.find_all(type="application/json")
auth = soup.find_all('auth')
soup2 = otherinfo[0]
soup2_str = soup2.text.replace('\\','')
soup2_str = soup2_str[1:-1]

# results = 正则化得到一个list，各元素对应每篇文章的信息
regex1 = '\"title\".*?\"authors\"\:\[\{.*?\}\]'
regex2 = '\"authors\"\:\[\{.*\}'
results = re.findall(regex1, soup2_str)
pass

# AuthorInfo返回print通讯与一作
def AuthorInfo(result): 
    while True:
        test = re.findall(regex1, result[2:])
        if not test:
            break
        else:
            result = test[0]
    # print(result)
    auths = re.findall(regex2, result)
    auths_str = auths[0][11:]
    refs = re.findall('\{.*?\}', auths_str)
    # print('\n', auths_str)
    print('作者： ', end='')

    # 提取每个作者的信息dict并print
    for i in range(len(refs)):
        refs[i] = json.loads(refs[i]) # 使refs[i]从str->dict
        print(refs[i]['givenName'], refs[i]['surname'], end='')
        if 'cor1' in refs[i]['refs']:
            print('(通讯)', end='')
        elif 'cor2' in refs[i]['refs']:
            print('(通讯)', end='')
        if refs[i]['id'] == 'auth-0':
            print('(一作)', end='')
        if i < len(refs)-1:
            print(', ', end='')
        else:
            print('.')
         

for title, link in zip(title, link):
    print('【{}】'.format(i+1), title.get_text())
    rl = url = 'http://fanyi.youdao.com/translate?smartresult=' \
               'dict&smartresult=rule&sessionFrom=https://www.baidu.com/link'

    data = {'from': 'AUTO', 'to': 'AUTO', 'smartresult': 'dict', 'client': 'fanyideskweb', 'salt': '1500092479607',
            'sign': 'c98235a85b213d482b8e65f6b1065e26', 'doctype': 'json', 'version': '2.1', 'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CL1CKBUTTON', 'typoResult': 'true', 'i': title.get_text()}

    data = urllib.parse.urlencode(data).encode('utf-8')
    response = urllib.request.urlopen(url, data)
    html = response.read().decode('utf-8')
    ta = json.loads(html)

    print('标题：', ta['translateResult'][0][0]['tgt'])
    if title.get_text() == 'Editorial Board':
        print('作者： None')
        count += 1
    elif title.get_text() == 'Publisher\'s Note': # 不是note
        print('作者： None')
        count += 1
    else:
        # print('作者：', name[i-count].get_text())
        AuthorInfo(results[i-count])

    print('链接：', 'https://www.sciencedirect.com{}'.format(link['href']), '\n')
    
    i += 1
