
import csv
__all__ = ["readCSV" ]

def readCSV(fname, deli=",", encoding="utf8"):
    with open(fname, newline='', encoding=encoding) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=deli, quotechar='\\')
        return list(spamreader)

