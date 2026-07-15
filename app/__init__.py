# Package initialization for app
import os
import importlib.util

# Dynamically load the root app.py file if it exists, exporting its app instance.
# This prevents namespace conflicts with the folder directory named app/ when running uvicorn.
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_app_py_path = os.path.join(_root_dir, "app.py")

if os.path.exists(_app_py_path):
    spec = importlib.util.spec_from_file_location("root_app", _app_py_path)
    if spec and spec.loader:
        _root_app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_root_app_module)
        app = _root_app_module.app
else:
    # Fallback to main if app.py is not present
    from app.main import app

