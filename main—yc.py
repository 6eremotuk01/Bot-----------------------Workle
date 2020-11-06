#############################################
#          Настройки для работы             #
#        (обязательные параметры)           #
#############################################

# JETBRAINS_ORGANIZATION_DOMAIN_NAME —      #
# доменное имя организации JetBrains Space  #
JETBRAINS_ORGANIZATION_DOMAIN_NAME = ""

# JETBRAINS_CLIENT_ID — идентификатор бота, #
# который будет отправлять сообщения        #
# JETBRAINS_CLIENT_SECRET — секретный ключ  #
# бота                                      #
JETBRAINS_CLIENT_ID = ""
JETBRAINS_CLIENT_SECRET = ""

#############################################
#       Настройки чата и упоминаний         #
#############################################
# Для того, чтобы направлять чат по его     #
# имени, то используйте переменнную         #
# CHAT_NAME, но при этом чат id должен      #
# быть пустым                               #
CHAT_NAME = ""

# Если вы хотиете использовать id чата,     #
# для отправки сообщений, то используйте    #
# переременную CHAT_ID                      #
CHAT_ID = ""

# Чтобы уведомление пришло для конкретного  #
# пользователя, то укажите его username в   #
# переменной MENTION_USER_ID. И при         #
# отправке сообщения к нему будет           #
# добавлено упоминание @username            #
MENTION_USER_ID = ""

#############################################

import requests
import json
import base64
import re

JETBRAINS_API_TOKEN = ""
REQUEST_HEADERS = {
    'Authorization': "Bearer {0}".format(JETBRAINS_API_TOKEN),
    'Accept': 'application/json',
}


def getAccessToken():
    global JETBRAINS_ORGANIZATION_DOMAIN_NAME
    global JETBRAINS_CLIENT_ID
    global JETBRAINS_CLIENT_SECRET

    authorizationString = JETBRAINS_CLIENT_ID + ":" + JETBRAINS_CLIENT_SECRET
    bytesString = authorizationString.encode('ascii')
    base64String = base64.b64encode(bytesString).decode('ascii')

    query = "https://{0}.jetbrains.space/oauth/token".format(
        JETBRAINS_ORGANIZATION_DOMAIN_NAME)
    response = requests.post(
        query,
        data={
            'grant_type': 'client_credentials',
        },
        headers={'Authorization': 'Basic ' + base64String})

    return json.loads(response.text)['access_token']


def getChannelsInfo(nameOfChannel=""):
    global JETBRAINS_ORGANIZATION_DOMAIN_NAME
    global REQUEST_HEADERS

    query = "https://{0}.jetbrains.space/api/http/chats/channels/all-channels?query={1}".format(
        JETBRAINS_ORGANIZATION_DOMAIN_NAME, nameOfChannel)

    response = requests.get(query, headers=REQUEST_HEADERS)
    return json.loads(response.text)


def sendMessage(channelId, message):
    if (not channelId):
        return

    global JETBRAINS_ORGANIZATION_DOMAIN_NAME
    global REQUEST_HEADERS

    query = "https://{0}.jetbrains.space/api/http/chats/channels/{1}/messages".format(
        JETBRAINS_ORGANIZATION_DOMAIN_NAME, channelId)

    dataToSend = {"text": message}
    response = requests.post(query, headers=REQUEST_HEADERS, json=dataToSend)

    return json.loads(response.text)


def setInfo():
    global JETBRAINS_API_TOKEN
    JETBRAINS_API_TOKEN = getAccessToken()

    global REQUEST_HEADERS
    REQUEST_HEADERS['Authorization'] = "Bearer {0}".format(JETBRAINS_API_TOKEN)

    global CHAT_NAME
    global CHAT_ID
    if (CHAT_ID == ""):
        CHAT_ID = getChannelsInfo(CHAT_NAME)['data'][0]['channelId']


#############################################
#                 Точка входа               #
#############################################


def doPost(event, context):
    setInfo()

    global CHAT_ID
    global MENTION_USER_ID
    base64_message = event['body']
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')

    jsonedData = json.loads(message)

    message = re.sub(r"(\n)|(<br>)", r"\n>", jsonedData['text'])

    if (MENTION_USER_ID):
        message += "\n\n@" + MENTION_USER_ID

    sendMessage(CHAT_ID, message)
    return json.dumps({"result": "ok"})