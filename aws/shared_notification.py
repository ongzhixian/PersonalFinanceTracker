"""
Notification module
"""
import json
import http.client
import logging
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

class Notification(object):
    def __init__(self):
        pass
        # runtime_dns_domain = environ.get('USERDNSDOMAIN')
        # aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
        # if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])

    def send_telegram_message(self, chat_id: str, message: str):
        # running_on_aws_lambda = 'LAMBDA_TASK_ROOT' in environ
        bot_api_token = environ['bot_api_token'] if 'bot_api_token' in environ else None
        bot_api_token= '7564623663:AAEFoyiBpgGmKjxhu6xr9LXbw9BNYcQk6SY'

        if bot_api_token is None:
            logging.warning('bot_api_token is not defined in environment variables; send_message does nothing.')
            return

        conn = http.client.HTTPSConnection('api.telegram.org')
        # if running_on_aws_lambda:
        #     conn = http.client.HTTPSConnection('api.telegram.org')
        # else:
        #     proxy_host = 'siproxyvip.ad.mlp.com'
        #     proxy_port = 3128
        #     conn = http.client.HTTPConnection(proxy_host, proxy_port)

        headers = {
            'Content-type': 'application/json; charset=utf-8',
        }

        body = json.dumps({
            'chat_id': chat_id,
            'text': message
        })

        conn.request(method="POST",
                     url=f"https://api.telegram.org/bot{bot_api_token}/sendMessage",
                     body=body,
                     headers=headers)

        response = conn.getresponse()
        print("Status:", response.status, response.reason)
        data = response.read()
        print("Response body:", data.decode())
        conn.close()

    # def send_slack_message(self):
    #     pass
    #     # Place holder for implementation in the future

def main():
    notification = Notification()
    notification.send_telegram_message('-1002841796915', 'hello world')

if __name__ == "__main__":
    main()
