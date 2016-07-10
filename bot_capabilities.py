from collections import namedtuple

confirmation_messages = ["Okay.", 
                        "Got it!", 
                        "Okay-dookay", 
                        "Done.",
                        "Awesome!"]

BotDo = namedtuple("BotDo", ['response', 
                            'action'])

# The key is the trigger word; The value is a tuple of text responses and actions
bot_capabilities = {'test': BotDo("Command received", 
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