import os
import sys

# Ensure the root directory is in python's path, so we can import from root-level modules
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from weather_app_premium import app
