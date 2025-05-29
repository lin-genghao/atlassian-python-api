from atlassian import Confluence

# 初始化Confluence客户端
host = "http://confluence.mmcuav.com:8002"
username = "genghaolin"
password = "genghaolin"
mmc_confluence = Confluence(
    url=host,
    username=username,
    password=password,
)

def get_page_title(id):
    content = mmc_confluence.get_page_by_id(page_id=id)
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
        content = mmc_confluence.get_page_by_id(page_id=id)
        page_id = content['id']
        # 获取页面的详细信息，包括其子页面
        page_details = confluence_client.get_child_title_list(page_id=page_id)
        return bool(page_details)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



def get_all_child_title(parent_id, collected_ids=None, level=0):
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
        child_ids = mmc_confluence.get_child_id_list(page_id=parent_id)
        for id  in child_ids :
            # 打印相应层级的"-"字符
            print("-" * (level * 2), end=' ')
            title = get_page_title(id)
            print(id + ' ' + title)
            # print(id)
            # 将子页面的ID和父页面的ID作为一个元组添加到列表中
            collected_ids.append((id, parent_id, level))
            
            if has_children(id, mmc_confluence):
                get_all_child_title(id, collected_ids, level+1)
                # print("This page has children.")
            # else:
            #     print("This page does not have children.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return collected_ids

# 父页面的ID
# parent_page_id = "your-parent-page-id"

source_title = "SLAM"
content_old = mmc_confluence.get_page_by_title(space="software", title=source_title, expand="space")
id_old = content_old['id']
print(id_old)

title_buf = get_page_title(id_old)
print(title_buf)

id_list = get_all_child_title(id_old)
print(id_list)
