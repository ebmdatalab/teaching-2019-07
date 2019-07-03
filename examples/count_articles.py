import argparse
import csv


parser = argparse.ArgumentParser(description='Count the number of articles published each month')
parser.add_argument('input_path', help='Path to CSV file containing metadata about articles')
parser.add_argument('--output-path', help='Write counts to OUTPUT_PATH')
parser.add_argument('--start-date', help='Only count articles published after START_DATE')
parser.add_argument('--tag', help='Only count articles matching TAG')

args = parser.parse_args()

# Try uncommenting the next line.
# print(args)

counts = {}

f = open(args.input_path)
reader = csv.reader(f)

for row in reader:
    # Try uncommenting the next line.
    # print(row)

    if args.start_date and args.start_date > row[2]:
        continue

    if args.tag and args.tag not in row[3].split(','):
        continue

    month = row[2][:7]
    if month not in counts:
        counts[month] = 0
    counts[month] += 1

# Try uncommenting the next line.
# print(counts)

if args.output_path:
    f = open(args.output_path, 'w')
    writer = csv.writer(f)
    for month in sorted(counts):
        writer.writerow([month, counts[month]])

else:
    for month in sorted(counts):
        print(month, str(counts[month]).rjust(3))
