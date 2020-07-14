import json
import time
import sys
import yaml
import requests
from parseris import *
from worker import *

g = ReadConf(f1)
conf = g.read_conf()
url = "https://ris-live.ripe.net/v1/stream/?format=json&client=test101"


def stream():
    hijack_count = 0
    leak_count = 0
    wr_announce_cnt = 0
    timer = Timer()
    while True:
        s = requests.Session()
        r = s.get(url, stream=True)
        print(r.status_code)
        if r.status_code == 200:
            try:
                for line in r.iter_lines():
                    if line:
                        parsed = json.loads(line)
                        elm = ParseRis(parsed)
                        elm.ris_data_full()
                        t = ToDo(g, elm)
                        t.upl_updates()
                        t.new_announces()
                        t.withdrawals()
                        if t.route_leak():
                            leak_count += 1
                            print("Route Leak: ", leak_count)
                            if leak_count >= 2:
                                if timer.get_time() >= 120:
                                    t.tlg_leak()
                                    t.slack_leak()
                                    t.mail_leak()
                                    leak_count = 0
                                    timer.restart()

                        if t.ishijack():
                            hijack_count += 1
                            print("Hijack: ", hijack_count)
                            if hijack_count >= 2:
                                if timer.get_time() >= 120:
                                    t.tlg_ishijack()
                                    t.slack_ishijack()
                                    t.mail_ishijack()
                                    hijack_count = 0
                                    timer.restart()

                        if t.wrong_announce():
                            wr_announce_cnt += 1
                            print("Wrong announce: ", wr_announce_cnt)
                            if wr_announce_cnt >= 2:
                                if timer.get_time() >= 120:
                                    t.tlg_wrong_announce()
                                    t.slack_wrong_announce()
                                    t.mail_wrong_announce()
                                    wr_announce_cnt = 0
                                    timer.restart()

            except requests.exceptions.RequestException as err:
                print("OOps: Something Else", err)
                time.sleep(10)
            except requests.exceptions.HTTPError as errh:
                print("Http Error:", errh)
                time.sleep(10)
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
                time.sleep(10)
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
                time.sleep(10)
            except KeyboardInterrupt:
                print("User stop requested")
                sys.exit()


stream()
