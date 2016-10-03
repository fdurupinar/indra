import sys
import time
import json
import logging
from slackclient import SlackClient

logger = logging.getLogger('indra_slack_bot')

def read_slack_token(fname=None):
    # Token can be found at https://api.slack.com/web#authentication
    if fname is None:
        fname = 'indrabot_slack_token'
    try:
        with open(fname, 'rt') as fh:
            token = fh.read().strip()
        return token
    except IOError:
        logger.error('Could not read Slack token from %s.' % fname)
        return None

def read_message(sc):
    event = sc.rtm_read()
    if event:
        try:
            event_type = event[0]['type']
            if event_type == 'message':
                msg = event[0]['text']
                user = event[0]['user']
                channel = event[0]['channel']
                user_info = json.loads(sc.server.api_call("users.info", users=user))
                username = user_info['users'][0]['name']
                return (channel, username, msg)
        except:
            pass
    return None

def send_message(sc, channel, msg):
    sc.rtm_send_message(channel, msg)

if __name__ == '__main__':
    token = read_slack_token()
    if not token:
        sys.exit()
    sc = SlackClient(token)
    conn = sc.rtm_connect()
    if not conn:
        logger.error('Could not connect to Slack.')
        sys.exit()
    while True:
        time.sleep(1)
        res = read_message(sc)
        if res:
            (channel, username, msg) = res
            if msg[0:8] == 'indrabot':
                reply = username + ' just said: ' + '"' + msg + '"'
                send_message(sc, channel, reply)
