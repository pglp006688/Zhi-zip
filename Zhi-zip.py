import sys
import os
import zipfile
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                               QVBoxLayout, QProgressBar, QFileDialog, QWidget, QLabel, QHBoxLayout)
from PySide6.QtCore import QThread, Signal

class ZipWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, files, output_path):
        super().__init__()
        self.files = files
        self.output_path = output_path

    def run(self):
        total = len(self.files)
        # 1. 计算公共父目录，用于保留相对路径，防止同名文件覆盖
        try:
            common_dir = os.path.commonpath([os.path.dirname(f) for f in self.files])
        except ValueError:
            common_dir = os.path.dirname(self.files[0]) # 跨盘符降级处理

        with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, file in enumerate(self.files):
                # 2. 使用相对路径作为压缩包内的路径
                arcname = os.path.relpath(file, common_dir)
                zf.write(file, arcname)
                self.progress.emit(int((i + 1) / total * 100))
        self.finished.emit("压缩完成！")

class ZhiZipWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zhi-zip")
        self.resize(450, 250)
        self.files = []
        
        layout = QVBoxLayout()
        self.lbl_status = QLabel("请选择文件或文件夹")
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("添加文件")
        self.btn_add_file.clicked.connect(self.select_files)
        self.btn_add_folder = QPushButton("添加文件夹")
        self.btn_add_folder.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.btn_add_file)
        btn_layout.addWidget(self.btn_add_folder)
        
        self.progress = QProgressBar()
        self.btn_start = QPushButton("开始压缩")
        self.btn_start.clicked.connect(self.start_zip)
        
        layout.addWidget(self.lbl_status)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress)
        layout.addWidget(self.btn_start)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_files(self):
        # 支持多选
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if files:
            self.files.extend(files) # 累加文件
            self.update_status()

    def select_folder(self):
        # 支持选择文件夹并递归读取
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    self.files.append(os.path.join(root, file))
            self.update_status()

    def update_status(self):
        self.lbl_status.setText(f"已添加 {len(self.files)} 个文件 (可继续添加)")

    def start_zip(self):
        if not self.files: 
            self.lbl_status.setText("请先添加文件或文件夹！")
            return
            
        output, _ = QFileDialog.getSaveFileName(self, "保存为", "my-zip.zip", "ZIP (*.zip)")
        if not output: return
        
        self.btn_start.setEnabled(False)
        self.progress.setValue(0)
        
        self.worker = ZipWorker(self.files, output)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.lbl_status.setText(msg)
        self.btn_start.setEnabled(True)
        self.files = [] # 清空列表

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZhiZipWindow()
    window.show()
    sys.exit(app.exec())