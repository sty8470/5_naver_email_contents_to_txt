import datetime
import json

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup

import time 
import urllib
import random
import re
import pandas as pd
import os 
import sys 
import requests
import pyperclip
import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW

# 관련 상대경로 불러오기
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../../')))


class NCrawler(QThread):
    cookie_signal = pyqtSignal(str, str, str, str, str)
    process_signal = pyqtSignal(str)

    def __init__(self, user_id, user_pw, save_dir, NNB, nid_inf, NID_AUT, NID_JKL, NID_SES):
        '''
        NNB: 네이버 앱에서 발급받는 인증 토큰으로, 사용자를 식별하는 데 사용됩니다.
        nid_inf: 네이버 아이디 정보를 암호화한 값입니다.
        NID_AUT: 네이버 로그인 시 발급받은 인증 토큰입니다.
        NID_JKL: 네이버에서 사용하는 통계 정보를 수집하는 쿠키입니다.
        NID_SES: 사용자의 세션 정보를 담고 있는 쿠키입니다.
        '''
        super(NCrawler, self).__init__()
        self.user_id = user_id
        self.user_pw = user_pw
        self.save_dir = save_dir
        self.NNB = NNB
        self.nid_inf = nid_inf
        self.NID_AUT = NID_AUT
        self.NID_JKL = NID_JKL
        self.NID_SES = NID_SES

    # 로그인 과정을 통해서 필요한 쿠키 획득하기 -> 부모 GUI 클래스에 보내서 임시로 저장하기
    def login_naver_get_cookies(self):
        self.process_signal.emit("네이버 로그인 세션이 만료되어 다시 로그인합니다.")

        chrome_service = Service(ChromeDriverManager().install())
        chrome_service.creationflags = CREATE_NO_WINDOW

        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x1080')
        # options.add_argument("headless")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.implicitly_wait(time_to_wait=10)

        self.process_signal.emit("네이버 로그인을 시도합니다.")
        self.driver.get("https://nid.naver.com/nidlogin.login")
        id_pw_inputs = self.driver.find_elements(By.CLASS_NAME, "input_text")
        id_input = id_pw_inputs[0]
        id_input.click()
        self.driver.execute_script("document.getElementsByName('id')[0].value = '" + self.user_id + "'")
        pw_input = id_pw_inputs[1]
        pw_input.click()
        self.driver.execute_script("document.getElementsByName('pw')[0].value = '" + self.user_pw + "'")
        self.driver.find_element(By.ID, "log.login").click()

        time.sleep(3)
        cookies = self.driver.get_cookies()

        # 로그인시에 반드시 필요한 5가지 쿠키 값 획득해와서 저장 -> 부모 클래스로 보내기
        for i in range(len(cookies)):
            if cookies[i]["name"] == "NNB":
                self.NNB = cookies[i]["value"]
            if cookies[i]["name"] == "nid_inf":
                self.nid_inf = cookies[i]["value"]
            if cookies[i]["name"] == "NID_AUT":
                self.NID_AUT = cookies[i]["value"]
            if cookies[i]["name"] == "NID_JKL":
                self.NID_JKL = cookies[i]["value"]
            if cookies[i]["name"] == "NID_SES":
                self.NID_SES = cookies[i]["value"]

        self.cookie_signal.emit(self.NNB, self.nid_inf, self.NID_AUT, self.NID_JKL, self.NID_SES)
        self.driver.close()
        self.process_signal.emit("네이버 로그인을 완료 했습니다.")

    # 해당 페이지의 모든 메일 리스트 정보를 들고온다
    # 네이버 모든 메일함 API 엔트포인트 쿠키 및 params를 활용한 requests를 요청해서 -> 메일 리스트 json 획득 -> CRUD 연산수행 가능
    def get_mail_list(self, page):
        '''
        모든 메일함 (folderSN: -1)
        받은메일함 (folderSN: 0)
        보낸메일함 (folderSN: 1)
        스팸메일함 (folderSN: 2)
        휴지통 (folderSN: 3)
        '''
        url = 'https://mail.naver.com/json/list'
        headers = {
            'cookie': f"NNB={self.NNB}; nid_inf={self.nid_inf}; NID_AUT={self.NID_AUT}; NID_JKL= {self.NID_JKL}; NID_SES={self.NID_SES}=",
        }
        params = {
            "folderSN": "-1",
            "page": page,
            "viewMode": "time",
            "previewMode": "1",
            "sortField": "1",
            "sortType": "0",
            "u": self.user_id,
        }
        response = requests.post(url, headers=headers, params=params)
        data = json.loads(response.content.decode('utf-8'))
        return data

    # 쿠키를 활용한 requests을 가지고 메일 내용을 json으로 획득하기
    def get_mail_text(self, mailSN):
        url = 'https://mail.naver.com/json/read'
        params = {
            'mailSN': mailSN,
            'folderSN': '-1',
        }
        headers = {
            'cookie': f"NNB={self.NNB}; nid_inf={self.nid_inf}; NID_AUT={self.NID_AUT}; NID_JKL= {self.NID_JKL}; NID_SES={self.NID_SES}=",
        }
        response = requests.post(url, headers=headers, params=params)
        data = json.loads(response.content.decode('utf-8'))
        return data

    # 최신순 저장을 위한 메일 끝페이지 값 가져오기
    def get_last_page(self):
        data = self.get_mail_list(page=1)

        if data["Result"] != "OK":
            self.login_naver_get_cookies()
            data = self.get_mail_list(page=1)

        lastPage = data["lastPage"]
        self.lastPage = lastPage

    # 각 페이지에서 모든 메일 제목과 내용을 크롤링 -> 저장하기
    def get_mail_items(self):
        
        # 끝 페이지 부터 역순으로 for 문 실행하면서, 해당 데이터 파싱하기
        for page in range(self.lastPage, 0, -1):
            self.process_signal.emit(f"이메일 페이지 {page}를 크롤링 합니다.")

            data = self.get_mail_list(page=page)

            # 혹시나 메일 리스트 json 결과가 OK가 아니면 로그인 재시도
            if data["Result"] != "OK":
                self.login_naver_get_cookies()
                data = self.get_mail_list(page=1)

            # 메일 리스트에 있는 각 메일의 정보
            mailData = data["mailData"]

            # 오래된 메일에서 부터 세부 element 추출하기
            reverse_list = list(reversed(mailData))
            for mail in reverse_list:
                mailSN = mail["mailSN"] # 메일 고유번호 int
                subject = mail["subject"] # 메일 제목 string
                receivedTime = mail["receivedTime"] # 메일 수신시간 timestamp
                received_datetime = str(datetime.datetime.fromtimestamp(receivedTime)) # 수신시간 datetime화
                from_name = mail["from"]["name"] # 발신자 이름 string
                from_email_address = mail["from"]["email"] # 발신자 이메일 전체 주소 string
                from_email = from_email_address.split('@')[0] # 발신자 이메일 아이디 string

                data = self.get_mail_text(mailSN)

                # 메일 body에서 줄바꿈 등 제거하기
                mail_body = data["mailInfo"]["body"]
                mail_text = BeautifulSoup(mail_body, 'html.parser'
                          ).text.replace('\n    ', '').replace('\n', '').replace('    ', "")

                # output.txt 없으면 생성하기
                if os.path.exists(self.save_dir + "/output.txt") == False:
                    f = open(self.save_dir + "/output.txt", 'w', encoding='utf-8')
                    f.close()

                # 기존에 저장된 output.txt 읽어오기
                with open(self.save_dir + "/output.txt", "r+", encoding='utf-8') as f:
                    content = f.read()

                # 메일 고유 번호 리스트를 관리하기 위한 parsing 부분 -> 만에 하나 중복 방지를 위해서
                content_list = content.split("\n")
                previous_mailSN_list = []
                for c in range(len(content_list)):
                    if "mailSN" in content_list[c]:
                        previous_mailSN = content_list[c].split("mailSN : ")[1]
                        previous_mailSN_list.append(previous_mailSN)

                # 메일 고유번호가 이미 previous_mailSN_list 있으면 무시하고 -> continue처리하기
                if str(mailSN) in previous_mailSN_list:
                    continue

                # output.txt 파일을 열어서, 아래의 항목들을 각각 줄에 기술합니다.                            
                with open(self.save_dir + "/output.txt", "w", encoding='utf-8') as f:
                    f.write("mailSN : " + str(mailSN) + "\n")
                    f.write("receivedTime : " + str(received_datetime) + "\n")
                    f.write("from_name : " + str(from_name) + "\n")
                    f.write("from_email : " + str(from_email) + "\n")
                    f.write("subject : " + str(subject) + "\n")
                    f.write("mail_text : " + str(mail_text) + "\n")
                    f.write("\n")
                    f.write(content)
                f.close()
                time.sleep(1)
    
    def run(self):
        '''
        크롤링 실행 순서 -> 최초 로그인 -> 전체 페이지 수 조사 -> 각 페이지의 메일 리스트 획득 -> 내부 내용 획득
        '''
        if self.NNB == "":
            self.login_naver_get_cookies()

        self.get_last_page()
        self.get_mail_items()

        self.process_signal.emit("메일 크롤링을 완료했습니다.")