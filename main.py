import imapclient
from dotenv import load_dotenv
import os
import pprint 

load_dotenv()
# print(os.environ.get('IMAP_SERVER'))
i = imapclient.IMAPClient(os.environ.get('IMAP_SERVER'))

try:
    i.login(os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_PASSWORD'))
    print(i.list_folders())
except Exception as e:
    # Print any error messages to stdout
    print(e)
