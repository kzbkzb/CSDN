'''
这是一个将网页解析过程进行包装的文件
采用了代理ip，来源：http://www.xicidaili.com/wt/
环境： python 3.6.5
需要安装的包：bs4、requests、lxml、fake_useragent
注意事项：如果代码无法运行，建议升级一下requests
建议：在爬不同网站时（http型与https型）建议将ip.txt文件删掉，重新下载一份，重新下载的ip比较有针对性，访问速度会稍微快一些
'''
from bs4 import BeautifulSoup  
import lxml
import requests  
import random,os,time
from fake_useragent import UserAgent
from urllib.parse import urlparse

class IPCrawler(object):
	"""docstring for IPCrawler"""
	def __init__(self,url,ip_stype):
		self.url = url
		self.ip_stype = ip_stype

	#下载ip文件
	def getIpFile(self):
		print('开始从互联网中获取ip，并将其中有效的ip写入文件当中')
		#进去网站爬取ip
		for url_target in ['http://www.xicidaili.com/wt/','http://www.xicidaili.com/wn/','http://www.xicidaili.com/nt/','http://www.xicidaili.com/nn/']:
			self.get_goubanjia(url_target)
		if not os.path.exists('ip.txt'): 
			self.getIpFile()
	
	#验证ip，返回True/False值
	def verifyIP(self,proxy):
		print('开始判断{}的有效性'.format(proxy))
		try:
			#设置ip
			proxies = {'{}'.format(self.ip_stype):proxy}
			#设置headers
			headers = {'User-Agent':str(UserAgent().random)}
			#发生requests请求
			print('requests前的proxies：{}'.format(proxies))
			req = requests.get(self.url, headers=headers, proxies=proxies, verify=False, timeout=(6,14))
		except Exception as e:
			print('requests后的proxies：{}'.format(proxies))
			print('{}代理ip无效'.format(proxies))
			print('在检验过程中遇到的requests错误原因是：{}'.format(e))
			return False
		else:
			print('requests后的proxies：{}'.format(proxies))
			print('{}代理ip有效'.format(proxies))
			return True
		finally:
			print('{}代理ip有效性判断完成'.format(proxies))

	#http://www.xicidaili.com/wt/
	def get_goubanjia(self,url_target):
		try:
			#设置headers
			headers = {'User-Agent':str(UserAgent().random)}
			#发送requests请求
			req = requests.get(url_target,headers=headers, timeout=5)
			#校正网页编码
			req.encoding = req.apparent_encoding
			#对网页进行解析
			soup = BeautifulSoup(req.text, 'lxml')
			tr_list = soup.find_all('tr')

			for each in range(1, 31):
				print('已经筛选了{}条ip'.format(each))
				print("获取地址")
				#获取地址
				td = tr_list[each].find_all('td')
				a = td[1].get_text()
				print("获取端口")
				#获取端口
				b = td[2].get_text()
				#将有效的ip写入文件
				proxy = 'http://' + a+':'+b
				#检验ip是否有效，将有效的ip写入文件当中
				if self.verifyIP(proxy):
					f = open('ip.txt','a+',encoding='utf-8')
					f.write(proxy+'\n')
					f.close()
				#输出爬取到的信息
				print(proxy)
		except Exception as e:
			print(str(e))
			print('{}：网站页面发生变动，请及时更新'.format(url_target))

