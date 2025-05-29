# coding=utf-8
import logging
from datetime import datetime

from atlassian import Confluence

host = "http://confluence.mmcuav.com:8002"
username = "genghaolin"
password = "genghaolin"

confluence = Confluence(
    url=host,
    username=username,
    password=password,
)

logging.basicConfig(level=logging.DEBUG)

filename = "test_file.txt"
with open(filename, "w") as f:
    f.write(str(datetime.utcnow()))

confluence.attach_file(filename, page_id="123456789")

link = """<p>
  <ac:link>
    <ri:attachment ri:filename="{}"/>
  </ac:link>
</p>""".format(
    filename
)

confluence.append_page(123456789, "Page Title", link)
