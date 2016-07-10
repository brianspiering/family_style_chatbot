"""Family Style Chat Bot: Group meal ordering made simple

Given a group of Slack users, order the best group meal for them.
"""

from collections import namedtuple
from datetime import datetime
import os
import pickle
from random import choice
import sys
import time

from credentials import credentials
from slackclient import SlackClient
from slacker import Slacker

from group_recommender import GroupRecommender   

slack_bot_token, bot_id = credentials.require(['slack_bot_token', 'bot_id'])
slack = Slacker(slack_bot_token)
try: 
    r = slack.api.test()
    assert r.successful == True
except:
    print("Check your tokens!")
    sys.exit(1)

AT_BOT = "<@" + str(bot_id) + ">:"

confirmation_messages = ["Okay.", "Got it!", "Okay-dookay", "I added you to the group", "Awesome"]

# Load recommendation engine data
data_items = pickle.load(open('data/user_by_cuisine_by_dish_ratings.pkl', 'rb'))
data_cuisine = pickle.load(open("data/user_by_cuisine_ratings.pkl", 'rb'))
model = GroupRecommender(data_items, data_cuisine)

BotDo = namedtuple("BotDo", ['response', 
                            'action'])
dialogue = {'test': BotDo("Command received", 
                            None),
            'add_me': BotDo(confirmation_messages,
                            "add_self_to_eaters"),
            'add_person': BotDo(confirmation_messages, 
                            "add_person_to_eaters"),
            'fit_model': BotDo(["Sounds good. Based on your group preferences here are my suggestions: ..."], 
                            "fit_model") # pass in list of users as arguments
            }

          #   'fit_model_current_eaters': BotDo(["Sounds good. Based on your group preferences here are my suggestions: ..."], 
          #                   "TODO: add fit model logic"),
          #   'order': BotDo("Okay. I have ordered the perfect meal for you. Here is the tracking number #867-5309. I'll keep you posted and let you when it arrives.",
          #                   "TODO: add order logic"),

          # }

# instantiate Slack client
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient(slack_bot_token)
eaters = set() # People going to lunch

def handle_command(channel, command, user_id):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    global eaters

    print(command, user_id)

    try: 
        # Search for action words to find if the bot should do something
        bot_followup = next(v for k,v in dialogue.items() if command.find(k) >= 0) 
        
        # Bot doing an action behind the scenes of the conversation
        # print(str(datetime.now())+": Family Bot does - '{}'".format(bot_followup.action))
        if bot_followup.action == "add_self_to_eaters": # TODO: make this an eval function
            user_id = user_id
            if user_id: # Given user ID, find user name and add to eaters"
                try:
                    r = slack.users.info(user_id)
                    user_real_name = r.body['user']['real_name'].lower()
                    eaters.add(user_real_name)
                    print(str(datetime.now())+": {} <--> '{}'".format(user_id, user_real_name))
                except:
                    print("ERROR: add someone to eaters")
            else:
                print("ERROR "+user_id)
        elif bot_followup.action == "add_person_to_eaters":
            eaters.add(command.split(" ")[1]) # TODO: add logical to check for chat room membership
        elif bot_followup.action == "fit_model":
            eaters |= set(command.split()[1:])

        print(str(datetime.now())+": Family Bot does - '{}'".format(bot_followup.action))
        
        # Bot responding the conversation
        if isinstance(bot_followup.response, list):
            response = choice(bot_followup.response)
        else:
            response = bot_followup.response
        print(str(datetime.now())+": Family Bot says, '{}'".format(response))
        

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

        Then returns (command, user_id)
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['channel'], output['text'].split(AT_BOT)[1].strip().lower(), output['user'],
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = .2 # Delay between reading from firehose
    if slack_client.rtm_connect():
        print(str(datetime.now())+": Family Bot connected and running!")
        while True:
            channel, command, user_id = parse_slack_output(slack_client.rtm_read())
            if command and user_id and channel:
                handle_command(channel, command, user_id)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")