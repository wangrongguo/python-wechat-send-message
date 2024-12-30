import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """
    程序主入口函数
    初始化 QT 应用并启动主窗口
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 