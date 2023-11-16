import schedule
import time
import subprocess


def run_my_script():
    subprocess.run(["python", "currency_data/end_day_data.py"])
    subprocess.run(["python", "currency_data/currency_predict_analys_rate.py"])


schedule.every().day.at("23:28").do(run_my_script)

while True:
    schedule.run_pending()
    time.sleep(1)
