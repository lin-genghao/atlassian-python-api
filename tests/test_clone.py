from atlassian import Confluence
from bs4 import BeautifulSoup
import re

import logging
from atlassian import Confluence
import os
import time

host = "http://confluence.mmcuav.com:8002"
username = "genghaolin"
password = "genghaolin"

mmc_confluence = Confluence(
    url=host,
    username=username,
    password=password,
)
# If you know Space and Title
# content1 = mmc_confluence.get_page_by_title(space="software", title="ROS学习-D435i深度摄像头")

# If you know page_id of the page
source_title = "ROS学习-Topics"
content_old = mmc_confluence.get_page_by_title(space="software", title=source_title, expand="space,body.storage,version,container")
id_old = content_old['id']
print(id_old)

title = content_old['title']
print(title)

html = content_old['body']['storage']['value']

lgh_confluence = Confluence(url="http://genghaolin.wiki/", username="root", password="Lgh201022")

# 使用BeautifulSoup解析HTML代码并修复错误
soup = BeautifulSoup(html, 'html.parser')
fixed_html = str(soup)

# 创建页面
# status = lgh_confluence.create_page(space="SPC", title=title, parent_id=1507355, body="")

content_new = lgh_confluence.get_page_by_title(space="SPC", title=title, expand="space,body.view,version,container")

id_new = content_new['id']
print("new id: " + id_new)

# 下载附件
current_dir = os.getcwd()
# print("--->"+current_dir)
my_path = os.path.join(current_dir, 'attachment_tests',  str(id_new))

# 检查这个路径是否存在，如果不存在，就创建它
if not os.path.exists(my_path):
    os.makedirs(my_path)

print(f"Directory created at: {my_path}")

page = id_old
mmc_confluence.download_attachments_from_page(page, path=my_path)
# logging.basicConfig(level=logging.DEBUG)


# 更新附件
all_items = os.listdir(my_path)
for filename in all_items:
    file_path = os.path.join(my_path, filename)
    print(f"file_path: {file_path}")
    lgh_confluence.attach_file(file_path, page_id=id_new)    

# 将fixed_html写入到文件中
with open('output.html', 'w', encoding='utf-8') as file:
    file.write(fixed_html)

status = lgh_confluence.update_page(parent_id=None, title=title, page_id=id_new, body=fixed_html)


