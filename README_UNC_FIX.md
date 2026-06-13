# Windows / Parallels Desktop UNC Path Fix

## Problem

When the repository is stored in a macOS shared folder such as:

```text
\\Mac\Home\Desktop\China_Southern_Status_Calculator
```

Windows `cmd.exe` cannot use that UNC path as the current working directory. It falls back to `C:\Windows`, so a relative path like:

```text
tools\gui_launcher.py
```

is incorrectly resolved as:

```text
C:\Windows\tools\gui_launcher.py
```

That is why the Python launcher never starts and `logs\launcher.log` may not be created.

## Fix

The updated `start.bat` and `start_cli.bat` use `pushd "%~dp0"`, which maps the UNC path to a temporary drive letter before launching Python.

## Recommended usage

Replace the existing files in the repository root:

```text
start.bat
start_cli.bat
```

Then double-click `start.bat` again.

## If venv / pip fails inside the shared folder

Parallels shared folders sometimes behave differently from a normal Windows local path. If virtual environment creation or dependency installation fails, copy the whole project to a local Windows path such as:

```text
C:\Users\yourname\Desktop\China_Southern_Status_Calculator
```

Then run `start.bat` there.
