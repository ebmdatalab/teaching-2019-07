import argparse
import csv
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser(description='Scrape metadata about articles and write to CSV')
parser.add_argument('output_path', help='Path to write CSV output')
parser.add_argument('--start-date', help='Only scrape articles published on or after START_DATE')

args = parser.parse_args()

fieldnames = ['url', 'title', 'pubdate', 'tags']

f = open(args.output_path, 'w')
writer = csv.DictWriter(f, fieldnames)

scrape_complete = False
url = 'https://www.england.nhs.uk/news/'

while True:
    print(url)
    rsp = requests.get(url)

    doc = BeautifulSoup(rsp.text, 'html.parser')

    for article in doc.find_all('article', class_='post group'):
        pubdate = article.find('time')['pubdate']
        if args.start_date and pubdate < args.start_date:
            scrape_complete = True
            break

        title = article.find('h2').text
        article_url = article.find('a', class_='read-more')['href']
        tags = []
        for li in article.find('ul', class_='topics').find_all('li'):
            tag_url = li.find('a')['href']
            query = urlparse(tag_url).query
            tag = parse_qs(query)['filter-category'][0]
            assert ',' not in tag
            tags.append(tag)

        row = {
            'url': article_url,
            'title': title,
            'pubdate': pubdate,
            'tags': ','.join(tags)
        }
        writer.writerow(row)

    if scrape_complete:
        break

    next_page_link = doc.find('a', class_='next-page')

    if next_page_link:
        url = next_page_link['href']
    else:
        break
