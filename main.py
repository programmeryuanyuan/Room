LOCAL=1
# selenium 4
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import sys
import time
import logging
import os
import random

import requests
from datetime import datetime


# os.environ['WDM_LOG'] = str(logging.NOTSET)
MAIN_URL='https://unswlibrary-bookings.libcal.com/'
LAW_LIB={'name':'law_lib','path':'/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/p[5]/button[1]'}
LAW_CAPACITY5='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/form[1]/div[4]/div[1]/select[1]/option[3]'
LAW_CAPACITY8='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/form[1]/div[4]/div[1]/select[1]/option[4]'
SHOW_AVAILABILITY='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/form[1]/div[7]/div[1]/button[1]'
NEXT_BUTTON='/html[1]/body[1]/div[3]/main[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/button[2]'
CHOOSE_TIME='/html[1]/body[1]/div[3]/main[1]/div[1]/div[1]/div[1]/div[4]/form[1]/fieldset[1]/div[1]/div[1]/div[1]/div[1]/div[1]/select[1]/option[ID]'
SUBMIT1='/html[1]/body[1]/div[3]/main[1]/div[1]/div[1]/div[1]/div[4]/form[1]/fieldset[1]/div[2]/button[1]'
SUBMIT2='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/button[1]'
SUBMIT3='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[3]/form[1]/fieldset[1]/div[4]/div[1]/button[1]'
START_TIME='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[4]'
END_TIME='/html[1]/body[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[5]'

Rooms={'LAWG20':{'lib':LAW_LIB,'cap':LAW_CAPACITY8,'line':'/html[1]/body[1]/div[3]/main[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/div[1]/div[2]/div[ID]/a[1]'}}


def update_chrome_driver():
    global driver_path
    driver_path=ChromeDriverManager().install()
    # print (driver_path)
    # driver = webdriver.Chrome(service=Service(driver_path))

class Driver:
    def __init__(self,Debuger):
        global driver_path
        if Debuger==None:
            update_chrome_driver()
        options=webdriver.ChromeOptions()
        # options.add_experimental_option("detach", True)#程序退出后浏览器保持打开
        options.add_argument("disable-infobars")#关闭“被自动控制”标签(好像没用)
        # prefs = {"profile.managed_default_content_settings.images": 2,'permissions.default.stylesheet':2}
        # options.add_experimental_option("prefs", prefs)
        if Debuger==None:
            options.add_argument(r'--user-data-dir=./Data')
            self.driver = webdriver.Chrome(service=Service(driver_path), options=options)
        else:
            options.add_experimental_option("debuggerAddress", Debuger)
            options.add_experimental_option('w3c', True)
            options.page_load_strategy = 'eager'#不完全加载
            self.driver = webdriver.Chrome(options=options)
        # options.add_argument("incognito")#隐身模式
        # self.driver = webdriver.Chrome(service=Service(driver_path),options=options)
        # print("启动浏览器")
        self.current='null'
        self.force_to_main_page()
    def force_to_main_page(self):
        self.driver.get(MAIN_URL)
        self.current='main'
    def switch_to_main_page(self):
        if(self.current=='main'):return
        return self.force_to_main_page()
    def switch_to_lib(self,lib):
        if(self.current==lib['name']):return
        try:
            self.switch_to_main_page()
            self.driver.find_element(by='xpath',value=lib['path']).click()
            self.current=lib['name']
        except:
            self.force_to_main_page()
            return self.switch_to_lib(lib)
    def book(self,room,date,start,length):
        #now only law lib
        start=int(start*2)
        length=int(length*2)
        try:
            self.switch_to_lib(room['lib'])
            time.sleep(0.5)
            self.driver.find_element(by='xpath',value=room['cap']).click()
            time.sleep(0.3)
            self.driver.find_element(by='xpath',value=SHOW_AVAILABILITY).click()
            time.sleep(0.3)
            for i in range(date):
                self.driver.find_element(by='xpath',value=NEXT_BUTTON).click()
            time.sleep(0.1)
            for i in range(start+1,start+length+1):
                timer=20
                while 1:
                    try:
                        grid=self.driver.find_element(by='xpath',value=room['line'].replace('ID',str(i)))
                        break
                    except:
                        time.sleep(0.1)
                        timer-=1
                        print('Reading timetable failed({0})'.format(timer))
                        if timer==0: 
                            self.current='null'
                            print('Not open yet')
                            return False
                print(grid.get_attribute('title'))
                if 'Unavailable' in grid.get_attribute('title'):
                    self.current='null'

                    return False
            grid=self.driver.find_element(by='xpath',value=room['line'].replace('ID',str(start+1)))
            # time.sleep(0.5)
            grid.send_keys('\n')
            time.sleep(0.3)

            grid=self.driver.find_element(by='xpath',value=room['line'].replace('ID',str(start+1)))
            if 'Unavailable' in grid.get_attribute('title'):
                self.current='null'
                return False
            time_box=self.driver.find_element(by='xpath',value=CHOOSE_TIME.replace('ID', str(length)))
            time_box.click()
            time.sleep(1)
            self.driver.find_element(by='xpath',value=SUBMIT1).click()
            time.sleep(1)
            self.driver.find_element(by='xpath',value=SUBMIT2).click()
            time.sleep(1)
            
            t=self.driver.find_element(by='xpath',value=START_TIME).text
            print('From:',t)
            t=self.driver.find_element(by='xpath',value=END_TIME).text
            print('To:  ',t)
            self.driver.find_element(by='xpath',value=SUBMIT3).click()
            self.current='null'
            return True
        except:
            self.force_to_main_page()
            return False
    
