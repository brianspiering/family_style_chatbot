"""Family Style Chat Bot: Group meal ordering made simple

Given a group of Slack users, order the best group meal for them.
"""

import os
from collections import namedtuple
from datetime import datetime
from random import choice
import time

from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + str(BOT_ID) + ">:"
BotDo = namedtuple("BotDo", ['response', 
                            'action'])
dialogue = {'lunch': BotDo("Did someone say lunch?", 
                            None),
          'me': BotDo(["Okay.", "Got it!"], 
                        "TODO: add logic"),
          'order': BotDo(["Sounds good. Based on your group preferences here are my suggestions: ..."], 
                        "TODO: add logic"),
          'go ahead': BotDo("Okay. I have order that meal. Here is the tracking number #867-5309. I'll keep you posted and let you when it arrives.",
           "TODO: add order logic"),
          'test': BotDo("Command received", 
                        None)
          }


# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
lunchers = set() # People going to lunch

def append_user(lunchers, user):
    "Add"
    return lunchers.add(users)

def handle_command(**kwargs):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    command = kwargs['command']
    channel = kwargs['channel']
    user = kwargs['user']

    try: 
        bot_followup = next(v for k,v in dialogue.items() if command.find(k) >= 0) # Search for action words to find if the bot should do something
        if isinstance(bot_followup.response, list):
            response = choice(bot_followup.response)
        else:
            response = bot_followup.response
        print(str(datetime.now())+": Family Bot says, '{}'".format(response))
        
        # TODO: do bot follow up action
        print(str(datetime.now())+": Family Bot does - '{}'".format(bot_followup.action))
    except StopIteration:
        response = "Not sure what you mean. Try something else."

    slack_client.api_call("chat.postMessage",
                            channel=channel,
                            text=response, 
                            as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return {'user': output['user'],
                        'command': output['text'].split(AT_BOT)[1].strip().lower(),
                        'channel': output['channel']}
    return {"command": None, "channel":None}


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = .2 # Delay between reading from firehose
    if slack_client.rtm_connect():
        print(str(datetime.now())+": Family Bot connected and running!")
        while True:
            output = parse_slack_output(slack_client.rtm_read())
            if output['command'] and output['channel']:
                print(str(datetime.now())+str(output))
                handle_command(**output)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")