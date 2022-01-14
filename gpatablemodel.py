import json
from typing import overload
import typing
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Slot, QFile, QTextStream, QIODevice
from PySide2.QtWidgets import QFileDialog
from typing import *
import PySide2.QtCore


class GPATableModel(QAbstractTableModel):
    def __init__(self, jsonData=None, parent=None):
        super().__init__(parent)
        self.headItem = ("计算此项", "学年学期", "课程名称", "课程性质", "学分", "成绩", "绩点")
        self.displayData = []

        def getGPA(score: float) -> float:
            if score >= 96:
                return 4.8
            elif score >= 93:
                return 4.5
            elif score >= 90:
                return 4.0
            elif score >= 86:
                return 3.8
            elif score >= 83:
                return 3.5
            elif score >= 80:
                return 3.0
            elif score >= 76:
                return 2.8
            elif score >= 73:
                return 2.5
            elif score >= 70:
                return 2.0
            elif score >= 66:
                return 1.8
            elif score >= 63:
                return 1.5
            elif score >= 60:
                return 1.0
            else:
                return 0
        def getGradeScore(grade: str) -> float:
            if grade == "优":
                return 95.0
            elif grade == "良":
                return 85.0
            elif grade == "中":
                return 75.0
            elif grade == "及格":
                return 65.0
            else:
                return 0.0
        def getGradeGPA(grade: str) -> float:
            if grade == "优":
                return 4.5
            elif grade == "良":
                return 3.5
            elif grade == "中":
                return 2.5
            elif grade == "及格":
                return 1.5
            else:
                return 0.0

        for item in jsonData:
            if item['DJCJMC'] == None:
                self.displayData.append((None, item['XNXQDM_DISPLAY'], item['KCM'],
                                        item['KCXZDM_DISPLAY'], item['XF'], item['ZCJ'], getGPA(float(item['ZCJ']))))
            else:
                self.displayData.append((None, item['XNXQDM_DISPLAY'], item['KCM'],
                                        item['KCXZDM_DISPLAY'], item['XF'], getGradeScore(item['DJCJMC']), getGradeGPA(item['DJCJMC'])))
        self.checkedItem = [Qt.Unchecked for i in range(len(self.displayData))]

    def rowCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        return len(self.displayData)

    def columnCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        return 7

    def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headItem[section]

    def data(self, index: PySide2.QtCore.QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if role == Qt.DisplayRole:
            return self.displayData[index.row()][index.column()]
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                return self.checkedItem[index.row()]
            return None
        return None

    def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        if not index.isValid():
            return super().flags(index)
        flag = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            flag |= Qt.ItemIsUserCheckable
        return flag

    def setData(self, index: PySide2.QtCore.QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                if self.checkedItem[index.row()] == Qt.Checked:
                    self.checkedItem[index.row()] = Qt.Unchecked
                else:
                    self.checkedItem[index.row()] = Qt.Checked
                self.dataChanged.emit(index, index)
                return True
        return False
    
    @Slot()
    def selectAll(self):
        self.checkedItem = [Qt.Checked for i in range(len(self.displayData))]
        self.beginResetModel()
        self.endResetModel()
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    @Slot()
    def clearSelect(self):
        self.checkedItem = [Qt.Unchecked for i in range(len(self.displayData))]
        self.beginResetModel()
        self.endResetModel()
        self.dataChanged.emit(QModelIndex(), QModelIndex())
    
    @Slot()
    def selectInv(self):
        for i in range(len(self.checkedItem)):
            if self.checkedItem[i] == Qt.Unchecked:
                self.checkedItem[i] = Qt.Checked
            else:
                self.checkedItem[i] = Qt.Unchecked
        self.beginResetModel()
        self.endResetModel()
        self.dataChanged.emit(QModelIndex(), QModelIndex())
    
    @Slot()
    def selectContemp(self):
        for i in range(len(self.displayData)):
            if self.displayData[i][-4] == "必修" or self.displayData[i][-4] == "限选":
                self.checkedItem[i] = Qt.Checked
            else:
                self.checkedItem[i] = Qt.Unchecked
        self.beginResetModel()
        self.endResetModel()
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    @Slot()
    def export2CSV(self):
        savePath = QFileDialog.getSaveFileName(None, "保存为CSV", "", "CSV文件(*.csv)")[0]
        file = QFile(savePath)
        file.open(QIODevice.WriteOnly)
        out = QTextStream(file)
        out << "学年学期,课程名称,课程性质,学分,成绩,绩点\n"
        for i in range(len(self.displayData)):
            out << (",".join([str(item) for item in self.displayData[i][1:]]) + "\n")

    def getAverage(self) -> Tuple[float, float, float]:
        sumXF = 0.0
        sumGPA = 0.0
        sumScore = 0.0
        for i in range(len(self.displayData)):
            if self.checkedItem[i] == Qt.Checked:
                sumXF += float(self.displayData[i][-3])
                sumScore += float(self.displayData[i][-2]) * float(self.displayData[i][-3])
                sumGPA += float(self.displayData[i][-1]) * float(self.displayData[i][-3])
        if sumXF == 0.0:
            return (0.0, 0.0, 0.0)
        else:
            return (sumXF, sumGPA / sumXF, sumScore / sumXF)