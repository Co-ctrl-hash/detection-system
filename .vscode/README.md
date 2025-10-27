# VS Code Configuration

This folder contains VS Code workspace settings that configure:

## settings.json
- **Python interpreter**: Points to `venv/Scripts/python.exe`
- **Extra paths**: Adds `external/yolov7` to Python path for imports
- **Language server**: Uses Pylance for better IntelliSense
- **Auto-activation**: Automatically activates virtual environment in terminal

## extensions.json
Recommended extensions for this project:
- **Python** - Python language support
- **Pylance** - Fast, feature-rich Python language server
- **Jupyter** - Notebook support
- **ESLint** - JavaScript linting
- **Prettier** - Code formatting
- **TypeScript** - TypeScript support

## How This Fixes Import Errors

The import errors you see (cv2, torch, flask_sqlalchemy) are resolved by:

1. **Virtual environment**: All packages installed in `venv/`
2. **Python path**: VS Code configured to use `venv/Scripts/python.exe`
3. **Extra paths**: YOLOv7 modules added to Python path
4. **Pylance**: Better import resolution and type checking

## Manual Configuration

If errors persist, manually select Python interpreter:
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose `.\venv\Scripts\python.exe`
4. Reload VS Code window

All import errors should disappear once VS Code loads these settings!
