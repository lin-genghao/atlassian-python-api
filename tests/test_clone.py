from atlassian import Confluence
from atlassian import Confluence
from bs4 import BeautifulSoup
import re
import requests
from requests import HTTPError
from atlassian.errors import ApiError, ApiNotFoundError, ApiPermissionError, ApiValueError, ApiConflictError, ApiNotAcceptable
from atlassian.rest_client import AtlassianRestAPI

import logging
from atlassian import Confluence
import os
import time

source_host = "http://confluence.com:8002"
source_username = "username"
source_password = "password"

source_confluence = Confluence(
    url=source_host,
    username=source_username,
    password=source_password,
)

target_host = "http://192.168.31.1:8090"
target_username = "username"
target_password = "password"

target_confluence = Confluence(
    url=target_host,
    username=target_username,
    password=target_password,
)
        
def get_page_title(id):
    content = source_confluence.get_page_by_id(page_id=id)
    title = content['title']
    return title

def has_children(id, confluence_client):
    """
    判断页面是否有子页面。
    
    参数:
    parent_page_id: 父页面的ID。
    confluence_client: Confluence客户端实例。
    
    返回:
    一个布尔值，如果页面有子页面则返回True，否则返回False。
    """
    try:
        content = source_confluence.get_page_by_id(page_id=id)
        page_id = content['id']
        # 获取页面的详细信息，包括其子页面
        page_details = confluence_client.get_child_title_list(page_id=page_id)
        return bool(page_details)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



def get_all_child_title(parent_id, source_space_1=None, collected_ids=None, level=1, target_space=None):
    """
    递归地获取所有子孙页面的ID，并与它们的父页面ID一起返回为元组。
    
    参数:
    parent_id: 父页面的ID。
    confluence_client: Confluence客户端实例。
    collected_ids: 已收集的页面ID元组列表（用于递归调用）。
    
    返回:
    包含所有子孙页面ID与父页面ID的元组列表。
    """
    #如果是第一次调用函数，初始化收集ID的列表
    if collected_ids is None:
        collected_ids = []

    try:
        child_ids = source_confluence.get_child_id_list(page_id=parent_id)
        # print("child_ids: " + str(child_ids))
        for id  in child_ids :
            title = get_page_title(id)
            parent_title = get_page_title(parent_id)
            # 打印相应层级的"-"字符
            print('\n')
            print("-" * (level * 2), end=' ')
            print("title: " + title)
            # print("parent_title: " + parent_title)
            # print(id + ' ' + title + ' 父节点： ' + parent_title)
            # print("level: " + str(level))
            
            # if(level == 2):
            #     print("title: " + title)
            #     print(source_space_1)
                # print("parent_title: " + parent_title)
                # print("target_space: " + target_space)
                
            confluence_source_to_target(title, source_id=None, source_space_1=source_space_1, parent_title=parent_title, target_space=target_space)
            # print(id)
            # 将子页面的ID和父页面的ID作为一个元组添加到列表中
            collected_ids.append((id, parent_id, level))
            
            if has_children(id, source_confluence):
                get_all_child_title(id, source_space_1=source_space_1, collected_ids=collected_ids, level=level+1, target_space=target_space)
                print("This page has children.")
            # else:
            #     print("This page does not have children.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return collected_ids

def confluence_source_to_target(source_title, source_id, source_space_1, parent_title, target_space):
    """
    复制confluence页面
    
    参数:
    source_id: 页面的ID。
    parent_id: 父页面的ID。
    """
    # If you know Space and Title
    # source_title = "ROS学习-Topics"
    parent_content = target_confluence.get_page_by_title(space=target_space, title=parent_title, expand="container")
    parent_id = parent_content['id']
    parent_title = parent_content['title']
    # print('parent_id: ' + parent_id + ' parent_title: ' + parent_title)
    # print('--' + parent_title)


    source_content = source_confluence.get_page_by_title(space=source_space_1, title=source_title, expand="space,body.storage,version,container")
    if source_id == None:
        source_id = source_content['id']
    # print(source_id)

    source_title = source_content['title']
    # print('----' + source_title)

    html = source_content['body']['storage']['value']

    # 使用BeautifulSoup解析HTML代码并修复错误
    soup = BeautifulSoup(html, 'html.parser')
    fixed_html = str(soup)

    page_exist = 0
    # 创建页面
    try:
        status = target_confluence.create_page(space=target_space, title=source_title, parent_id=parent_id, body="")
    except HTTPError as e:
        print(f"页面已经创建")
        page_exist = 1

    if page_exist == 0:
        target_content = target_confluence.get_page_by_title(space=target_space, title=source_title, expand="space,body.storage,version,container")

        target_id = target_content['id']
        print("new id: " + target_id)

        # 下载附件
        current_dir = os.getcwd()
        # print("--->"+current_dir)
        my_path = os.path.join(current_dir, 'attachment_tests',  source_title)

        # 检查这个路径是否存在，如果不存在，就创建它
        if not os.path.exists(my_path):
            os.makedirs(my_path)

        print(f"Directory created at: {my_path}")

        source_confluence.download_attachments_from_page(source_id, path=my_path)
        # logging.basicConfig(level=logging.DEBUG)

        # 更新附件
        all_items = os.listdir(my_path)
        for filename in all_items:
            file_path = os.path.join(my_path, filename)
            print(f"file_path: {file_path}") 
            try:
                target_confluence.attach_file(file_path, page_id=target_id)
            except requests.exceptions.ReadTimeout as e:
                print("Read time out")


        # 将fixed_html写入到文件中
        with open('output.html', 'w', encoding='utf-8') as file:
            file.write(fixed_html)

        status = target_confluence.update_page(parent_id=None, title=source_title, page_id=target_id, body=fixed_html)

        print("copy succeed!")


print("\n=============Confluence copy start============")

_source_title = "foc电调"
_source_space = "software"
_parent_title = "嵌入式组"
_target_space = "SPC"

print(_source_title)
confluence_source_to_target(source_title=_source_title, source_id=None, source_space_1=_source_space, parent_title=_parent_title, target_space=_target_space)

source_content = source_confluence.get_page_by_title(space=_source_space, title=_source_title, expand="space")
source_id = source_content['id']
# print(source_id)

id_list = get_all_child_title(source_id, source_space_1=_source_space, target_space=_target_space)
# print(id_list)

# confluence_source_to_target("SLAM", source_id=None, parent_id=1507338)

print("==============================================\n")


