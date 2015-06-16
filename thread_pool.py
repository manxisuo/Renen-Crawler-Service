#coding:utf-8
import threading
from Queue import Queue

# @private
def handle_item(q, func, timeout):
    while True:
        item = q.get(timeout = timeout)
        func(item)
        q.task_done()

# @private
def handle_item_with_out_queue(q, q_out, func, timeout):
    while True:
        item = q.get(timeout = timeout)
        func(item, q_out)
        q.task_done()

class Pool():
    def __init__(self, seq):
        if isinstance(seq, Queue):
            self.q = seq
        else:
            self.q = Queue()
            for item in seq:
                self.q.put(item)

    # 提交一个任务
    def submit_task(self, func, thead_num = 5, timeout = None):
        for i in range(thead_num):
            t = threading.Thread(target = handle_item, args = (self.q, func, timeout))
            t.daemon = True
            t.start()

    # 提交一个任务
    def sumbit_task_with_out_queue(self, func, thead_num = 5, timeout = None):
        q_out = Queue()
        for i in range(thead_num):
            t = threading.Thread(target = handle_item_with_out_queue, args = (self.q, q_out, func, timeout))
            t.daemon = True
            t.start()
        return q_out

    def join(self):
        self.q.join()
