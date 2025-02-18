#python script to convert tab separated file to csv file
import csv

tsv_file = "uni.tsv"
csv_file = "uni.csv"

with open(tsv_file, "r", newline="", encoding="utf-8") as infile, \
     open(csv_file, "w", newline="", encoding="utf-8") as outfile:

    tsv_reader = csv.reader(infile, delimiter="\t")  # Read TSV with tab delimiter
    csv_writer = csv.writer(outfile, delimiter=",")  # Write CSV with comma delimiter

    for row in tsv_reader:
        csv_writer.writerow(row)

print(f"Converted '{tsv_file}' to '{csv_file}' successfully.")
