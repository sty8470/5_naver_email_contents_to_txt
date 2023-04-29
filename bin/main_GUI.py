import datetime
import linecache
import sys
import os
import threading
import re
from time import timezone

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from pytz import utc

from crawl_naver_emails import NCrawler
from ui.main_ui import Ui_MainWindow

# 관련 경로 sys 환경변수에 추가해주기
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../../')))

class NcrawlerUI(QMainWindow, Ui_MainWindow):

    sys._excepthook = sys.excepthook

    # 시스템 에러를 재 정의해서 로컬 sys에 저장하기
    def exception_hook(exctype, value, traceback):
        error = str(exctype) + " " + str(value) + " " + str(traceback)
        f = traceback.tb_frame
        lineno = traceback.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        error_text = 'EXCEPTION IN : {}, \nLINE : {}, \nWHICH : "{}", \nERROR : {}'.format(
            filename, lineno, line.strip(), error)
        print(error_text)
        # sys._excepthook(exctype, value, traceback)

    sys.excepthook = exception_hook

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon(os.path.join(current_path, '../img/naver.jpg')))
        self.setWindowTitle('네이버 이메일 다운로드')
        self.save_file_dir_icon = self.style().standardIcon(getattr(QStyle, 'SP_DirIcon'))
        self.save_file_dir_button.setIcon(self.save_file_dir_icon)

        self.save_file_init_dir_path = current_path
        self.NNB = ""
        self.nid_inf = ""
        self.NID_AUT = ""
        self.NID_JKL = ""
        self.NID_SES = ""

        self.button_init_signal()
        self.get_user_input()

    # 각각의 pushButton이 처음에 클릭되었을 때, 발현되는 이벤트들 정의하기 -> 저장할 디렉토리, 시작(실행), 취소 버튼 셋업
    def button_init_signal(self):
        self.save_file_dir_button.clicked.connect(self.find_safe_dir_to_save)
        self.execute_button.clicked.connect(self.check_before_accept)
        self.cancel_button.clicked.connect(self.close)

    # 저장할 디렉토리를 변수에 저장하기 -> 
    def find_safe_dir_to_save(self):
        self.save_file_dir_path = QFileDialog.getExistingDirectory(QFileDialog(),
                                                              caption="결과를 저장할 폴더를 선택 해주세요.",
                                                              directory=self.save_file_init_dir_path
                                                                   )
        if self.save_file_dir_path != '':
            self.save_file_line_edit.setText(self.save_file_dir_path)
        self.save_file_init_dir_path = self.save_file_line_edit.text()

    # 배치 시간(밀리세컨즈) * 1000으로 계산된 {}초만큼 self.accept 함수를 반복하여서 실행한다 -> self.accept는 크롤링 이벤트
    def set_batch_timer(self, batch_time):
        self.timer = QTimer()
        self.timer.setInterval(batch_time*1000)
        self.timer.timeout.connect(self.accept)
        self.timer.start()

    # 사용자 UI로 입력받은 input을 validate하는 부분 -> 사전 에러 방지
    def check_before_accept(self):
        if self.id_line_edit.text().strip() == '':
            QMessageBox.warning(self, "경고 메세지", "로그인 할 ID을 입력 해주세요!")
            return
        if self.password_line_edit.text().strip() == '':
            QMessageBox.warning(self, "경고 메세지", "로그인 할 PW를 입력 해주세요!")
            return
        if self.batch_time_line_edit.text().strip() == '':
            QMessageBox.warning(self, "경고 메세지", "배치시간을 초단위로 입력 해주세요!")
            return
        if self.save_file_line_edit.text().strip() == '':
            QMessageBox.warning(self, "경고 메세지", "다운로드 받을 디렉토리 경로를 설정 해주세요!")
            return
        if self.batch_time_line_edit.text().strip().isdigit() == False:
            QMessageBox.warning(self, "경고 메세지", "배치시간은 숫자만 입력 해주세요!")
            return

        # 시작버튼 더블 클릭 방지 및 배치 시간 타이머 설정 시작 -> 크롤링 시작전에 세팅 여부 확인
        self.execute_button.setText("작업 중")
        self.execute_button.setEnabled(False)

        batch_time = int(self.batch_time_line_edit.text().strip())
        self.set_batch_timer(batch_time)
        self.accept()

    # GUI에서 현재 정보 파싱 후 크롤링 시작 -> 크롤링 시에 쿠키값 저장
    def accept(self):
        self.user_id = self.id_line_edit.text().strip()
        self.user_pw = self.password_line_edit.text().strip()
        self.save_dir = self.save_file_line_edit.text().strip()

        # 쓰레드가 아직 작동 중인지 확인해서, 동작 중이면, 멈추고 새로운 크롤링 시작하기 -> Qtimer로 인한 복수 동작 방지
        try: 
            if self.crawler_thread.isFinished() == False:
                return
        except:
            pass

        self.append_text("크롤링을 시작합니다.")
        self.crawler_thread = NCrawler(self.user_id, self.user_pw, self.save_dir, self.NNB, self.nid_inf, self.NID_AUT, self.NID_JKL, self.NID_SES)
        self.crawler_thread.start()
        self.crawler_thread.cookie_signal.connect(self.cookie_save)
        self.crawler_thread.process_signal.connect(self.append_text)

    # 현재 시간 계산 후 -> 콘솔 출력 -> GUI 로그창에 표시
    @pyqtSlot(str)
    def append_text(self, msg):
        current_time = str(datetime.datetime.now()).split(".")[0]
        print(current_time + " - " + msg)
        self.plainTextEdit.appendPlainText(current_time + " - " + msg)

    # 시작 버튼 이름&기능 초기화 -> 타이머 중지 -> 크롤링 중지 -> 상태 전달
    def close(self):
        self.execute_button.setText("시작")
        self.execute_button.setEnabled(True)
        self.timer.stop()
        self.crawler_thread.terminate()
        self.append_text("크롤링을 중지합니다.")

    # 한번 성공적인 로그인 후 크롤링을 했으면 -> user_input.txt에 로그인 정보와 쿠키 정보 저장해 두기
    def save_user_input(self):
        with open(current_path + "/user_input.txt", 'w') as f:
            f.write(self.id_line_edit.text().strip() + "\n")
            f.write(self.password_line_edit.text().strip() + "\n")
            f.write(self.batch_time_line_edit.text().strip() + "\n")
            f.write(self.save_file_line_edit.text().strip() + "\n")
            f.write(self.NNB + "\n")
            f.write(self.nid_inf + "\n")
            f.write(self.NID_AUT + "\n")
            f.write(self.NID_JKL + "\n")
            f.write(self.NID_SES + "\n")
        f.close()
 
    # 미리 저장된 사용자의 로그인 관련된 정보들과 쿠키들을 불러와서 로딩하는 부분 -> 초기 UI 화면에 보여주기 + 이후에 reference 정보 저장
    def get_user_input(self):
        if os.path.exists(current_path + "/user_input.txt"):
            with open(current_path + "/user_input.txt", 'r') as f:
                user_data = f.read()
            f.close()
            user_data_list = user_data.split("\n")

            self.id_line_edit.setText(user_data_list[0])
            self.password_line_edit.setText(user_data_list[1])
            self.batch_time_line_edit.setText(user_data_list[2])
            self.save_file_line_edit.setText(user_data_list[3])
            self.NNB = user_data_list[4]
            self.nid_inf = user_data_list[5]
            self.NID_AUT = user_data_list[6]
            self.NID_JKL = user_data_list[7]
            self.NID_SES = user_data_list[8]

    # 로그인 시에 쿠키 관련 데이터 자식 클래스에서 받아서 저장하기
    @pyqtSlot(str, str, str, str, str)
    def cookie_save(self, NNB, nid_inf, NID_AUT, NID_JKL, NID_SES):
        self.NNB = NNB
        self.nid_inf = nid_inf
        self.NID_AUT = NID_AUT
        self.NID_JKL = NID_JKL
        self.NID_SES = NID_SES

    # exe 종료 시그널 -> 해당 객체가 소멸될때 __del__메소드 호출되며 -> 사용자의 로그인 정보를 로컬에 다시 저장
    def __del__(self):
        try:
            self.crawler_thread.terminate()
        except:
            pass
        try:
            self.save_user_input()
        except:
            pass
    
    # GUI를 닫으면, 호출되는 pyqt 내장함수
    def closeEvent(self, event: QCloseEvent) -> None:
        self.__del__()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NcrawlerUI()
    window.show()
    sys.exit(app.exec_())