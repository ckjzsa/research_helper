from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import requests
import json
import regex as re
import time


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

        # results = 正则化得到一个list，各元素对应每篇文章的信息
        self.regex0 = '\"totalResults\":\d+'
        self.regex1 = '\"title\".*?\"authors\"\:\[\{.*?\}\]'
        self.regex2 = '\"authors\"\:\[\{.*\}'
        self.regex3 = ',\{\"#name\":\"textfn\".*?\}'
        self.otherinfo = self.soup.find_all(type="application/json")
        self.auth = self.soup.find_all('auth')
        

    # =============== ↓ WR文章作者 ↓ ===============
    def wr_author_results(self):
        # 提取网页中存储各paper附属信息的内容并用正则表达式提取所需片段，主要提取authors这个字典
        soup2 = self.otherinfo[0]
        # print(self.otherinfo[0])
        # self.soup2_str = self.soup2.contents[0].replace('\\', '')
        soup2_str = soup2.contents[0].replace('\\', '')
        soup2_str = soup2_str[1:-1]

        number = re.findall(self.regex0, soup2_str)
        number = int(re.findall('\d+', number[0])[0])
        results = re.findall(self.regex1, soup2_str)
        return results

    def author_info_wr(self, result):
        authors = {'一作': [], '通讯': [], '其他': []}
        while True:
            test = re.findall(self.regex1, result[2:]) # 删除多余部分，直到test为空
            if not test: # 保留test为空的前一步
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

    # =============== ↓ ES&T文章作者 ↓ ===============
    def author_info_est(self, result):
        authors = {'一作': [], '通讯': [], '其他': []}
        cut = lambda raw_str, to_cut: [piece.strip() for piece in raw_str.split(to_cut)]
        authors_lst = cut(result, 'and')
        authors_new_lst = []

        for author in authors_lst:
            authors_new_lst += cut(author, ',')

        for author in authors_new_lst:
            if '*' in author:
                authors['通讯'].append(author[:-1])
            else:
                authors['其他'].append(author)

        authors['一作'].append((authors_new_lst[0].split('*'))[0]) 
        # 后输出一作，怕和通讯矛盾，这样处理方便
        # 至此，authors字典中已储存了所有的作者名字（注意：通讯名后带*号）

    # =============== ↓ WR第一单位 ↓ ===============
    def company_wr(self, paper_url):
        html_url = requests.get(paper_url, headers=self.headers)
        soup_comp = BeautifulSoup(html_url.content, features='lxml')
        info = soup_comp.find(type="application/json").get_text()

        try:
            comp_info = (re.findall(self.regex3, info))[0][24:-2]
        except:
            comp_info = None

        return comp_info
    
    # =============== ↓ ES&T第一单位 ↓ ===============
    def company_est(self, paper_url):
        html_url = requests.get(paper_url, headers=self.headers)
        soup_comp = BeautifulSoup(html_url.content, features='lxml')
        comp = soup_comp.find('div', {'class': 'loa-info-affiliations-info'})

        return comp.get_text()

    # =============== ↓ 整合结果 ↓ ===============
    def get_results(self):
        res = {'标题': [], '中文标题': [], '作者': [], '链接': [], '单位': []}
        results = []

        if 'water-research' in self.url:
            results = self.wr_author_results()

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

            if 'water-research' in self.url:
                paper_url = 'https://www.sciencedirect.com{}'.format(link['href'])
                # results = self.wr_author_results()

                if 'Editorial Board' in title.get_text():
                    res['作者'].append('None')
                    self.count += 1
                elif title.get_text() == 'Publisher\'s Note':  # 不是note
                    res['作者'].append('None')
                    self.count += 1
                else:
                    # print('作者：', name[i-count].get_text())
                    res['作者'].append(self.author_info_wr(results[self.i - self.count]))

                res['链接'].append(paper_url)
                res['单位'].append(self.company_wr(paper_url))         

            elif 'esthag' in self.url:
                paper_url = 'https://pubs.acs.org{}'.format(link.a['href'])

                res['作者'].append(self.author_info_est(self.name.get_text()))
                res['链接'].append(paper_url)
                res['单位'].append(self.company_est(paper_url))

            self.i += 1

        return res

# =============== ↓ 输入期刊和期数开始运行 ↓ ===============
global headers 
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }


def get_latest_wr_vol():    
    wr_main_page = 'https://www.sciencedirect.com/journal/water-research'
    html_url = requests.get(wr_main_page, headers=headers)
    soup_comp = BeautifulSoup(html_url.content, features='lxml')
    info = soup_comp.find(type="application/json").get_text()
    vol = re.findall('latestIssue\":\".*?\"', info.replace('\\',''))[0].split('vol/')[1].split('/')[0]

    return vol # vol的type是str

def get_latest_est_vol():
    est_main_page = 'https://pubs.acs.org/journal/esthag'
    html_url = requests.get(est_main_page, headers=headers)
    soup_comp = BeautifulSoup(html_url.content, features='lxml')
    info = soup_comp.find("div", {"class": "jhHeader_right"}).get_text()
    vol = re.findall('Volume\s\d*', info)[0][7:]
    iss = re.findall('Issue\s\d*', info)[0][6:]

    return (vol, iss) # tuple里的type是str

def get_url(journal='wr', vol = '50', issue = '10'):
    
    main_url = "https://www.sciencedirect.com/journal/water-research/vol/180/suppl/C"
    journal = input("请输入期刊（WR或ES&T）,回车结束：\n")
    if journal.lower() == 'wr': 
        journal = 'wr'
        new_vol = get_latest_wr_vol() # 最新一期的卷号
        print('最新一期WR期刊期数为', new_vol, end = ',')
        vol = input("请输入Volume期数（如180），回车结束：\n")
        main_url = "https://www.sciencedirect.com/journal/water-research/vol/{}/suppl/C".format(vol)

    elif 'es' in journal.lower():
        journal = 'est'
        new_vol = get_latest_est_vol() # 最新一期的卷号
        print('最新一期ES&T期刊Volume数为', new_vol[0], ',Issue数为', new_vol[1], end = ',')
        vol = input("请输入Volume数（如50），回车结束：\n")
        issue = input("请输入Issue数（如10），回车结束：\n")
        main_url = 'https://pubs.acs.org/toc/esthag/{}/{}'.format(vol, issue)

    else:
        print('无效！请重新输入。')

    return main_url

def main():
    #try:
        main_url = get_url()
        # main_url = "https://pubs.acs.org/toc/esthag/53/24"
        print("开始爬取......")
        time.sleep(2)
        crawler = Crawler(main_url)
        crawler.get_results()
    #except:
        #print('无效！请重新输入。')
        #pass


if __name__ == '__main__':
    main()