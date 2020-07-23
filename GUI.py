from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)


class ResearchHelperGUI(QDialog):
    def __init__(self, parent=None):
        super(ResearchHelperGUI, self).__init__(parent)
        self.orinalPalette = QApplication.palette()
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())
        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.journal_choose()  # 左侧创建期刊输入框
        # self.createBottomRightGroupBox()  # 右侧创建笔记栏
        # self.result_table()  # 下方为爬虫结果

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.journal_box_title, 1, 0)
        # mainLayout.addWidget(self.bottomRightGroupBox, 1, 0)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("环境科研小助手")
        self.window().setFixedSize(1000, 500)
        # self.changeStyle('Fusion')

    def volume_acquire(self):
        QMessageBox.information(self, 'I Love U', '你是我的宝贝！')

    def journal_choose(self):
        self.journal_box_title = QGroupBox("请选择或输入您想爬取的期刊：")

        journal_box = QComboBox()
        journal_list = ['Water Research', 'Chemical Engineering Journal', 'Journal of Cleaner Production']
        journal_box.addItems(journal_list)

        volume_box = QComboBox()
        volume_list = ['1', '2']  # 通过爬虫获取volume数目
        volume_box.addItems(volume_list)

        volume_label = QLabel("期数：")

        # 网址输入框
        line_check_box = QGroupBox("输入网址：如'www.sciencedirect.com/journal/water-research/'")
        line_check_box.setCheckable(True)
        line_check_box.setChecked(False)
        line_edit = QLineEdit(line_check_box)

        # if not line_check_box.isChecked():
        #     line_edit.setDisabled(True)

        line_check_box.toggled.connect(journal_box.setDisabled)

        # 获取期数
        bt_volume = QPushButton('爬取期数', self)
        bt_volume.clicked.connect(self.volume_acquire)
        bt_volume.setFixedSize(80, 30)
        bt_volume.resize(100, 30)
        bt_volume.move(1000, 1000)

        # 布局设置
        layout = QGridLayout()
        layout.addWidget(journal_box, 1, 0, 1, 2)
        layout.addWidget(line_check_box, 2, 0, 1, 2)
        layout.addWidget(line_edit, 3, 0, 1, 2)
        layout.addWidget(bt_volume, 4, 0, 1, 2)
        layout.addWidget(volume_label, 5, 0, 1, 2)
        layout.addWidget(volume_box, 6, 0, 1, 2)
        self.journal_box_title.setLayout(layout)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    ui = ResearchHelperGUI()
    ui.show()
    sys.exit(app.exec_())

