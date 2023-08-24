# coding:utf8
import os
import time
import redis
import frida
from flask import Flask
import random
import sys

sys.path.append(os.path.dirname(__file__) + os.sep + '../../')

from common.setting import REDIS_CLIENT_ONE
redis_client = REDIS_CLIENT_ONE

class FlaskServer:
    def __init__(self, device_data, thread_id, thread_name):
        '''
        :param index_name: 索引名称
        :param index_type: 索引类型
        '''
        self.device_data = device_data
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.redis_client = redis_client

    def v_code_nums_letters(self, n=44):
        ret = ""
        for i in range(n):
            num = random.randint(0, 9)
            # num = chr(random.randint(48,57))#ASCII表示数字
            letter = chr(random.randint(97, 122))  # 取小写字母
            Letter = chr(random.randint(65, 90))  # 取大写字母
            s = str(random.choice([num, letter, Letter]))
            ret += s
        return ret

    def message(self, message, data):
        if message['type'] == 'send':
            print(f"[*] {message['payload']}")
        else:
            print(message)

    def api_error(self, ip, val):
        self.redis_client.hset("frida_app_error", ip, val)

    # 所有用户的队列
    def flask_api(self):
        # 参数配置-------------------------------------------------------
        task_list = self.device_data.split(";")
        device_info = task_list[0]
        flask_prot = task_list[1]
        device_info_list = device_info.split(":")
        frida_device = f"{device_info_list[0]}:5555"
        app_name = "xxx.xxx.xxx"
        app_start_activity = "xxxx.xxx.Activity"
        # start  每次开启，需要重新打开APP，防止异常的启动造成无法加载的情况---------------------------
        # 关闭 APP
        os.system(f"adb  -s {frida_device} shell am force-stop {app_name}")
        print("APP 已经关闭成功.......")
        time.sleep(5)
        # 开启 APP
        os.system(f"adb  -s {frida_device} shell am start -n {app_name}/{app_start_activity}")
        print("APP 开启成功...........")
        time.sleep(20)
        # end  每次开启，需要重新打开APP，防止异常的启动造成无法加载的情况---------------------------

        app = Flask(__name__)

        # frida js 文件加载------------------------------------------------------------------
        session = frida.get_device_manager().add_remote_device(device_info).attach(app_name)
        with open("sign.js") as f:
            jsCode = f.read()
        script = session.create_script(jsCode)
        script.on("message", self.message)
        script.load()

        # flask API 主程序----------------------------------------------------------------------
        @app.route('/sign_dt', methods=['POST'])  # data解密
        def sign_dt():
            # 业务逻辑
            return "业务逻辑"

        print("开启端口服务：", flask_prot)
        app.run(port=int(flask_prot))
