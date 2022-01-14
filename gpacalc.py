from PySide2.QtWidgets import QWidget
from ui_gpacalc import *
from gpatablemodel import GPATableModel
import sys
import json
class GPACalc(QWidget):
    def __init__(self, session, parent = None):
        super().__init__(parent)
        self.ui = Ui_GPACalc()
        self.ui.setupUi(self)
        self.session = session
    
    @Slot()
    def gpaLoader(self):
        self.session.get("http://ehall.seu.edu.cn/appShow?appId=4768574631264620")
        url = 'http://ehall.seu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do'

        params = {"querySetting": [{"name": "SHOWMAXCJ", "caption": "显示最高成绩", "linkOpt": "AND",
                                    "builderList": "cbl_String", "builder": "equal", "value": 0, "value_display": "否"}],
                "*order": "-XNXQDM,-KCH,-KXH",
                "pageSize": 100,
                "pageNumber": 1}
        res = self.session.post(url, data=params)
        data = json.loads(res.text)['datas']['xscjcx']['rows']
        model = GPATableModel(data, None)
        model.dataChanged.connect(self.updateAverage)
        self.ui.selectAll.clicked.connect(model.selectAll)
        self.ui.clear.clicked.connect(model.clearSelect)
        self.ui.selectInv.clicked.connect(model.selectInv)
        self.ui.selectContemp.clicked.connect(model.selectContemp)
        self.ui.export2CSV.clicked.connect(model.export2CSV)
        self.ui.gpaViewer.setModel(model)
    
    @Slot()
    def updateAverage(self):
        if self.ui.gpaViewer.model() == None:
            return
        result = self.ui.gpaViewer.model().getAverage()
        self.ui.totalXF.setText("%.2f" % result[0])
        self.ui.averageGPA.setText("%.4f" % result[1])
        self.ui.averageScore.setText("%.4f" % result[2])


if __name__ == "__main__":
    app = QApplication([])
    window = GPACalc(None)
    window.show()
    sys.exit(app.exec_())