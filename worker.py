import yaml
import socket
import json
import time
from parseris import *
from slack import *
from telegram import *
from sendmail import *

f1 = "config.yaml"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 6000))


def read_json(file):
    with open(file) as json_file:
        data = json.load(json_file)
        return data


class ReadConf:
    def __init__(self, conf):
        self.conf = conf

    def read_conf(self):
        with open(self.conf, "r") as file:
            elem = yaml.load(file)
            self.elem = elem
            return self.elem

    def asns(self):
        asns = self.elem["asns"]
        return asns

    def main_asn(self):
        main_asn = self.elem["main_asn"]
        return main_asn

    def debug(self):
        debug = self.elem["debug"]
        return debug

    def uplinks(self):
        uplinks = self.elem["uplinks"]
        return uplinks

    def collector(self):
        if self.elem["logstash"]["enable"] == True:
            state = True
            host = self.elem["logstash"]["host"]
            port = self.elem["logstash"]["port"]
            return state, host, port

    def mail(self):
        mail = self.elem["email"]
        return mail

    def min_hosts(self):
        min_hosts = self.elem["min_hosts"]
        return min_hosts

    def slack(self):
        if self.elem["slack"]["enable"] == True:
            state = True
            url = self.elem["slack"]["url"]
            return state, url

    def telegram(self):
        if self.elem["telegram"]["enable"] == True:
            state = True
            token = self.elem["telegram"]["token"]
            chat_id = self.elem["telegram"]["chat_id"]
            return state, token, chat_id


