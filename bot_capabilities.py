from collections import namedtuple

confirmation_messages = ["Okay.", 
                        "Got it!", 
                        "Okay-dookay", 
                        "Done.",
                        "Awesome!"]

init_convo_messages = ["Did someone say lunch!?",
                     "Who's hungry?!",
                     "Sounds like someone's hungry! Who's in?"]

BotDo = namedtuple("BotDo", ['response', 
                            'action'])

# The key is the trigger word; The value is a tuple of text responses and actions
bot_capabilities = {'test': BotDo("Command received", 
                            None),
            'me': BotDo(confirmation_messages,
                            "add_self_to_eaters"),
            'lunch': BotDo(init_convo_messages,
                            None),
            'nevermind': BotDo(confirmation_messages,
                            'remove_person_from_eaters'),
            'different': BotDo(confirmation_messages,
                            'generate_new_recommandations'),
            'weather': BotDo(["It's always foggy in San Fransisco"],
                            None),
            'sandwich': BotDo(["Sorry :( I don't have arms!"],
                            None)
            'add_person': BotDo(confirmation_messages, 
                            "add_person_to_eaters"),
            'whats_your_favorite': BotDo(['Beer!', 'I could always go for pizza!'],
                            None)
            'go': BotDo(["Sounds good. Based on your group preferences here are my suggestions: ..."], 
                            "fit_model") # pass in list of users as arguments
            }

          #   'fit_model_current_eaters': BotDo(["Sounds good. Based on your group preferences here are my suggestions: ..."], 
          #                   "TODO: add fit model logic"),
          #   'order': BotDo("Okay. I have ordered the perfect meal for you. Here is the tracking number #867-5309. I'll keep you posted and let you when it arrives.",
          #                   "TODO: add order logic"),

          # }