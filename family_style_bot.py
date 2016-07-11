"""Family Style Chat Bot: Group meal ordering made simple

Given a group of Slack users, order the best group meal for them.
"""

from datetime import datetime
import os
import pickle
from random import choice
import string
import sys
import time

from credentials import credentials
import pandas as pd
from slackclient import SlackClient
from slacker import Slacker

import bot_capabilities
bot_capabilities = reload(bot_capabilities)
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

def validate_eaters(eaters):
    "Only allow valid eaters to be eaters"
    valid_eaters = {'brian', 'eugene', 'anne', 'david', 'jon', 'marvin', 'leah', 'michelle', 'samatha'} 
    return {_ for _ in eaters if _ in valid_eaters}

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
            if user_id: # Given user ID, find user name and add to eaters"
                try:
                    r = slack.users.info(user_id)
                    first_name = r.body['user']['profile']['first_name'].lower()
                    eaters.add(first_name)
                    print(str(datetime.now())+": {} <--> '{}'".format(user_id, first_name))
                except:
                    print("ERROR: add someone to eaters")
            else:
                print("ERROR "+user_id)

            if isinstance(bot_followup.response, list): # Bot responding the conversation
                response = choice(bot_followup.response)
            else:
                response = bot_followup.response
        elif bot_followup.action == "add_person_to_eaters":
            l = command.split(" ")
            current_eater = l[l.index('add')+1]
            eaters.add(current_eater) # TODO: add logical to check that we have data
            print(eaters)
            if isinstance(bot_followup.response, list): # Bot responding the conversation
                response = choice(bot_followup.response)
            else:
                response = bot_followup.response
        elif bot_followup.action == "fit_model":
            # eaters |= set(command.split()[1:]) # parse command line args
            print(eaters)
            eaters = validate_eaters(eaters)
            eaters = [_.title() for _ in list(eaters)]
            print(eaters)
            try:
                results_raw = model.recommend(eaters)
                response = """Sounds good. Based on your group preferences here are my suggestions: 
    #1) {restaurant_1} (Resturant): {dishes_1}
    #2) {restaurant_2} (Resturant): {dishes_2}
    #3) {restaurant_3} (Resturant): {dishes_3}

    Should I order for y'all?
    """.format(restaurant_1=results_raw[0][0], dishes_1=" | ".join(results_raw[0][1]),
          restaurant_2=results_raw[1][0], dishes_2=" | ".join(results_raw[1][1]),
         restaurant_3=results_raw[2][0], dishes_3=" | ".join(results_raw[2][1])
          )
                eaters = set()
            except TypeError:
                print("Passed empty eater set")
                response = "I don't know who wants to eat. Please tell me who is hungry."
        else:
            if isinstance(bot_followup.response, list): # Bot responding the conversation
                response = choice(bot_followup.response)
            else:
                response = bot_followup.response

        # print(str(datetime.now())+": Family Bot does - '{   }'".format(bot_followup.action))
        # print(str(datetime.now())+": Family Bot says, '{}'".format(response))
        

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
                s = output['text'].split(AT_BOT)[1].strip().lower()
                exclude = set(string.punctuation)
                s = ''.join(ch for ch in s if ch not in exclude)
                return output['channel'], s, output['user'],
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = .01 # Delay between reading from firehose
    if slack_client.rtm_connect():
        print(str(datetime.now())+": Family Bot connected and running!")
        while True:
            channel, command, user_id = parse_slack_output(slack_client.rtm_read())
            if command and user_id and channel:
                handle_command(channel, command, user_id)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")