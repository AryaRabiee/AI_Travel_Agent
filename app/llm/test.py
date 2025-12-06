import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
DATA_PATH = os.path.join(BASE_DIR, "embeding_test.json")
print("start")
db_test = json.load(open(DATA_PATH, "r", encoding="utf-8"))
if isinstance(db_test, list):
        db_test = {item["city"]: item for item in db_test}
print("finish")
print(db_test['tehran']['text'])