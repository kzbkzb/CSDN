
# 获取网站的sitemap
import requests,sys
import urllib
from bs4 import BeautifulSoup
import urllib.parse
import time
import urllib.request
import random
from fake_useragent import UserAgent
 
url = "http://www.ygdy8.net/html/zongyi2013/qitazongyi/list_103_16.html"
domain = "ygdy8.net"
#整个网站的页面
sites = set()
#需要遍历的页面
waitUrls = set()

#获取IP列表并检验IP的有效性      
def get_ip_list():      
    f=open('IP.txt','r')      
    ip_list=f.readlines()      
    f.close()      
    return ip_list      
      
#从IP列表中获取随机IP      
def get_random_ip(ip_list):      
    proxy_ip = random.choice(ip_list)      
    proxy_ip=proxy_ip.strip('\n')      
    proxies = {'https': proxy_ip}      
    return proxies

ip_list = get_ip_list()

def get_local_pages(url,domain):
    global sites
    global waitUrls
    global ip_list
    repeat_time = 0
    pages = set()

    #防止url读取卡住
    while True:
        try:
            time.sleep(2)
            print ("Opening the web : "+url)
            proxies=get_random_ip(ip_list)
            headers = {"UserAgent":str(UserAgent().random)}
            web = requests.get(url=url, proxies=proxies, headers=headers, timeout=5)#
            print ("Success to Open the web")
            break
        except :
            print ("Open Url Failed !!! Repeat",sys.exc_info())
            time.sleep(10)
            repeat_time = repeat_time+1
            if repeat_time == 5:
                return
    #解析web网页对象
    web.encoding = 'utf-8'
    soup = BeautifulSoup(web.text, 'lxml')
    tags = soup.findAll(name='a')
    for tag in tags:
       	
        #避免参数传递异常
        try:
            ret = tag['href']
        except:
            print ("Maybe not the attr : href")
            continue
        #分解URL
        o = urllib.parse.urlparse(ret)

        #处理相对路径url
        if o[0] is "" and o[1] is "":
            print ("Fix  Page: " +ret)
            if ret == '#':
                pass
            elif '/html/' in ret:
                url_obj = urllib.parse.urlparse(url)
                ret = url_obj[0] + "://" + url_obj[1] +'/'  + ret
            else:
                ret = url.replace('index.html','') + ret
            #保持url的干净
            print(ret)
            ret = ret[:8] + ret[8:].replace('//','/')
            print(ret)
            o = urllib.parse.urlparse(ret)
            #这里不是太完善，但是可以应付一般情况
            if '../' in o[2]:
                paths = o[2].split('/')
                for i in range(len(paths)):
                    if paths[i] == '..':
                        paths[i] = ''
                        if paths[i-1]:
                            paths[i-1] = ''
                tmp_path = ''
                for path in paths:
                    if path == '':
                        continue
                    tmp_path = tmp_path + '/' +path
                ret =ret.replace(o[2],ret_path)
            print ("FixedPage: " + ret)
           
           
        #协议处理
        if 'http' not in o[0]:
            print ("Bad  Page 1 ：" + str(ret.encode('utf-8')))
            continue
       
        #url合理性检验
        if o[0] is "" and o[1] is not "":
            print ("Bad  Page 2 : " + ret)
            continue
       
        #域名检验
        if domain not in o[1]:
            print ("Bad  Page 3 : " + ret)
            continue
        
        #整理，输出
        newpage = ret
        if newpage not in sites and newpage not in waitUrls:
            print ("Add New Page: " + newpage)
            
            # newpage = newpage.replace('//',"/")
            urlSplit = newpage.split('/')

            #将界面分开存放
            if urlSplit[-2].isdigit() and len(urlSplit[-2])==8:
                #信息界面存入
                sites.add(newpage)
                f = open("test_sites.txt", 'a+')
                f.write(newpage + '***'+ url + '\n')
                f.close()
            else:
                #主干界面存入
                waitUrls.add(newpage)
                f = open("test_waitUrls.txt", 'a+')
                f.write(newpage +'***'+ url +'\n')
                f.close()
                pages.add(newpage)

    return pages
 
#dfs算法遍历全站
def dfs(pages):
    #无法获取新的url说明便利完成，即可结束dfs
    if pages is set():
        return
    if pages is None:
    	return

    global domain

    for page in pages:
        print ("Visiting" + page)
        url = page
        pages = get_local_pages(url, domain)
        dfs(pages)
   
    print ("sucess")
 
 
pages = get_local_pages(url, domain)
dfs(pages)
for i in sites:
    print (i)