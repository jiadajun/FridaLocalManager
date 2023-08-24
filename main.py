import threading
import os
import sys
import logging
import inspect
import ctypes

sys.path.append(os.path.dirname(__file__) + os.sep + '../../')

from common.setting import REDIS_CLIENT_ONE
redis_client = REDIS_CLIENT_ONE
from server.frida_sign_api import *

exitFlag = 0

class myThread(threading.Thread):
    def __init__(self, name, Thread_id, device_data):
        threading.Thread.__init__(self)
        self.name = name
        self.threadID = Thread_id
        self.device_data = device_data
        self.redis_client = redis_client

    def monitor_thread(self):
        while True:
            thread_list = []
            time.sleep(30)
            for thread in threading.enumerate():
                thread_list.append(thread.getName())
                # print(thread.getName(), thread.ident)
                thread_error_status = self.redis_client.hget("frida_app_error", thread.getName())
                if thread_error_status:
                    thread_error_status = thread_error_status.decode()
                else:
                    time.sleep(3)
                    continue
                time.sleep(2)

                if thread_error_status == '1':
                    # 通过调用stop()方法关闭线程
                    exctype = SystemExit
                    tid = ctypes.c_long(thread.ident)
                    if not inspect.isclass(exctype):
                        exctype = type(exctype)
                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
                    if res == 0:
                        raise ValueError("invalid thread id")
                    elif res != 1:
                        # """if it returns a number greater than one, you're in trouble,
                        # and you should call it again with exc=NULL to revert the effect"""
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                        raise SystemError("PyThreadState_SetAsyncExc failed")
                    pass
                    # 终止完线程之后，重新打开此线程
                    time.sleep(5)
                    run_device = self.redis_client.hget("frida_device_name_ip_hash", thread.getName()).decode()
                    thread_i = myThread(thread.getName(), thread.ident, run_device)
                    thread_i.start()
                    thread_i.join()
            time.sleep(5)

    def run(self):
        print("开始线程：" + self.name, ' 线程ID：', self.threadID)
        if self.device_data == '0000':
            self.monitor_thread()
        else:
            try:
                self.redis_client.hset("frida_device_name_ip_hash", self.name, self.device_data)
                self.redis_client.hset("frida_app_error", self.name, '0')
                FlaskServer(self.device_data, self.threadID, self.name).flask_api()
            except:
                print("退出车重新开始....")
            print("退出线程：" + self.name)


if __name__ == '__main__':
    while True:
        print("开始执行...........................................................")
        # 设备列表 此处可以设置成动态获取，无线扩展
        device_list = ["0000", "192.168.137.63:6666;5000"]
        i = 1
        thread_pool = []
        for item in device_list:
            # 创建新线程
            thread_i = myThread("Thread-" + str(i), i, item)

            thread_pool.append(thread_i)
            i = i + 1
        # 开启新线程
        try:
            print("thread_pool 长度：", len(thread_pool))
            for th in thread_pool:
                th.start()
                tid = 1
                print("当前线程ID", tid, th)
            for th in thread_pool:
                th.join()
            print("退出主线程")
        except Exception as e:
            logging.exception(e)
            print('请求异常')
            break
        print("结束执行.....................................................")
