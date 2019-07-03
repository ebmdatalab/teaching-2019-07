import os


# Set this to True to send email notifications about new news articles.
# If you change this, you will need to change EMAIL_RECIPIENT, EMAIL_USER, and
# EMAIL_PASSWORD below.  See README for more details.
SEND_EMAIL = True

# Change this to your email address.
EMAIL_RECIPIENT = 'changeme@example.com'

# Change this to the email address of a gmail.com account.
EMAIL_USER = 'changeme@gmail.com'

# Change this to an app password belonging to the gmail.com account.
EMAIL_PASSWORD = 'changeme'

# Do not change these unless you know what you are doing!
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

# Change this if you would like to write the data to another location.
CSV_PATH = os.path.expanduser('~/full-example/nhs-news.csv')

# Change this if you would like to write the notebook in another location.
# NOTEBOOK_PATH = os.path.expanduser('~/work/ebmdatalab/teaching/2019-07-03/full-example/nhs-news-analysis.ipynb')
NOTEBOOK_PATH = os.path.expanduser('~/full-example/nhs-news-analysis.ipynb')
