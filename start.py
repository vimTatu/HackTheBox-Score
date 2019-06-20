from settings import userIDs
from htb_api import HTBAPI
from db_connect import add_item, get_players_stats
from hangouts import send_message, latest_updates
from time import sleep
from terminaltables import AsciiTable

htbApi = HTBAPI()
htbApi.init()


def main():
    for id in userIDs:
        try:
            player = htbApi.parseprofile(id)
            last = add_item(player)
            if last == True:
                table = get_players_stats()
                thread = send_message(table)
                latest_updates(thread=thread, text="New user joined! {}".format(id))
            elif last != False:
                table = get_players_stats()
                thread = send_message(table)
                latest_updates(thread, last.replace('[','').replace(']','').replace('\'', ''))
            get_players_stats()
        except:
            pass

if __name__ == "__main__":
    while True:
        main()
