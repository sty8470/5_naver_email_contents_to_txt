# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(536, 374)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cancel_button = QtWidgets.QPushButton(self.centralwidget)
        self.cancel_button.setMinimumSize(QtCore.QSize(0, 40))
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout_2.addWidget(self.cancel_button, 1, 1, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.batch_time_label = QtWidgets.QLabel(self.centralwidget)
        self.batch_time_label.setObjectName("batch_time_label")
        self.gridLayout.addWidget(self.batch_time_label, 2, 0, 1, 1)
        self.id_label = QtWidgets.QLabel(self.centralwidget)
        self.id_label.setMinimumSize(QtCore.QSize(90, 0))
        self.id_label.setObjectName("id_label")
        self.gridLayout.addWidget(self.id_label, 0, 0, 1, 1)
        self.save_file_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.save_file_line_edit.setMinimumSize(QtCore.QSize(0, 30))
        self.save_file_line_edit.setObjectName("save_file_line_edit")
        self.gridLayout.addWidget(self.save_file_line_edit, 3, 1, 1, 1)
        self.save_file_dir = QtWidgets.QLabel(self.centralwidget)
        self.save_file_dir.setObjectName("save_file_dir")
        self.gridLayout.addWidget(self.save_file_dir, 3, 0, 1, 1)
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setObjectName("password_label")
        self.gridLayout.addWidget(self.password_label, 1, 0, 1, 1)
        self.save_file_dir_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_file_dir_button.setText("")
        self.save_file_dir_button.setObjectName("save_file_dir_button")
        self.gridLayout.addWidget(self.save_file_dir_button, 3, 2, 1, 1)
        self.password_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.password_line_edit.setMinimumSize(QtCore.QSize(0, 30))
        self.password_line_edit.setObjectName("password_line_edit")
        self.gridLayout.addWidget(self.password_line_edit, 1, 1, 1, 2)
        self.id_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.id_line_edit.setMinimumSize(QtCore.QSize(0, 30))
        self.id_line_edit.setObjectName("id_line_edit")
        self.gridLayout.addWidget(self.id_line_edit, 0, 1, 1, 2)
        self.batch_time_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.batch_time_line_edit.setMinimumSize(QtCore.QSize(0, 30))
        self.batch_time_line_edit.setObjectName("batch_time_line_edit")
        self.gridLayout.addWidget(self.batch_time_line_edit, 2, 1, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 2)
        self.execute_button = QtWidgets.QPushButton(self.centralwidget)
        self.execute_button.setMinimumSize(QtCore.QSize(0, 40))
        self.execute_button.setObjectName("execute_button")
        self.gridLayout_2.addWidget(self.execute_button, 1, 0, 1, 1)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout_2.addWidget(self.plainTextEdit, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.id_line_edit, self.password_line_edit)
        MainWindow.setTabOrder(self.password_line_edit, self.batch_time_line_edit)
        MainWindow.setTabOrder(self.batch_time_line_edit, self.save_file_line_edit)
        MainWindow.setTabOrder(self.save_file_line_edit, self.save_file_dir_button)
        MainWindow.setTabOrder(self.save_file_dir_button, self.execute_button)
        MainWindow.setTabOrder(self.execute_button, self.cancel_button)
        MainWindow.setTabOrder(self.cancel_button, self.plainTextEdit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.cancel_button.setText(_translate("MainWindow", "중지"))
        self.batch_time_label.setText(_translate("MainWindow", "배치시간"))
        self.id_label.setText(_translate("MainWindow", "아이디"))
        self.save_file_dir.setText(_translate("MainWindow", "저장위치"))
        self.password_label.setText(_translate("MainWindow", "비밀번호"))
        self.execute_button.setText(_translate("MainWindow", "시작"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
