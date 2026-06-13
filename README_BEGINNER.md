# 南航明珠等级测算 WebUI：启动说明

本项目是非官方、本地运行的南航明珠等级测算 WebUI。计算结果仅供规划参考，请以南航明珠及相关航司官方规则、客服解释、出票页面和最终入账为准。

## Windows 推荐方式

1. 下载并解压项目 ZIP。
2. 双击 `start.bat`。
3. 首次运行会自动创建 `.venv` 并安装依赖。
4. 启动完成后，浏览器会自动打开：

```text
http://127.0.0.1:5055/
```

如果想使用命令行模式，可以双击 `start_cli.bat`，或者在终端中运行：

```bat
python tools\cli_launcher.py
```

## macOS 推荐方式

1. 下载并解压项目 ZIP。
2. 双击 `start.command`。
3. 如果系统提示无法打开，可以右键选择“打开”，或在终端中执行：

```bash
chmod +x start.command
./start.command
```

命令行模式：

```bash
./start.sh
```

## Linux 推荐方式

```bash
chmod +x start.sh
./start.sh
```

如需 GUI：

```bash
chmod +x start_gui.sh
./start_gui.sh
```

## GUI 启动器

GUI 启动器入口：

```bash
python tools/gui_launcher.py
```

功能包括：

- 启动 WebUI
- 停止服务
- 自动打开浏览器
- 重新安装依赖
- 打开日志文件夹
- 打开项目文件夹
- 显示运行日志

GUI 启动器会优先使用 `CustomTkinter` 现代界面。如果没有安装，也会自动回退到 Python 自带的 Tkinter 界面。

安装更美观的 GUI 依赖：

```bash
python -m pip install -r requirements-gui.txt
```

## 命令行启动器

基本运行：

```bash
python tools/cli_launcher.py
```

常用参数：

```bash
python tools/cli_launcher.py --port 5055
python tools/cli_launcher.py --no-browser
python tools/cli_launcher.py --reinstall
python tools/cli_launcher.py --reset-venv
python tools/cli_launcher.py --no-port-fallback
```

参数说明：

| 参数 | 作用 |
|---|---|
| `--port 5055` | 指定优先使用的本地端口 |
| `--no-browser` | 启动后不自动打开浏览器 |
| `--reinstall` | 强制重新安装依赖 |
| `--reset-venv` | 删除并重建 `.venv` |
| `--no-port-fallback` | 端口占用时直接失败，不自动换端口 |

## 日志位置

```text
logs/launcher.log
logs/flask_server.log
```

如果启动失败，请优先查看这两个文件。

## 常见问题

### 1. 提示找不到 Python

请安装 Python 3.10+。Windows 安装时建议勾选：

```text
Add Python to PATH
```

### 2. 端口 5055 被占用

默认情况下，启动器会自动寻找下一个可用端口，例如 5056。GUI 或命令行日志中会显示实际地址。

### 3. 依赖安装失败

可以尝试：

```bash
python tools/cli_launcher.py --reset-venv
```

或者使用国内镜像源手动安装依赖。

### 4. WebUI 启动了但浏览器没有打开

手动访问日志中显示的地址，例如：

```text
http://127.0.0.1:5055/
```