class WebParse(IPCrawler):
	"""docstring for WebParse"""
	def __init__(self,url,ip_stype):
		super().__init__(url,ip_stype)
		self.url = url
		self.ip_stype = ip_stype

	#解析网页
	def parseHTML(self):
		flag=True
		while (flag!=False):
			try:
				try:
					#设置代理ip
					proxy = self.createRandomIp()
					#设置proxies
					proxies = {'{}'.format(self.ip_stype):proxy}
					#设置代理headers
					headers = {'User-Agent':str(UserAgent().random)}
					req = requests.get(self.url, proxies=proxies, headers=headers, verify=False, timeout=(9,21))
					flag=False
				except Exception as e:
					print('上一次请求失败，10秒后我们将进行下一次请求')
					print("上一次requests请求失败的原因是{}".format(e))
					print('上一次请求的代理ip为：{}'.format(proxy))
					time.sleep(10)
					#验证proxy的有效性，并对无效proxy进行处理
					proxy = self.verifyProxy(proxy)
					#设置proxies
					proxies = {'{}'.format(self.ip_stype):proxy}
					#设置代理headers
					headers = {'User-Agent':str(UserAgent().random)}
					req = requests.get(self.url, proxies=proxies, headers=headers, verify=False, timeout=(9,21))
					flag=False
			except:
				pass
		
		req.encoding = req.apparent_encoding
		soup = BeautifulSoup(req.text, 'lxml')

		return soup

	#获取随机ip地址
	def createRandomIp(self):
		print('开始获取随机ip地址')
		#从文件中获取ip地址
		f = open('ip.txt', 'r', encoding='utf-8')
		self.ip_list = f.readlines()
		f.close()

		#当文件为空时，重新下载文件
		if len(self.ip_list)==0:
			print('现在列表为空，我们将重新获取ip')
			# IPCrawler = IPCrawler('http://www.weixinquanquan.com/pub/1.html')
			super().getIpFile()

		#生成随机proxy
		proxy = random.choice(self.ip_list).strip('\n')
		return proxy

	#删除proxy
	def deleteProxy(self,proxy):
		print('删除无效proxy：{}'.format(proxy))
		f = open('ip.txt', 'r', encoding='utf-8')
		proxy_list = f.readlines()
		f.close()
		#删除列表中的换行符号
		proxy_list = [proxy.replace('\n','') for proxy in proxy_list]
		#删除原文件
		os.remove('ip.txt')
		#删除指定的proxy
		proxy_list.remove(proxy)
		#当文件为空时，重新下载文件
		if len(proxy_list)==0:
			print('现在列表为空，我们将重新获取ip')
			#调用父类下载新的ip文件
			super().getIpFile()
		#将信息重新写入文件
		f = open('ip.txt', 'a+', encoding='utf-8')
		for each in proxy_list:
			f.write(each+'\n')
		f.close()


	#验证proxy的有效性，并对无效proxy进行处理
	def verifyProxy(self,proxy):
		try:
			#设置ip
			proxies = {'{}'.format(self.ip_stype):proxy}
			#设置headers
			headers = {'User-Agent':str(UserAgent().random)}
			#发生requests请求
			req = requests.get(self.url, headers=headers, proxies=proxies, timeout=(9,21))
		except Exception as e:
			# print('{}代理ip无效，我们将为您重新分配proxy'.format(proxies))
			print('在检验过程中遇到的requests错误原因是：{}'.format(e))
			#删除无效的proxy
			self.deleteProxy(proxy)
			#获取新的proxy
			proxy = self.createRandomIp()
			#验证新proxy是否有效
			proxy = self.verifyProxy(proxy)
			return proxy
		else:
			print('{}代理ip有效'.format(proxies))
			return proxy

class parseHTMLPack(WebParse,IPCrawler):
	"""docstring for parseHTMLPack"""
	def __init__(self, url, ip_stype):
		#设置父类WebParse,IPCrawler
		WebParse.__init__(self,url,ip_stype)
		IPCrawler.__init__(self,url,ip_stype)
		self.url = url
		self.ip_stype = ip_stype
	
	#这是一个采用了代理ip的函数，测试完后使用该函数
	def parseHTMLPack(self):
		o = urlparse(self.url)
		self.ip_stype = o[0]
		#先判断是否存在ip文件
		if not os.path.exists('ip.txt'): 
			super().getIpFile()

		soup = super().parseHTML()
		return soup

	#未采用代理ip，在测试时使用该函数
	def parseHTML_BeautifulSoup(self):
		#设置headers
		headers = {'User-Agent':str(UserAgent().random)}
		#发送requests请求
		req = requests.get(self.url, headers=headers, verify=False, timeout=(9,21))
		#使编码格式一致，避免乱码
		req.encoding = req.apparent_encoding
		#解析网页
		soup = BeautifulSoup(req.text, 'lxml')
		return soup

if __name__ == '__main__':
	for each in range(1,10):
		parseHTMLPack = parseHTMLPack('https://blog.csdn.net/qq_38251616/article/details/81435449','https')
		parseHTMLPack.parseHTMLPack()


# 		