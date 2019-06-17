from httplib2 import Http
from json import dumps, loads
from settings import hook


def send_message(table):
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    message = {"text": "*Hack The Box scores*\n```" + table.table + "```"}
    http_obj = Http()
    response = http_obj.request(
        uri=hook, method="POST", headers=message_headers, body=dumps(message)
    )
    if response[0]["status"] == "200":
        return loads(response[1])["thread"]["name"]


def latest_updates(thread, text):
    bot_message = {"text": "*{}*".format(text)}
    bot_message["thread"] = {"name": thread}
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}

    http_obj = Http()

    response = http_obj.request(
        uri=hook, method="POST", headers=message_headers, body=dumps(bot_message)
    )
    if response[0]["status"] == "200":
        return True
