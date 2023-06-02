import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from qt_material import apply_stylesheet
from PyQt6.QtWidgets import  QWidget, QLabel, QMenu, QApplication, QSystemTrayIcon, QWidget
from PyQt6.QtCore import Qt, QRect, QPoint,QThread
from PyQt6.QtGui import QPixmap, QScreen, QPainter, QPen, QGuiApplication, QColor,QIcon,QAction
import requests
import json
import base64
import urllib
import pyperclip
import time
import openai
import keyboard




class WorkerThread(QThread):
    resultReady = QtCore.pyqtSignal(str)  # 定义一个信号，用于发送任务结果

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        # 在这里执行你的耗时任务
        result = "Your result"
        self.resultReady.emit(result)  # 任务完成后，发送结果



class pyOCR:
    def ocrmain():
        API_KEY =  baidu_api_key
        SECRET_KEY = baidu_secret_key
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}


        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + str(requests.post(url, params=params).json().get("access_token"))
    
        
        with open('screenshot.png', "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            content = urllib.parse.quote_plus(content)
            


        payload='image='+content+'&language_type=ENG&paragraph=true'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
    
        response = requests.request("POST", url, headers=headers, data=payload)

        data=json.loads(response.text)

        # 创建一个空的列表来存储段落
        paragraphs = []

        # 遍历data中的每个段落
        for paragraph in data['paragraphs_result']:
            # 创建一个空的字符串来存储当前段落的文本
            paragraph_text = ''
            # 遍历当前段落中的每个句子片段的索引
            for word_idx in paragraph['words_result_idx']:
                # 将对应的句子片段添加到段落文本中
                paragraph_text += data['words_result'][word_idx]['words'] + ' '
            # 将完整的段落文本添加到段落列表中
            paragraphs.append(paragraph_text.strip())

        # 最后，你可以将所有段落合并成一个字符串，段落之间用空行分隔
        text = ' '.join(paragraphs)

        return text

class CaptureLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.drawRect(QRect(self.begin, self.end))

class CaptureScreen(QWidget):
    finished = QtCore.pyqtSignal()  # 定义一个新的信号

    def __init__(self, pixmap,show_ui_ocr):
        super().__init__()

        self.show_ui = show_ui_ocr  # 保存 show_ui 为一个成员变量

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.begin = QPoint()
        self.end = QPoint()

        self.lbl = CaptureLabel(self)
        self.lbl.setPixmap(pixmap)
        self.lbl.show()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.lbl.begin = self.begin
        self.lbl.end = self.end
        self.lbl.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.lbl.end = self.end
        self.lbl.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        screenshot: QPixmap = self.lbl.pixmap().copy(QRect(self.begin, self.end))
        screenshot.save("screenshot.png", "png")
        self.show_ui.setText(pyOCR.ocrmain())
        self.finished.emit()
        self.close()

class OCRSlovt(QtCore.QObject):


    def __init__(self, show_Form,show_ui):
        super().__init__()
        self.show_Form=show_Form
        self.show_ui_ocr=show_ui

    def do_something(self):
        screen: QScreen = QGuiApplication.primaryScreen()
        screenshot: QPixmap = screen.grabWindow(0)
        self.capture_screen = CaptureScreen(screenshot,self.show_ui_ocr)
        self.capture_screen.finished.connect(self.show_Form.show)
        self.capture_screen.show()
        
class Read:
    def tag_verbs_or_adverbs(text):

        # 发送POST请求
        url = nlpurl  # 更改为你的API地址
        data = {
            'text':text,
        }
        headers = {'Content-Type': 'application/json'}  # 如果需要的话

        response = requests.post(url, data=json.dumps(data), headers=headers)

        # 检查状态码是否为200（即请求成功）
        if response.status_code == 200:
            # 解析JSON数据
            json_data = response.json()

            return json_data['result'].strip()  # 更改为你的键名
        else:
            return '请求失败，状态码：'+ response.status_code

class ReadSlovt(QtCore.QObject):
    def __init__(self, show_Form,show_ui_ocr,show_ui_read):
        super().__init__()
        self.show_Form=show_Form
        self.show_ui_ocr=show_ui_ocr
        self.show_ui_read=show_ui_read

    def do_something(self):
        if self.show_ui_ocr.toPlainText()!="":
            text=self.show_ui_ocr.toPlainText()
        else:
            keyboard.send('ctrl+c')  # Replace this line
            time.sleep(0.7)
            text = pyperclip.paste()
        
        if not text:
            self.show_ui_read.setText("无法从剪贴板或OCR窗口获取获取数据")
            self.show_Form.show()
        else:
            self.show_ui_read.setText(Read.tag_verbs_or_adverbs(text))
            self.show_Form.show()
       
class TransSlovt(QtCore.QObject):
    def __init__(self, show_Form,show_ui_ocr,show_ui_trans):
        super().__init__()
        self.show_Form=show_Form
        self.show_ui_ocr=show_ui_ocr
        self.show_ui_trans=show_ui_trans

    def do_something(self):
        # 获取用户的输入
        # 默认先检测ocr识别的文本，ocr文本框为空的时候，在读取框选的文字。
        if self.show_ui_ocr.toPlainText()!="":
            user_input=self.show_ui_ocr.toPlainText()
        else:
            keyboard.send('ctrl+c')  # Replace this line
            time.sleep(0.7)
            user_input = pyperclip.paste()
       

        if not user_input:
            self.show_ui_trans.setText("无法从剪贴板或OCR窗口获取获取数据")
            self.show_Form.show()
        else:
            openai.api_key = openaikey
            openai.api_base = openaiurl
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Translate the following English text to Chinese: \n {user_input}"}])
            self.show_ui_trans.setText(response['choices'][0]['message']['content'])
            self.show_Form.show()
            
class HotkeySignal(QtCore.QObject):
    hotkey_triggered = QtCore.pyqtSignal(str)

    def trigger_hotkey(self, action):
        self.hotkey_triggered.emit(action)
        
class Ui_MainForm(object):

    def switchFramelessMode(self, checked):
        if checked:
            self.Form.setWindowFlags(self.Form.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)
        else:
            self.Form.setWindowFlags(self.Form.windowFlags() & ~QtCore.Qt.WindowType.FramelessWindowHint)
        self.Form.show()

    def toggleVisibility(self):
        # 切换主窗口的显示和隐藏
        if self.Form.isVisible():
            self.Form.hide()
        else:
            self.Form.show()

        # 切换ShowForm窗口的显示和隐藏
        #if self.ShowForm.isVisible():
        #    self.ShowForm.hide()
        #else:
        #    self.ShowForm.show()

    def setupUi(self, Form):
        self.Form = Form
        Form.setObjectName("Mtools")
        Form.resize(200, 40)
        Form.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setBold(False)
        Form.setFont(font)
        Form.setMouseTracking(False)
        #Form.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 200, 40))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.checkBox = QtWidgets.QCheckBox(parent=self.horizontalLayoutWidget)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)



        #托盘
        self.tray_icon = QSystemTrayIcon(self.Form)
        self.tray_icon.setIcon(QIcon('favicon.ico'))

        exit_action = QAction("Exit",self.Form)
        exit_action.triggered.connect(QApplication.instance().quit)

        tray_menu = QMenu()
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        #self.Form.setWindowFlags(QtCore.Qt.WindowType.Tool)


        self.checkBox.toggled.connect(self.switchFramelessMode)

        self.retranslateUi(Form)
        

        self.ShowForm = QtWidgets.QWidget()  # 创建一个 QWidget 实例
        self.show_ui = Ui_ShowForm(self.ShowForm)  # 将 ShowForm 窗口的实例传入 Ui_ShowForm

        self.ocr_slovt = OCRSlovt(self.ShowForm,self.show_ui.textEdit)
        self.read_slovt = ReadSlovt(self.ShowForm,self.show_ui.textEdit,self.show_ui.textEdit_2)
        self.trans_slovt = TransSlovt(self.ShowForm,self.show_ui.textEdit,self.show_ui.textEdit_3)

        # 创建HotkeySignal实例，分别对应ocr_slovt、read_slovt和trans_slovt的do_something方法
        self.ocr_hotkey_signal = HotkeySignal()
        self.read_hotkey_signal = HotkeySignal()
        self.trans_hotkey_signal = HotkeySignal()

        # 当全局快捷键被触发时，发出hotkey_triggered信号，并传入对应的动作
        keyboard.add_hotkey(k_ocr, self.ocr_hotkey_signal.trigger_hotkey, args=['ocr'])
        keyboard.add_hotkey(k_read, self.read_hotkey_signal.trigger_hotkey, args=['read'])
        keyboard.add_hotkey(k_trans, self.trans_hotkey_signal.trigger_hotkey, args=['trans'])
        keyboard.add_hotkey(k_show, self.toggleVisibility)

         # 当hotkey_triggered信号被触发时，调用对应的方法
        self.ocr_hotkey_signal.hotkey_triggered.connect(self.trigger_action)
        self.read_hotkey_signal.hotkey_triggered.connect(self.trigger_action)
        self.trans_hotkey_signal.hotkey_triggered.connect(self.trigger_action)


        self.pushButton_3.clicked.connect(self.ocr_slovt.do_something)
        #self.pushButton_3.clicked.connect(self.ShowForm.show)
        self.pushButton_3.clicked.connect(self.show_ui.textEdit_3.hide)
        self.pushButton_3.clicked.connect(self.show_ui.textEdit_2.hide)
        self.pushButton_3.clicked.connect(self.show_ui.textEdit.show)

        self.pushButton_2.clicked.connect(self.read_slovt.do_something)
        #self.pushButton_2.clicked.connect(self.ShowForm.show)
        self.pushButton_2.clicked.connect(self.show_ui.textEdit_3.hide)
        self.pushButton_2.clicked.connect(self.show_ui.textEdit_2.show)
        self.pushButton_2.clicked.connect(self.show_ui.textEdit.hide)

        self.pushButton.clicked.connect(self.trans_slovt.do_something)
        self.pushButton.clicked.connect(self.ShowForm.show)
        self.pushButton.clicked.connect(self.show_ui.textEdit_3.show)
        self.pushButton.clicked.connect(self.show_ui.textEdit_2.hide)
        self.pushButton.clicked.connect(self.show_ui.textEdit.hide)

        #self.checkBox.toggled['bool'].connect(Form.SwitchSlovt) # type: ignore
        
        QtCore.QMetaObject.connectSlotsByName(Form)

    def trigger_action(self, action):
        if action == 'ocr':
            self.ocr_slovt.do_something()
            self.show_ui.textEdit.show()
            self.show_ui.textEdit_2.hide()
            self.show_ui.textEdit_3.hide()
        elif action == 'read':
            self.read_slovt.do_something()
            self.show_ui.textEdit.hide()
            self.show_ui.textEdit_2.show()
            self.show_ui.textEdit_3.hide()
        elif action == 'trans':
            self.trans_slovt.do_something()
            self.show_ui.textEdit.hide()
            self.show_ui.textEdit_2.hide()
            self.show_ui.textEdit_3.show()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_3.setText(_translate("Form", "O"))
        self.pushButton_2.setText(_translate("Form", "R"))
        self.pushButton.setText(_translate("Form", "T"))
        self.checkBox.setText(_translate("Form", "K"))





class Ui_ShowForm(object):

    def __init__(self, Form):
        self.Form = Form  # 保存 ShowForm 窗口的实例
        self.setupUi()

    def setupUi(self):
        Form=self.Form
        Form.setObjectName("显示窗口")
        Form.resize(851, 428)
        #Form.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_5.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_2.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_5.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_4.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_5.addWidget(self.pushButton_4)
        self.pushButton_5 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_5.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_5.addWidget(self.pushButton_5)
        self.pushButton_6 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_6.setMaximumSize(QtCore.QSize(30, 30))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.clicked.connect(self.on_pushButton_6_clicked)
        self.horizontalLayout_5.addWidget(self.pushButton_6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.textEdit = QtWidgets.QTextEdit(parent=Form)
        self.textEdit.setEnabled(True)
        self.textEdit.setOverwriteMode(False)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_4.addWidget(self.textEdit)
        self.textEdit_2 = QtWidgets.QTextEdit(parent=Form)
        self.textEdit_2.setObjectName("textEdit_2")
        self.verticalLayout_4.addWidget(self.textEdit_2)
        self.textEdit_3 = QtWidgets.QTextEdit(parent=Form)
        self.textEdit_3.setObjectName("textEdit_3")
        self.verticalLayout_4.addWidget(self.textEdit_3)
        self.gridLayout_2.addLayout(self.verticalLayout_4, 0, 0, 1, 1)

        self.Form.setWindowFlags(QtCore.Qt.WindowType.Tool)


        self.retranslateUi(Form)
        self.pushButton_5.clicked.connect(self.textEdit.clear) # type: ignore
        self.pushButton_5.clicked.connect(self.textEdit_2.clear) # type: ignore
        self.pushButton_5.clicked.connect(self.textEdit_3.clear) # type: ignore
        self.pushButton_4.clicked.connect(self.textEdit.show) # type: ignore
        self.pushButton_4.clicked.connect(self.textEdit_2.show) # type: ignore
        self.pushButton_4.clicked.connect(self.textEdit_3.show) # type: ignore
        self.pushButton_2.clicked.connect(self.textEdit.hide) # type: ignore
        self.pushButton_2.clicked.connect(self.textEdit_2.show) # type: ignore
        self.pushButton_2.clicked.connect(self.textEdit_3.hide) # type: ignore
        self.pushButton.clicked.connect(self.textEdit.show) # type: ignore
        self.pushButton.clicked.connect(self.textEdit_2.hide) # type: ignore
        self.pushButton.clicked.connect(self.textEdit_3.hide) # type: ignore
        self.pushButton_3.clicked.connect(self.textEdit.hide) # type: ignore
        self.pushButton_3.clicked.connect(self.textEdit_2.hide) # type: ignore
        self.pushButton_3.clicked.connect(self.textEdit_3.show) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "o"))
        self.pushButton_2.setText(_translate("Form", "r"))
        self.pushButton_3.setText(_translate("Form", "t"))
        self.pushButton_4.setText(_translate("Form", "a"))
        self.pushButton_5.setText(_translate("Form", "c"))
        self.pushButton_6.setText(_translate("Form", "z"))

    def on_pushButton_6_clicked(self):
        if self.Form.windowFlags() & QtCore.Qt.WindowType.WindowStaysOnTopHint:
            # 移除 WindowStaysOnTopHint 和 FramelessWindowHint 标志
            self.Form.setWindowFlags(self.Form.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint & ~QtCore.Qt.WindowType.FramelessWindowHint)
        else:
            # 添加 WindowStaysOnTopHint 和 FramelessWindowHint 标志
            self.Form.setWindowFlags(self.Form.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.Form.show()


def main():
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QIcon('favicon.ico'))

        Form = QtWidgets.QWidget()
        apply_stylesheet(app, theme='dark_teal.xml')
        ui = Ui_MainForm()
        ui.setupUi(Form)
        Form.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    
    # 从配置文件中读取URL和数据
    with open('config.json', 'r') as f:
        config = json.load(f)

    openaikey=config['openai_key']
    openaiurl=config['openai_url']
    nlpurl=config['nlpurl']
    baidu_api_key=config['baidu_api_key']
    baidu_secret_key=config['baidu_secret_key']
    k_ocr=config['k_ocr']
    k_read=config['k_read']
    k_trans=config['k_trans']
    k_show=config['k_show']
    main()
