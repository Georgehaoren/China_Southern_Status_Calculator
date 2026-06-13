# Packaging Strategy / 发布包策略

## 推荐发布层级

### 1. 源码包

适合开发者或懂 Python 的用户。

内容：

```text
源代码 + requirements.txt + tools/cli_launcher.py + tools/gui_launcher.py
```

运行方式：

```bash
python tools/cli_launcher.py
```

### 2. 小白 ZIP 包

适合普通用户。

内容：

```text
完整项目源码
start.bat
start.command
start.sh
README_BEGINNER.md
```

用户体验：

```text
解压 ZIP → 双击 start.bat / start.command → 浏览器自动打开
```

这种方式仍然要求用户电脑已经安装 Python。

### 3. PyInstaller 桌面包

适合完全不懂 Python 的用户。

建议优先使用 one-folder 模式，而不是 one-file 模式。原因是本项目包含：

- `templates/`
- `static/`
- `data/`
- 多个 JSON/CSV 规则库
- Flask WebUI 静态资源

one-folder 模式更容易排查路径问题，也更适合本地 WebUI。

示例命令，需按平台分别打包：

```bash
python -m pip install pyinstaller customtkinter
pyinstaller --onedir --name CZStatusCalculatorLauncher tools/gui_launcher.py
```

实际打包时还需要把 `app.py`、`api/`、`services/`、`web/`、`templates/`、`static/`、`data/` 等目录加入打包资源。建议后续单独写 `.spec` 文件管理。

## 不建议直接把便携 Python 放进 GitHub repo

原因：

1. repo 体积会迅速膨胀；
2. 不同平台需要不同 Python 包；
3. 后续 Python 安全更新和依赖更新难维护；
4. GitHub 源码仓库会变得不清晰。

更合适的方式：

```text
GitHub repo：源码、启动器、文档
GitHub Release / 网盘：Windows 小白包、macOS 小白包、可选便携 Python 包
```

## 建议发布命名

```text
CZ-Status-Calculator-v27-source.zip
CZ-Status-Calculator-v27-windows-beginner.zip
CZ-Status-Calculator-v27-macos-beginner.zip
CZ-Status-Calculator-v28-windows-gui.zip
CZ-Status-Calculator-v28-macos-gui.zip
```
