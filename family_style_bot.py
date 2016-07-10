"""Family Style Chat Bot: Group meal ordering made simple

Given a group of Slack users, order the best group meal for them.
"""

from datetime import datetime
import os
import pickle
from random import choice
import sys
import time

from credentials import credentials
import pandas as pd
from slackclient import SlackClient
from slacker import Slacker

from bot_capabilities import bot_capabilities
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

# Load recommendation engine data
data_cuisine = pickle.load(open("data/user_by_cuisine_ratings.pkl", 'rb'))
df_cuisine = pd.DataFrame(data_cuisine)
data_items = pickle.load(open("data/user_by_cuisine_by_dish_ratings.pkl", 'rb'))
model = GroupRecommender(df_cuisine, data_items)

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
        bot_followup = next(v for k,v in bot_capabilities.items() if command.find(k) >= 0) 
        
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

            if isinstance(bot_followup.response, list): # Bot responding the conversation
                response = choice(bot_followup.response)
            else:
                response = bot_followup.response
        elif bot_followup.action == "add_person_to_eaters":
            eaters.add(command.split(" ")[1]) # TODO: add logical to check for chat room membership

            if isinstance(bot_followup.response, list): # Bot responding the conversation
                response = choice(bot_followup.response)
            else:
                response = bot_followup.response
        elif bot_followup.action == "fit_model":
            eaters |= set(command.split()[1:])
            eaters = [_.title() for _ in list(eaters)]
            result = model.recommend(eaters)
            response = result # Bot responding the conversation
            eaters = set()

        print(str(datetime.now())+": Family Bot does - '{}'".format(bot_followup.action))
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