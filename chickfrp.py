# chickfrp
# author @JXDYYY
# cron 30 8 * * *
# 变量 export chick=账号#密码@账号2#密码2@....  多账号使用@ 或者\n 分隔
# 签到获取流量
# 仅用于学习交流，请勿用于商业用途，禁止用于任何非法用途，下载后请24小时内删除，否则后果自负



import requests
from typing import Optional, Dict
from urllib.parse import urlparse
import time
import json
import logging
import os
from typing import List,Tuple
import random

logging.basicConfig(level=logging.INFO)

def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{func.__name__}: {e}")
            return None
    return wrapper


class Template:
    def __init__(self, index: int, cookie: str) -> None:
        self.index = index
        self.session = requests.Session()
        self.logger = logging.getLogger(f"用户{self.index+1}")
        self.token = cookie
        self.content = ''

    def log(self, msg):  # 改写一下日志可以输出定向的log单账号推送，全部账号一起推送 在run里return self.content即可
        self.logger.info(msg)
        self.content += str(msg) + '\n'

    @handle_errors
    def request(self, url, method='get', data=None, add_headers: Optional[Dict[str, str]] = None, headers=None, dtype='json'):
        host = urlparse(url).netloc
        _default_headers = {
            "Host": host,
        }
        request_headers = headers or _default_headers
        # request_headers = request_headers.copy()
        if method == 'post' and data:
            if isinstance(data, dict):
                data = json.dumps(data, separators=(',', ':'))
                request_headers.update({'Content-Type': 'application/json', 'content-length': str(len(data))})
            else:
                request_headers.update({'Content-Type': 'application/x-www-form-urlencoded', 'content-length': str(len(data))})
        if add_headers:
            request_headers.update(add_headers)

        response = self.session.request(method, url, headers=request_headers, data=data)
        if response.status_code == 200:
            if dtype == 'json':
                return response.json()
            else:
                return response.text()
        else:
            self.log(f"请求失败，状态码：{response.status_code}")

    def example(self):
        # Here you can write some code.
        pass
    time.sleep(10)
    @handle_errors
    def login(self,username:str, password:str):
        self.log(f"开始登录账号{username}")
        login_url = 'https://api.chickfrp.com/login'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            "Origin": "https://console.chickfrp.com",
            "Referer": "https://console.chickfrp.com/"
        }
        data = {
            'username': username,
            'password': password
        }
        try:
            response = self.session.post(url=login_url, headers=headers, json=data)  # 获取登录后的cookie
            if response.status_code == 200:
                self.session.cookies.update(response.cookies)  # 更新会话的cookies
                self.log(f"账号{self.index+1}登录成功")
                return True  
            else:
                self.log(f'账号{self.index+1}登录失败,获取cookie失败\n,{response.text}')
                return False  
        except requests.exceptions.RequestException as e:
            self.log(f"发生网络请求错误: {e}")
            return False
         
    def sign_in(self):
        self.log(f"账号{self.index+1}正在签到...")
        sign_inurl = 'https://api.chickfrp.com/index/sign'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            'Origin': 'https://console.chickfrp.com',
            'Referer': 'https://console.chickfrp.com/',
        }  
        cookie = self.session.cookies.get_dict()  # 获取当前会话的cookies
        try:
            response = self.session.post(url=sign_inurl, headers=headers,cookies=cookie)  # 使用正确的请求方式，并传入cookie
            if response.status_code == 200:
                self.log(f"账号{self.index+1}签到成功!")
                return True
            else:
                self.log(f"账号{self.index+1}签到失败!，响应信息：{response.text}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"发生网络请求错误: {e}")
            return False
        
    def logout(self):
        self.log(f"账号{self.index+1}正在退出...")
        logout_url = 'https://api.chickfrp.com/logout'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            "Origin": "https://console.chickfrp.com",
            "Referer": "https://console.chickfrp.com/"
        }
        try:
            response = self.session.post(url=logout_url, headers=headers)  # 使用正确的URL
            if response.status_code == 200:
                self.log(f"账号{self.index+1}退出成功")
            else:
                self.log(f"账号{self.index+1}退出失败，响应信息：{response.text}")
        except requests.exceptions.RequestException as e:
            self.log(f"发生网络请求错误: {e}")
        
    @handle_errors
    def run(self):
        if '#' in self.token:
            account,password = self.token.split('#',1)
            self.login(account,password)
        else:
            self.log(f'账号{self.index+1}格式不对，应该使用#连接,跳过登录')
            return
        self.sign_in()
        time.sleep(random.randint(1,5))
        self.logout()
        time.sleep(random.randint(1,5))
        self.session.close()


@handle_errors
def check_env(env: str) -> List[Tuple[str, str]]:
    accounts_raw = os.getenv(env, 'chick')
    delimiter = '@' if '@' in accounts_raw else '\n'
    if not accounts_raw:
        logging.warning(f"请设置环境变量 {env}, @分割或者换行分割,账号密码使用#连接")
        return []
    
    account_data: list[tuple[str, str]] = []
    
    for account_pair in accounts_raw.split(delimiter):
        account_pair = account_pair.strip()
        if '#' in account_pair:
            username,password = account_pair.split('#',1)
            account_data.append((username,password))
    return account_data

@handle_errors
def main():
    users = check_env(env='chick')
    tasks = []
    for index, (username,password) in enumerate(users):
        token = f"{username}#{password}"
        task = Template(index, token)
        tasks.append(task)
    for task in tasks:
        task.run()

if __name__ == '__main__':
    main()
