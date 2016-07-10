from collections import namedtuple

confirmation_messages = ["Okay.", 
                        "Got it!", 
                        "Okay-dookay", 
                        "Done.",
                        "Awesome!",
                        "Sweet!",
                        "Can do."]

init_convo_messages = ["Who wants nom noms?",
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
            'dinner': BotDo(init_convo_messages,
                            None),
            'nevermind': BotDo(confirmation_messages,
                            'remove_person_from_eaters'),
            'different': BotDo(confirmation_messages,
                            'generate_new_recommandations'),
            'weather': BotDo(["It's always foggy in San Fransisco"],
                            None),
            'sandwich': BotDo(["Sorry :( I don't have arms!"],
                            None),
            'add': BotDo(confirmation_messages, 
                            "add_person_to_eaters"),
            'favorite': BotDo(['Beer!', 'I could always go for pizza!'],
                            None),
            'suggest': BotDo(["Sounds good. Based on your group preferences here are my suggestions: ..."], 
                            "fit_model"), # pass in list of users as arguments
            'order': BotDo("Okay. I have ordered that for you. Here is the tracking number #867-5309. I'll keep you posted and let you know when it arrives.",
                            None),
}