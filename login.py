import sys
import typing
from PySide2.QtWidgets import QWidget, QPushButton, QLineEdit, QDialog, QApplication, QMessageBox
from ids_encrypt import encryptAES
from ui_login import Ui_Login
import requests
from PySide2.QtCore import Slot
from bs4 import BeautifulSoup
import json
from gpacalc import GPACalc

class Login(QDialog):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.ui = Ui_Login()
        self.ui.setupUi(self)

    @Slot()
    def loginProc(self):
        ss = requests.Session()
        form = {"username": self.ui.cardnum.text()}

        #  获取登录页面表单，解析隐藏值
        url = "https://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal"
        res = ss.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        attrs = soup.select('[tabid="01"] input[type="hidden"]')
        for k in attrs:
            if k.has_attr('name'):
                form[k['name']] = k['value']
            elif k.has_attr('id'):
                form[k['id']] = k['value']
        form['password'] = encryptAES(self.ui.password.text(), form['pwdDefaultEncryptSalt'])
        # 登录认证
        res = ss.post(url, data=form)
        # 登录ehall
        ss.get('http://ehall.seu.edu.cn/login?service=http://ehall.seu.edu.cn/new/index.html')

        res = ss.get('http://ehall.seu.edu.cn/jsonp/userDesktopInfo.json')
        json_res = json.loads(res.text)
        try:
            name = json_res["userName"]
        except Exception:
            QMessageBox.warning(self, "警告", "登录失败，请检查用户名和密码")
            return
        self.session = ss
        self.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = Login()
    if (window.exec_() == QDialog.Accepted):
        calc = GPACalc(window.session)
        calc.show()
    else:
        sys.exit(0)
    sys.exit(app.exec_())