class ToDo:
    def __init__(self, argcfg, argdata):
        self.argcfg = argcfg
        self.argdata = argdata

    def udpsock(self, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 6005))
        sock.sendto(
            json.dumps(msg).encode("utf-8"),
            (self.argcfg.collector()[1], self.argcfg.collector()[2]),
        )

    def todo(self, data):
        try:
            if self.argcfg.debug() == True:
                print(data)
            if self.argcfg.collector()[0] == True:
                self.udpsock(data)
        except Exception as err:
            print(err)

    def slck(self, text, raw):
        try:
            if self.argcfg.slack()[0] == True:
                sl = Slack(url=self.argcfg.slack()[1])
                text = (
                    50 * "*"
                    + "\n"
                    + text
                    + "\n"
                    + 50 * "-"
                    + "\nRaw data is below:\n"
                    + str(raw)
                )
                sl.post(text=text)
        except Exception as err:
            print(err)

    def tlgm(self, data, raw):
        try:
            if self.argcfg.telegram()[0] == True:
                tlg = BotHandler(self.argcfg.telegram()[1])
                data = (
                    50 * "*"
                    + "\n"
                    + data
                    + "\n"
                    + 50 * "-"
                    + "\nRaw data is below:\n"
                    + str(raw)
                )
                tlg.send_message(self.argcfg.telegram()[2], data)
        except Exception as err:
            print(err)

    def email(self, data, raw):
        sender = "bgp@gmail.com"
        receiver = self.argcfg.mail()
        subject = "BGP Notice"
        body = (
            50 * "*"
            + "\n"
            + data
            + "\n"
            + 50 * "-"
            + "\nRaw data is below:\n"
            + str(raw)
        )
        try:
            email = Email(sender, receiver, subject, body)
            email.sendmail()

        except Exception as err:
            print(err)

    def upl_updates(self):
        upl_updates = {}
        for k, v in self.argcfg.uplinks().items():
            for asn in self.argcfg.asns():
                try:
                    if int(asn) in self.argdata.path():
                        if (
                            int(v)
                            == self.argdata.path()[
                                self.argdata.path().index(int(asn)) - 1
                            ]
                        ):
                            upl_updates.update(
                                {
                                    "upl_update": {
                                        "time": self.argdata.timestamp(),
                                        "host": self.argdata.host(),
                                        "uplink": k,
                                        "path": self.argdata.path(),
                                        "prefixes": self.argdata.prefixes(),
                                    }
                                }
                            )
                            self.todo(upl_updates)
                            text = "{} - New update for prefixes {} via {}".format(
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(self.argdata.timestamp()),
                                ),
                                self.argdata.prefixes(),
                                k,
                            )
                except Exception as err:
                    pass

    def new_announces(self):
        new_announces = {}
        for asn in self.argcfg.asns():
            try:
                if int(asn) == self.argdata.path()[-1]:
                    new_announces.update(
                        {
                            "new_announces": {
                                "time": self.argdata.timestamp(),
                                "asn": asn,
                                "host": self.argdata.host(),
                                "path": self.argdata.path(),
                                "prefixes": self.argdata.prefixes(),
                            }
                        }
                    )
                    text = "{} - New announce for prefix {} with origin {}.".format(
                        time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(self.argdata.timestamp()),
                        ),
                        self.argdata.prefixes(),
                        asn,
                    )
                    self.todo(new_announces)
            except Exception as err:
                pass

    def wrong_announce(self):
        wrong_announce = {}
        try:
            for asn in self.argcfg.asns():
                if int(asn) == self.argdata.path()[-1]:
                    for prfx in self.argdata.prefixes():
                        if prfx not in read_json("prefixes.json").keys():
                            wrong_announce.update(
                                {
                                    "wrong_announce": {
                                        "time": self.argdata.timestamp(),
                                        "asn": asn,
                                        "host": self.argdata.host(),
                                        "path": self.argdata.path(),
                                        "prefixes": prfx,
                                    }
                                }
                            )
                            text = "{} - Wrong announce for prefix {} with origin {}.".format(
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(self.argdata.timestamp()),
                                ),
                                prfx,
                                asn,
                            )
                            self.text = text
                            self.wrong_announce = wrong_announce
                            self.todo(wrong_announce)
                            return wrong_announce, text

        except Exception as err:
            pass

    def route_leak(self):
        route_leak = {}
        for k, v in self.argcfg.uplinks().items():
            for asn in self.argcfg.asns():
                try:
                    if int(asn) in self.argdata.path():
                        if (
                            int(v)
                            == self.argdata.path()[
                                self.argdata.path().index(int(asn)) + 1
                            ]
                        ):
                            uplink = self.argdata.path()[
                                self.argdata.path().index(int(asn)) - 1
                            ]
                            route_leak.update(
                                {
                                    "route_leak": {
                                        "time": self.argdata.timestamp(),
                                        "host": self.argdata.host(),
                                        "uplink": uplink,
                                        "path": self.argdata.path(),
                                        "prefixes": self.argdata.prefixes(),
                                    }
                                }
                            )
                            text = "{} - It seems like route leak was occurred for prefix {}.".format(
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(self.argdata.timestamp()),
                                ),
                                self.argdata.prefixes(),
                            )
                            self.route_leak = route_leak
                            self.text = text
                            self.todo(route_leak)
                            return route_leak, text
                except Exception as err:
                    pass

    def withdrawals(self):
        withdrawals = {}
        if self.argdata.withdrawals() != None:
            for prfx in self.argdata.withdrawals():
                if prfx in read_json("prefixes.json").keys():
                    withdrawals.update(
                        {
                            "withdrawals": {
                                "time": self.argdata.timestamp(),
                                "host": self.argdata.host(),
                                "prefixes": prfx,
                            }
                        }
                    )
                    text = "{} - Withdrawals for prefix {}.".format(
                        time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(self.argdata.timestamp()),
                        ),
                        prfx,
                    )
                    self.todo(withdrawals)

    def ishijack(self):
        ishijack = {}
        try:
            for p, a in read_json("prefixes.json").items():
                if p in self.argdata.prefixes():
                    for asn in a:
                        if int(asn) != self.argdata.path()[-1]:
                            ishijack.update(
                                {
                                    "ishijack": {
                                        "time": self.argdata.timestamp(),
                                        "asn": asn,
                                        "hijacckedasn": self.argdata.path()[-1],
                                        "host": self.argdata.host(),
                                        "prefixes": p,
                                    }
                                }
                            )
                            text = "{} - It seems like BGP hijack was occurred for prefix {},\
                                where the right origin is {} and wrong origin is {}".format(
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(self.argdata.timestamp()),
                                ),
                                p,
                                asn,
                                self.argdata.path()[-1],
                            )
                            self.text = text
                            self.ishijack = ishijack
                            self.todo(ishijack)
                            return ishijack, text

        except Exception as err:
            pass

    def tlg_ishijack(self):
        self.tlgm(self.text, self.ishijack)

    def tlg_leak(self):
        self.tlgm(self.text, self.route_leak)

    def tlg_wrong_announce(self):
        self.tlgm(self.text, self.wrong_announce)

    def slack_ishijack(self):
        self.slck(self.text, self.ishijack)

    def slack_leak(self):
        self.slck(self.text, self.route_leak)

    def slack_wrong_announce(self):
        self.slck(self.text, self.wrong_announce)

    def mail_ishijack(self):
        self.email(self.text, self.ishijack)

    def mail_leak(self):
        self.email(self.text, self.route_leak)

    def mail_wrong_announce(self):
        self.email(self.text, self.wrong_announce)


class Timer:
    def __init__(self):
        self.start = time.time()

    def restart(self):
        self.start = time.time()

    def get_time(self):
        end = time.time()
        elapsed = end - self.start
        return elapsed
