# Zhi-zip


一款基于 Python 和 PySide6 开发的轻量级 GUI 压缩工具。

## ✨ 功能特性
- **多格式支持**：支持单文件多选、文件夹递归压缩。
- **防覆盖机制**：自动保留文件相对目录结构，避免同名文件冲突。
- **异步处理**：后台线程压缩，界面流畅不卡顿，实时显示进度。
- **累加操作**：支持分批次添加文件或文件夹到压缩列表。

## 🛠️ 环境依赖
- Python 3.8+
- PySide6

## 🚀 快速使用
一 ：直接运行`.py`

**安装依赖**
```bash
pip install PySide6
```
**运行**
```bash
python Zhi-zip.py
```

二 ：打包为`.exe`文件
```bash
# 安装打包工具
pip install pyinstaller

# 打包为单文件且隐藏控制台
pyinstaller --noconsole --onefile Zhi_zip.py
```
- 你也可直接到**Releases**下载`版本号-exe`
## 📖 使用指南
1.点击 “添加文件”（支持按住 Ctrl/Shift 多选）或 “添加文件夹”。

2.确认状态栏显示已添加的文件数量。

3.点击 “开始压缩”，选择保存路径及文件名（默认 .zip）。

4.等待进度条完成即可。

## 改进
原版 `Zhi-zip` 有一些缺点

1 . `on_finished` 里状态提示立刻被覆盖

> 用户根本看不到完成提示（影响美感）

2 . `ZipWorker.run `完全没有异常处理

> 文件被占用时，异常会直接在线程里吞掉，UI 永远卡在"压缩中"。而且` total == 0 `会 `ZeroDivisionError`。所以我重写了 Worker

3 . 没有解压功能

> 我改了改，设定`zipfile.ZipFile` 在打开时会自动定位 EOCD → 读中央目录 → 建好所有 `ZipInfo` 对象。`zf.namelist()` 能立刻拿到全部文件名。

## 💻 许可证
**MIT**
