from requests import post, get
from requests_html import HTMLSession
from time import time
from re import sub
import json
from gzip import decompress
from config import user, passwd

def get_webauth_cookies():
    url = 'https://id.tsinghua.edu.cn/do/off/ui/auth/login/form/a585295b8da408afdda9979801383d0c/0?/fp/'
    response = get(url=url)
    return response.cookies

def get_ticket_url(webauth_cookies):
    url = 'https://id.tsinghua.edu.cn/do/off/ui/auth/login/check'
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'MIME Type': 'application/x-www-form-urlencoded',
        'i_user': user,
        'i_pass': passwd,
        'i_captcha': None
    }
    session = HTMLSession()
    response = session.post(url=url, headers=headers, data=data, cookies=webauth_cookies)
    return response.html.absolute_links.pop()

def get_thos_cookies():
    webauth_cookies = get_webauth_cookies()
    ticket_url = get_ticket_url(webauth_cookies)
    response = get(ticket_url, allow_redirects=False)
    return response.cookies

def get_service_id(thos_cookies):
    url = 'https://thos.tsinghua.edu.cn/fp/fp/formHome/AllSvsByConditionpage'
    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    data = {
        "project_id": "",
        "category_ids": "",
        "orderBy": "defaultAsc",
        "firstCharacter": "",
        "unit_id": "",
        "isCollect": "all",
        "isRecommend": "no",
        "pageNum": "1",
        "pageSize": "40"
    }
    response = post(url=url, data=json.dumps(data), headers=headers, cookies=thos_cookies)
    items = json.loads(response.content.decode())
    for item in items['list']:
        if item['NAME'] == '学生健康及出行情况报告':
            return item['ID']
    raise Exception('No item named "学生健康及出行情况报告"')

def get_url_params(service_id, thos_cookies):
    url = 'https://thos.tsinghua.edu.cn/fp/fp/serveapply/getServeApply'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json;charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        "serveID": service_id,
        "from": "hall"
    }
    response = post(url=url, headers=headers, data=json.dumps(data), cookies=thos_cookies)
    items = json.loads(response.content.decode())
    return {
        'formid': items['formID'],
        'process': items['procID'],
        'service_id': items['resource_id'],
        'privilegeId': items['privilegeId'],
        'seqId': None
    }

def get_previous_data(url_params, thos_cookies):
    url = 'https://thos.tsinghua.edu.cn/fp/formParser'
    params = {
        'status': 'select',
        'formid': url_params['formid'],
        'service_id': url_params['service_id'],
        'process': url_params['process'],
        'seqId': url_params['seqId'],
        'privilegeId': url_params['privilegeId']
    }
    session = HTMLSession()
    response = session.get(url=url, params=params, cookies=thos_cookies)
    return response.html.find('#dcstr', first=True).text

def update_data(previous_data):
    return sub(r'{"name":"SYS_DATE","source":"interface","type":"date","value":"(?P<time>\d+)"}', update_time, previous_data)

def update_time(matched):
    total = matched.group()
    _time = matched.group('time')
    return total.replace(_time, str(int(time() * 1000)))


def push_data(url_params, plain_data, thos_cookies):
    params = {
        'status': 'update',
        'formid': url_params['formid'],
        'seqId': url_params['seqId'],
        'process': url_params['process'],
        'workflowAction': 'startProcess',
        'workitemid': None,    
    }
    url = 'https://thos.tsinghua.edu.cn/fp/formParser'
    headers = {
        'Content-Type': 'text/plain;charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = post(url=url, data=plain_data.encode('utf-8'), params=params, headers=headers, cookies=thos_cookies)
    return response.content.decode()

if __name__ == '__main__':
    cookies = get_thos_cookies()
    page = get_service_id(cookies)
    service_id = get_service_id(cookies)
    url_params = get_url_params(service_id, cookies)
    previous_data = get_previous_data(url_params, cookies)
    push_data(url_params, update_data(previous_data), cookies)




