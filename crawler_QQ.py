#爬取QQ群中群员的个人信息
#coding=utf-8

from lxml import etree
import time
from selenium import webdriver

class qqGroupSpider():
    '''
    Q群爬虫类
    '''
    def __init__(self, driver,qq,passwd,qqgroup):
        '''
        初始化根据用户信息登录到Q群管理界面
        :param driver:
        :param qq:
        :param passwd:
        :param qqgroup:
        :param writefile:
        '''
        url = "https://qun.qq.com/member.html#gid=" + str(qqgroup)
        self.driver=driver
        driver.delete_all_cookies()
        driver.get(url)
        time.sleep(1)
        driver.switch_to.frame("login_frame")  # 进入登录iframe
        time.sleep(1)
        change = driver.find_element_by_id("switcher_plogin")
        change.click()
        driver.find_element_by_id('u').clear()  # 选择用户名框
        driver.find_element_by_id('u').send_keys(qq)
        driver.find_element_by_id('p').clear()
        driver.find_element_by_id('p').send_keys(passwd)
        driver.find_element_by_class_name("login_button").click()
        time.sleep(1)

    def scroll_foot(self,driver):
        '''
        控制屏幕向下滚动一下
        :param driver:
        :return:
        '''
        js = "var q=document.documentElement.scrollTop=100000"
        return driver.execute_script(js)

    def getTbodyList(self, driver):
        print("getTbodyList()函数运行过")
        return driver.find_elements_by_xpath('//div[@class="group-memeber"]//tbody[contains(@class,"list")]')

    def parseMember(self, mb):
        '''
        解析每个人各项描述，以逗号隔开，返回一个成员的基本情况
        :param mb:
        :return:
        '''
        print("parseMember()函数运行过")

        td = mb.find_elements_by_xpath('td')
        print("td长度为：{}".format(len(td)))

        qId = td[1].text.strip()
        nickName = td[2].find_element_by_xpath('span').text.strip()
        card = td[3].find_element_by_xpath('span').text.strip()
        qq = td[4].text.strip()
        sex = td[5].text.strip()
        qqAge = td[6].text.strip()
        joinTime = td[7].text.strip()
        lastTime = td[8].text.strip()

        a = (qId + "|" + qq + "|" + nickName + "|" + card + "|" + sex + "|" + qqAge + "|" + joinTime + "|" + lastTime)
        print(a)
        return a

    def parseTbody(self, html):
        '''
        解析tbody里面的内容，一个tbody里面有多个成员，
        解析完成后，返回成员基本情况的列表
        :param html:
        :return:
        '''
        # selector = etree.HTML(html)
        print("parseTbody()函数运行过")
        memberLists = []
        for each in html:
            memberList = each.find_elements_by_xpath('tr[contains(@class,"mb mb")]')
            memberLists += memberList

        print("memberLists长度为：{}".format(len(memberLists)))
        memberLists_data = []
        for each in memberLists:   
            memberLists_data.append(self.parseMember(each))
        return memberLists_data

    def parseAndWrite(self, tbody):
        '''
        解析HTML中的tbody，解析完成后写入到本地文件
        :param tbody:
        :return:
        '''
        print("parseAndWrite()函数运行过")

        memberList = self.parseTbody(tbody)

        with open("1607.csv", 'a+', encoding="utf-8") as f:
            for each in memberList:
                f.write(str(each)+"\n")


def main():
    qq = "QQ账号"
    passwd = "QQ密码"
    qqgroup = "想要爬取的QQ群群号"
    
    driver = webdriver.Chrome()
    spider=qqGroupSpider(driver,qq,passwd,qqgroup)
    time.sleep(10)
    # 找到QQ群的人数
    qqNum = int(driver.find_element_by_xpath('//*[@id="groupMemberNum"]').text.strip())
    print("QQ群人数为："+str(qqNum))
    curren_qq_num=0
    prelen=0

    
    while curren_qq_num != qqNum:
        curren_qq_num=len(driver.find_elements_by_xpath('//*[@id="groupMember"]//td[contains(@class,"td-no")]'))
        #不停的向下滚动屏幕，直到底部
        spider.scroll_foot(driver)
        #每次滚动休息1秒
        time.sleep(1)
     
        tlist = spider.getTbodyList(driver)

        spider.parseAndWrite(tlist[prelen:])

        prelen = len(tlist)#更新tbody列表的长度

    driver.quit()

if __name__ == '__main__':
    main()