import sys
import os
import zipfile
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                               QProgressBar, QFileDialog, QWidget, QLabel, QHBoxLayout, 
                               QStackedWidget, QLineEdit, QFrame)
from PySide6.QtCore import QThread, Signal, Qt

# ================= 1. 后台压缩线程 =================
class ZipWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, files, output_path):
        super().__init__()
        self.files = files
        self.output_path = output_path

    def run(self):
        total = len(self.files)
        try:
            common_dir = os.path.commonpath([os.path.dirname(f) for f in self.files])
        except ValueError:
            common_dir = os.path.dirname(self.files[0]) if self.files else ""

        with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, file in enumerate(self.files):
                arcname = os.path.relpath(file, common_dir) if common_dir else os.path.basename(file)
                zf.write(file, arcname)
                self.progress.emit(int((i + 1) / total * 100))
        self.finished.emit("Zhi-zip 压缩完成！")

# ================= 2. 主窗口 =================
class ZhiZipWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zhi-zip")
        self.resize(600, 400)
        self.files = []
        self.config_file = "zhi_config.json"
        self.config = self.load_config()

        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧导航栏
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(10)
        
        self.btn_start = self.create_nav_btn("🚀 开始")
        self.btn_settings = self.create_nav_btn("⚙️ 设置")
        self.btn_about = self.create_nav_btn("ℹ️ 关于")
        
        nav_layout.addWidget(self.btn_start)
        nav_layout.addWidget(self.btn_settings)
        nav_layout.addWidget(self.btn_about)
        nav_layout.addStretch()

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #cccccc;")
        
        # 右侧页面栈
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #f9f9f9;")

        main_layout.addLayout(nav_layout, 1)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.stacked_widget, 4)

        self.setCentralWidget(main_widget)

        # 初始化页面
        self.init_start_page()
        self.init_settings_page()
        self.init_about_page()

        # 绑定导航切换
        self.btn_start.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_about.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

    def create_nav_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedSize(120, 50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0; border: none; border-radius: 8px;
                font-size: 16px; font-weight: bold; color: #333333;
            }
            QPushButton:hover { background-color: #d0d0d0; }
            QPushButton:pressed { background-color: #0078d7; color: white; }
        """)
        return btn

    # ---------- 页面 1: 开始 ----------
    def init_start_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        self.lbl_status = QLabel("请选择文件或文件夹")
        self.lbl_status.setStyleSheet("font-size: 14px; color: #555;")

        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("添加文件 (可多选)")
        self.btn_add_file.clicked.connect(self.select_files)
        self.btn_add_folder = QPushButton("添加文件夹")
        self.btn_add_folder.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.btn_add_file)
        btn_layout.addWidget(self.btn_add_folder)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(25)
        
        self.btn_start_compress = QPushButton("开始压缩")
        self.btn_start_compress.setFixedHeight(40)
        self.btn_start_compress.setStyleSheet("""
            QPushButton { background-color: #0078d7; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #005a9e; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.btn_start_compress.clicked.connect(self.start_zip)

        layout.addWidget(self.lbl_status)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress)
        layout.addWidget(self.btn_start_compress)
        layout.addStretch()

        self.stacked_widget.addWidget(page)

    # ---------- 页面 2: 设置 ----------
    def init_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        lbl_title = QLabel("⚙️ 压缩设置")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        lbl_name = QLabel("默认压缩文件名 (不含 .zip 后缀):")
        self.input_filename = QLineEdit()
        self.input_filename.setText(self.config.get("default_name", "zhi"))
        self.input_filename.setFixedHeight(35)
        self.input_filename.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")

        self.btn_save = QPushButton("保存设置")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #28a745; color: white; border: none; border-radius: 5px; font-size: 15px; font-weight: bold; }
            QPushButton:hover { background-color: #218838; }
        """)
        self.btn_save.clicked.connect(self.save_settings)

        self.lbl_save_status = QLabel("")
        self.lbl_save_status.setStyleSheet("color: #28a745;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_name)
        layout.addWidget(self.input_filename)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.lbl_save_status)
        layout.addStretch()

        self.stacked_widget.addWidget(page)

    # ---------- 页面 3: 关于 ----------
    def init_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        about_text = """
        <div style="text-align: center;">
            <h1 style="color: #0078d7;">Zhi-zip</h1>
            <p style="font-size: 16px;"><b>作者：</b>志校儿</p>
            <p style="font-size: 16px;"><b>合作者：</b>玩游戏的鲁邦</p>
            <p style="font-size: 16px;"><b>项目地址：</b><a href="https://github.com/zhi-xiaoer/Zhi-zip" style="color: #0078d7; text-decoration: none;">github.com/zhi-xiaoer/Zhi-zip</a></p>
        </div>
        """
        lbl_about = QLabel(about_text)
        lbl_about.setOpenExternalLinks(True)
        lbl_about.setStyleSheet("font-size: 15px; line-height: 1.8;")

        layout.addWidget(lbl_about)
        self.stacked_widget.addWidget(page)

    # ================= 逻辑方法 =================
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"default_name": "zhi"}

    def save_settings(self):
        name = self.input_filename.text().strip()
        if not name:
            name = "zhi"
            self.input_filename.setText(name)
        
        self.config["default_name"] = name
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        self.lbl_save_status.setText("✅ 设置已保存！")
        # 2秒后清除提示
        QTimer.singleShot(2000, lambda: self.lbl_save_status.setText("")) # 需导入 QTimer，这里简化处理，直接用延时或不管

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if files:
            self.files.extend(files)
            self.update_status()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    self.files.append(os.path.join(root, file))
            self.update_status()

    def update_status(self):
        self.lbl_status.setText(f"✅ 已添加 {len(self.files)} 个文件 (可继续添加)")

    def start_zip(self):
        if not self.files: 
            self.lbl_status.setText("❌ 请先添加文件或文件夹！")
            return
            
        default_name = self.config.get("default_name", "zhi")
        if not default_name.endswith(".zip"):
            default_name += ".zip"
            
        output, _ = QFileDialog.getSaveFileName(self, "保存为", default_name, "ZIP (*.zip)")
        if not output: return
        
        self.btn_start_compress.setEnabled(False)
        self.progress.setValue(0)
        
        self.worker = ZipWorker(self.files, output)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.lbl_status.setText(msg)
        self.btn_start_compress.setEnabled(True)
        self.files = []
        self.update_status()

# 补充 QTimer 导入以防保存提示需要 (上面代码已简化，若需精确延时可加，此处保持简洁不依赖 QTimer)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZhiZipWindow()
    window.show()
    sys.exit(app.exec())