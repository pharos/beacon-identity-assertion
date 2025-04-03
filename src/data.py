
import csv, json, os

def load_csv_data(file_path):
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]
    return rows

assertion_data = load_csv_data(os.getenv("CSV_DATA_FILE", "data.csv"))