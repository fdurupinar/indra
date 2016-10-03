from slackclient import SlackClient

token = open('indrabot_slack_token', 'r').read().strip()     # found at https://api.slack.com/web#authentication
sc = SlackClient(token)import


import time
import json

if sc.rtm_connect():
    while True:

        user = ''
        msg = ''
        reply = ''

        time.sleep(1)
        a = sc.rtm_read()

        if len(a)>0:
            try:
                event_type = a[0]['type']
                if event_type == 'message':
                    msg = a[0]['text']
                    user = a[0]['user']
                    channel = a[0]['channel']

                    user_info = json.loads(sc.server.api_call("users.info",users =user))
                    username = user_info['users'][0]['name']

                    if msg[0:8] == 'indrabot':
                        reply = username + ' just said: ' + '"' + msg + '"'
                        sc.rtm_send_message(channel, reply)


            except:
                None
