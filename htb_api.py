import requests
import json
import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup as bs
from player import Player

#################
CONFIGFILE = "config"
LOGLEVEL = 2  # 0 = no debug info, 1 = debug info, 2 = debug info with colors

MAX_CHALLENGES = 10
EXTRA_SYSTEM_DIFFICULTY = 5
MAX_OPTIONS = 5
#################

log_OK = 0
log_INFO = 1
log_ERROR = 2
log_HEADING = 3
log_NULL = 4


class cli_colors:
    header = "\033[95m"
    blue = "\033[94m"
    green = "\033[92m"
    warning = "\033[93m"
    fail = "\033[91m"
    endc = "\033[0m"
    bold = "\033[1m"
    underline = "\033[4m"


class HTBAPI(object):
    def __init__(self, credentials="config", loglevel=2):
        self.credentials = credentials
        self.loglevel = loglevel
        self.cfg = self.config()

    def init(self):
        self.s = self.login()

    def config(self):
        try:
            cfg = json.loads(open(self.credentials, "r").read())
            api = cfg["api"]
            self.userid = int(api["userid"])
            self.username = str(api["username"])
            self.password = str(api["password"])
            self.email = str(api["email"])
            search = cfg["search"]
            self.searchuserid = search["userid"]
            self.searchusername = search["username"]

            self.searchprofileurl = (
                "https://www.hackthebox.eu/home/users/profile/" + str(self.searchuserid)
            )
            return cfg
        except:
            self.log(self.credentials + " not found", log_ERROR)

    def log(self, msg, log_type=4):
        msg = self.html_unescape(msg)
        if log_type == 4:
            print(msg)
        elif log_type == 3:
            if self.loglevel == 2:
                print(
                    cli_colors.bold
                    + cli_colors.green
                    + "----------"
                    + str(msg)
                    + "----------"
                    + cli_colors.endc
                )
            elif self.loglevel == 1:
                print("----------" + str(msg) + "----------")
            else:
                return
        elif log_type == 2:
            if self.loglevel == 2:
                print(cli_colors.fail + "[-] " + cli_colors.endc + str(msg))
            else:
                print("[-] " + str(msg))
        elif log_type == 1:
            if self.loglevel == 2:
                print(cli_colors.blue + "[*] " + cli_colors.endc + str(msg))
            elif self.loglevel == 1:
                print("[*] " + str(msg))
            else:
                return
        elif log_type == 0:
            if self.loglevel == 2:
                print(cli_colors.green + "[+] " + cli_colors.endc + str(msg))
            elif self.loglevel == 1:
                print("[+] " + str(msg))
            else:
                return

    def html_unescape(self, s):
        return HTMLParser().unescape(s)

    def login(self):
        s = requests.Session()
        r = s.get("https://www.hackthebox.eu/login")  # get csrf-token
        csrf_token = (
            re.findall('_token".* value=".*"', str(r.content))[0]
            .split('value="')[1]
            .split('">')[0]
        )
        data = {"_token": csrf_token, "email": self.email, "password": self.password}
        r = s.post("https://www.hackthebox.eu/login", data=data)
        if (
            not r.status_code == 200
            or not s.get(self.searchprofileurl).status_code == 200
        ):
            self.log("Login failed", log_ERROR)
            exit(-1)
        else:
            self.log("Login Successful", log_OK)
            return s

    def parseprofile(self, userid):
        self.log("Parsing profile", log_INFO)
        s = self.s
        r = s.get("https://www.hackthebox.eu/home/users/profile/" + str(userid))
        if not r.status_code == 200:
            self.log("Error while trying to parse the profile", log_ERROR)
        soup = bs(r.content, "html.parser")
        profile = soup.find_all("div", class_="header-title")[0].text
        profile = profile.split(" ")
        for i in profile:
            if i == " " or i == "":
                profile.remove(i)
        nickname = profile[0]
        points = profile[1]
        ownedsystems = profile[2]
        ownedusers = profile[3]
        rank = profile[5] + " " + profile[6]

        last_activity = soup.find_all("div", class_="vertical-timeline-content")[0]
        last_div = str(last_activity).split(" ")
        last_car = []
        if last_div[15] == "root" or last_div[15] == "user":
            last_car.append(
                last_div[13]
                + " "
                + last_div[14]
                + " "
                + last_div[15]
                + " "
                + "at"
                + " "
                + last_div[23].split(">")[1].split("<")[0]
            )
        last_activity = soup.find_all("div", class_="vertical-timeline-content")[1]
        prev_div = str(last_activity).split(" ")
        prev_car = []
        if prev_div[15] == "root" or "user":
            prev_car.append(
                prev_div[13]
                + " "
                + prev_div[14]
                + " "
                + prev_div[15]
                + " "
                + "at"
                + " "
                + prev_div[23].split(">")[1].split("<")[0]
            )
        player = Player(
            nickname, points, ownedusers, ownedsystems, rank, last_car, prev_car
        )
        return player
