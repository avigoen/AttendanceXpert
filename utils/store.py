import csv
from datetime import datetime


def record_attendace(output):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    file_path = f"static/attendance/{current_date}.csv"
    f = open(file_path, "w+", newline="")
    count = sum(1 for _ in f)

    lnwriter = csv.writer(f)
    if count < 1:
        lnwriter.writerow(["DateTime", "UniqueID"])

    for entry in output:
        lnwriter.writerow([date_time, entry["label"]])

    f.close()
