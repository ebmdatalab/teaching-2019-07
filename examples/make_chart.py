import argparse
import csv

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Plot number of articles published each month')
parser.add_argument('input_path', help='Path to CSV file containing aggregated data')
parser.add_argument('output_path', help='Path to file to save chart')

args = parser.parse_args()

f = open(args.input_path)
reader = csv.reader(f)

labels = []
values = []

for row in reader:
    labels.append(row[0])
    values.append(int(row[1]))

fig, ax = plt.subplots()

ax.plot(labels, values, color='red')

ax.xaxis.set_major_locator(plt.MultipleLocator(6))
ax.tick_params(axis='x', labelrotation=90)
ax.set_xlabel('Month')
ax.set_ylabel('Number of articles')
ax.set_title('NHSE News: articles per month')

fig.savefig(args.output_path, bbox_inches='tight')
