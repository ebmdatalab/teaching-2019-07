# This program:
#
# * scrapes any new records from https://www.england.nhs.uk/news/
# * appends new records to a CSV file
# * updates a notebook with some analysis
# * if configured, sends an email notification about new articles
#
# Program configuration is in config.py.  If you want the program to send
# email, see the instructions in README.

import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

import config


fieldnames = ['url', 'title', 'pubdate', 'tags']

if not os.path.exists(config.CSV_PATH):
    # There is no file at config.CSV_PATH, so we create it.

    # First, create the directory if it doesn't already exist.
    dir_path = os.path.dirname(config.CSV_PATH)
    os.makedirs(dir_path, exist_ok=True)

    # Create the CSV file and write the headers.
    with open(config.CSV_PATH, 'w') as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()


# Read all records we've already seen.
with open(config.CSV_PATH) as f:
    records = list(csv.DictReader(f))


if records:
    # The CSV file was not empty, so we don't need to scrape the whole dataset
    # again.  We find the publication date of the most recent article we have,
    # and only request articles published on that date or later.

    # This is a "list comprehension".
    pubdates = [record['pubdate'] for record in records]
    latest_pubdate = max(pubdates)
    url = 'https://www.england.nhs.uk/news/?filter-date-from=' + latest_pubdate

else:
    # The CSV file was empty (this is probably the first time we've run the
    # scraper) so we need to scrape the whole dataset.
    url = 'https://www.england.nhs.uk/news/'


# Even though we're only not requesting the whole dataset (unless this is the
# first time we've run the scraper) we might scrape a record we've seen before
# (why?) so we need to keep track of the articles we have seen, otherwise we'll
# end up with duplicates in our data.
seen_urls = [record['url'] for record in records]

# We're going to add data about new articles to this list.
new_records = []

while True:
    # Request the next page of articles and parse the contents.
    rsp = requests.get(url)
    doc = BeautifulSoup(rsp.content, 'html.parser')

    for article in doc.find_all('article', class_='post group'):
        # For each article on the page, extract the metadata (URL, publication
        # date, title, tags).

        article_url = article.find('a', class_='read-more')['href']
        if article_url in seen_urls:
            # This is an article we've seen before, so we don't add it to our
            # list of new records.
            continue

        pubdate = article.find('time')['pubdate']
        title = article.find('h2').text
        tags = []
        for li in article.find('ul', class_='topics').find_all('li'):
            tag_url = li.find('a')['href']
            query = urlparse(tag_url).query
            tag = parse_qs(query)['filter-category'][0]
            assert ',' not in tag
            tags.append(tag)

        # Add the metadata to the list of new records.
        record = {
            'url': article_url,
            'title': title,
            'pubdate': pubdate,
            'tags': ','.join(tags)
        }
        new_records.append(record)

    next_page_link = doc.find('a', class_='next-page')

    if next_page_link:
        # There is a link to the next page, so extract that link and loop back to
        # the top.
        url = next_page_link['href']
    else:
        # There is no link to the next page, so break out of the loop.
        break


num_new_articles = len(new_records)

print('Found {} new articles'.format(num_new_articles))

if num_new_articles == 0:
    # There are no new articles, so there's nothing to do.
    exit()


# Write the new records to the CSV file.
with open(config.CSV_PATH, 'a') as f:
    writer = csv.DictWriter(f, fieldnames)
    writer.writerows(new_records)


# Update the notebook, by reading it, running it, and writing it back.
with open(config.NOTEBOOK_PATH) as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
metadata = {'path': os.path.dirname(config.NOTEBOOK_PATH)}
ep.preprocess(nb, {'metadata': metadata})

with open(config.NOTEBOOK_PATH, 'w') as f:
    nbformat.write(nb, f)


if not config.SEND_EMAIL:
    # We're not set up to send email, so quit here.
    exit()


# TODO: comment
if num_new_articles == 1:
    subject = 'New article on NHS News'
    body_lines = ['There is 1 new NHS News article:']
else:
    subject = 'New articles on NHS News'
    line = 'There are {} new NHS News articles:'.format(num_new_articles)
    body_lines = [line]

body_lines.append('')
for record in new_records:
    body_lines.append('* {}'.format(record['title']))

body = '\r\n'.join(body_lines)

# Create a message object and set the appropriate properties.
msg = MIMEMultipart()
msg['From'] = config.EMAIL_USER
msg['To'] = config.EMAIL_RECIPIENT
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

# Start a secure SMTP session, authenticate, send the message, and close
# the session.
client = smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT)
client.ehlo()
client.starttls()
client.ehlo()
client.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
client.sendmail(config.EMAIL_USER, config.EMAIL_RECIPIENT, msg.as_string())
client.quit()
