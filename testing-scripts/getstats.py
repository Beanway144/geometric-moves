import os
import csv

def percentageGeometricFromCensus(directory):
# Loop over all files in the directory
    f = open(f'percent-geom-from-{directory}.csv', "w")
    f.write(f'manifold, geometric, nongeometric, percentage\n')
    f.close()
    for filename in os.listdir(directory):
        if filename.endswith("nodes.csv"):
            geometric = 0
            nongeometric = 0
            file_path = os.path.join(directory, filename)
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader) #skip table heading

                for row in reader:
                    if len(row) > 1:
                        if int(row[1]) == 1:
                            geometric += 1
                        else:
                            nongeometric += 1

            f = open(f'percent-geom-from-{directory}.csv', "a")
            f.write(f'{filename[:4]}, {geometric}, {nongeometric}, {round(geometric/(nongeometric + geometric) * 100, 1)}\n')
            f.close()