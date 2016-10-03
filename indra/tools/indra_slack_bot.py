import sys
import time
import json
import indra
import logging
from slackclient import SlackClient

logger = logging.getLogger('indra_slack_bot')

user_cache = {}
channel_cache = {}

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

def get_user_name(sc, user_id):
    user_name = user_cache.get(user_id)
    if user_name:
        return user_name
    res = sc.server.api_call('users.info', users=user_id)
    user_info = json.loads(res)
    for user in user_info['users']:
        if user['id'] == user_id:
            user_cache[user_id] = user['name']
            return user['name']
    return None

def get_channel_name(sc, channel_id):
    channel_name = channel_cache.get(channel_id)
    if channel_name:
        return channel_name
    res = sc.server.api_call('channels.info', channel=channel_id)
    channel_info = json.loads(res)
    channel = channel_info['channel']
    if channel['id'] == channel_id:
        channel_cache[channel_id] = channel['name']
        return channel['name']
    return None

def read_message(sc):
    events = sc.rtm_read()
    logger.info('%s events happened' % len(events))
    if not events:
        return None
    try:
        event = events[0]
        event_type = event.get('type')
        if not event_type:
            return
        if event_type == 'message':
            msg = event['text']
            user = event['user']
            channel = event['channel']
            user_name = get_user_name(sc, user)
            channel_name = get_channel_name(sc, channel)
            logger.info('Message received - [%s/%s]: %s' %
                        (channel_name, user_name, msg))
            return (channel, user_name, msg)
    except Exception as e:
        logger.error('Could not read message')
        logger.error(e)
    return None

def send_message(sc, channel, msg):
    sc.rtm_send_message(channel, msg)
    channel_name = get_channel_name(sc, channel)
    logger.info('Message sent - [%s]: %s' %
                (channel_name, msg))

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
        try:
            time.sleep(1)
            res = read_message(sc)
            if res:
                (channel, username, msg) = res
                if msg[0:8] == 'indrabot':
                    reply = username + ' just said: ' + '"' + msg + '"'
                    send_message(sc, channel, reply)
        except KeyboardInterrupt:
            logger.info('Shutting down due to keyboard interrupt.')
            sys.exit()
