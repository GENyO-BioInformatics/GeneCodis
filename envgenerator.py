import secrets
envs = {
    'prod':{
        "FLASK_HOST":"<>",
        "FLASK_DEBUG":"0",
        "API_URL":"<>",
        "WEB_FOLDER":"<>"
    },
    'preprod':{
        "FLASK_HOST":"<>",
        "FLASK_DEBUG":"<>",
        "API_URL":"<>",
        "WEB_FOLDER":"<>"
    },
    'laptop':{
        "FLASK_HOST":"<>",
        "FLASK_DEBUG":"<>",
        "API_URL":"<>",
        "WEB_FOLDER":"<>"
    },
    'workstation':{
        "FLASK_HOST":"<>",
        "FLASK_DEBUG":"<>",
        "API_URL":"<>",
        "WEB_FOLDER":"<>"
    },
    "common":{
        "FLASK_PORT":"<>",
        "TEMPLATE_FOLDER":"<>",
        "STATIC_URL_PATH":'<>',
        "STATIC_FOLDER":"<>",
        "SECRET_KEY":"<>"
    }
}

import sys
env = sys.argv[1]
# env = "workstation"
myenvs = [env,"common"]
private = open(".private").read()
with open(".env","w") as envHNDL:
    for env in myenvs:
        for var in envs[env]:
            envHNDL.write("{}={}\n".format(var,envs[env][var]))
    envHNDL.write(private)
