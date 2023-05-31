import os

app_path = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = str("/").join(app_path.split('/')[:-1])
print(f"\n\n BASE DIR: {BASE_DIR}")
