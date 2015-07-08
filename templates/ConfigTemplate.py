class Config:
    General = {
        # "owner_name": "[Owner name here]", # Required
        # "owners": [ { "stackexchange.com": User id here, "stackoverflow.com": User id here, "meta.stackexchange.com": User id here } ], # you can add multiple owners
        # "owners" is a required configuration value
        # "chatbot_name": "[Chatbot name here]", # Required
        # "email": "[Email of chatbot account]", # Optional
        # "password": "[Password of chatbot account]", # Optional, and NOT RECOMMENDED
        # "github": "[github repository link]", # Optional, https://github.com/ProgramFOX/SE-Chatbot as standard
        # "yandex_api_key: "API key" # Optional, API key for Yandex for the translation module
    }

    Configurations = {  # Optional, add configurations here
        # "ConfigurationNameHere": {
        #    "site": "<Site name> (without the `chat.` prefix)",
        #    "room": <room id>,
        #    "prefix": "<command prefix>" # Optional, standard: ">>"
        #    "privileged_users": same syntax as "owners" above. This configuration value is for users who can run privileged commands (such as `delete`).
        # }
    }
