import csv
from datetime import datetime

def record_attendace(output):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    f = open(f"static/attendance/{current_date}.csv", "w+", newline="")
    lnwriter = csv.writer(f)
    for entry in output:
        lnwriter.writerow([date_time, entry['label']])

    f.close()