import logging
from datetime import datetime
from atlassian import Confluence
import os

host = "http://confluence.mmcuav.com:8002"
username = "genghaolin"
password = "genghaolin"

confluence = Confluence(
    url=host,
    username=username,
    password=password,
)

confluence_lgh = Confluence(
    url="http://genghaolin.wiki",
    username="root",
    password="Lgh201022",
)

# this is the directory where the attachments will be saved.
# In this example we use current working directory where script is executed + subdirectory 'attachment_tests'

current_dir = os.getcwd()
# print("--->"+current_dir)
my_path = current_dir + "/attachment_tests"
# print("--->"+my_path)
page = 77136432  # make sure the page id exists and has attachments

confluence.download_attachments_from_page(page, path=my_path)
# Directory  'attachment_tests' should include saved attachment. If directory deosn't exist or if there is permission issue function should raise an error.

logging.basicConfig(level=logging.DEBUG)

filename = my_path + "/image2024-4-23_9-59-44.png"
# with open(filename, "w") as f:
#     f.write(str(datetime.utcnow()))

confluence_lgh.attach_file(filename, page_id="9928821")
