import time
import sys

import stomp

TARGET_QUEUE_NAME = 'TEST.QUEUE'

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        print('received a message "%s"' % frame.body)


def consumer_main():
    conn = stomp.Connection()
    conn.set_listener('', MyListener())
    conn.connect('admin', 'password', wait=True)
    conn.subscribe(TARGET_QUEUE_NAME, id=1, ack='auto')
    time.sleep(1) # secs
    # conn.subscribe(destination='/queue/test', id=1, ack='auto')
    # conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')
    # time.sleep(2)
    conn.disconnect()

def producer_main():
    conn = stomp.Connection10()
    conn.connect()
    conn.send(TARGET_QUEUE_NAME, 'A test message from STOMP client')
    conn.disconnect()


if __name__ == '__main__':
    # consumer_main()
    producer_main()