class Booker:
    def run(self,browser,inque,outque):
        self.driver=Driver(browser)
        while 1:
            room,date,start,length=inque.get()
            outque.put(self.driver.book(room,date,start,length))

def test():
    driver=Driver(None)
    driver.book(Rooms['LAWG20'], 14, 1, 0.5)
    exit(0)
if __name__=='__main__':
    assert(len(sys.argv)>5)
    #LAWG20 14 11 4
    bid=sys.argv[1]
    if bid=='0':LOCAL=1
    roomname=sys.argv[2]
    date=int(sys.argv[3])
    start=float(sys.argv[4])
    length=float(sys.argv[5])
    assert(roomname in Rooms)
    room=Rooms[roomname]
    if LOCAL:
        driver=Driver(None)
    else:
        url = "http://localhost:50325/api/v1/browser/active?user_id=" + bid
        time.sleep(1.1)
        response = requests.request("GET", url, headers={}, data={}).json()
        assert(response['code'] == 0)
        if(response['data']['status'] == 'Inactive'):
            open_url = "http://local.adspower.net:50325/api/v1/browser/start?user_id=" + bid

            time.sleep(1)
            resp = requests.get(open_url).json()
            if resp["code"] != 0:
                print(resp["msg"])
                print("please check ads_id")
                sys.exit()
            url = "http://localhost:50325/api/v1/browser/active?user_id=" + bid
            time.sleep(1.1)
            response = requests.request("GET", url, headers={}, data={}).json()
            assert(response['code'] == 0)
        Debugger = response['data']['ws']['selenium']
        driver=Driver(Debugger)
    print(bid,'Started')
    while 1:
        # print(datetime.now().time().hour,datetime.now().time().minute)
        if datetime.now().time().hour==23 and datetime.now().time().minute>=58:
            
            T=10
            while 1:
                print(datetime.now(),'Start new booking')
                res=driver.book(room, date, start, length)
                # print(res)
                if res:
                    print(datetime.now(), '{0} Booking success: after {1} days, room {2}, from {3} to {4}'.format(bid,date,roomname,start,start+length))
                    time.sleep(120)
                    break
                else:
                    T-=1
                    print(datetime.now(), '{0} Try({5}) failed: after {1}, room {2}, from {3} to {4}'.format(bid,date,roomname,start,start+length,T))
                    if T<=0:
                        print(datetime.now(), '{0} Booking failed: after {1}, room {2}, from {3} to {4}'.format(bid,date,roomname,start,start+length))
                        # time.sleep(60)
                        break
        else:
            time.sleep(1)
            continue
