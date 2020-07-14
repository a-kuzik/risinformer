#!/usr/bin/env python3
# coding: utf-8

import socket
import time
import re
import json
import yaml

with open("config.yaml") as file:
    config = yaml.load(file)

asns = config["asns"]
irr = config["irr"]


class IrrQuery:
    def __init__(self, irr):
        self.irr = irr

    def recv_timeout(self, the_socket, timeout=2):
        the_socket.setblocking(0)
        total_data = []
        data = ""
        begin = time.time()
        while 1:
            if total_data and time.time() - begin > timeout:
                break
            elif time.time() - begin > timeout * 2:
                break
            try:
                data = the_socket.recv(8192).decode()
                if data:
                    total_data.append(data)
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        text = "".join(total_data)
        return text

    def connect_whois(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("whois.{}.net".format(self.irr), 43))
        self.s = s

    def request_whois(self, obj, query):
        self.s.send((query.format(obj)).encode())
        return self.s

    def parse_irr_out(self, text_data):
        summ_j = {}
        regex4 = (
            "route:\s+(?P<route>[\d.]+/\d.)[\n]+"
            "origin:\s+AS(?P<origin>\d+)[\n]+"
            "|route6:\s+(?P<route6>[\w+:]+/\d.)[\n]+"
            "origin:\s+AS(?P<origin6>\w+)"
        )
        route = re.finditer(regex4, text_data)
        for a in route:
            origin, route, origin6, route6 = a.group(
                "origin", "route", "origin6", "route6"
            )
            if origin or route != None:
                summ_j[route] = []
                summ_j[route].append(origin)
            elif origin6 or route6 != None:
                summ_j[route6] = []
                summ_j[route6].append(origin6)
        return summ_j


radb_query = "!!\r\n -K -i origin AS{} \r\n"
ripe_query = "-i origin -k AS{} -K\n"
radb_moas = "!!\r\n -K {} \r\n"
ripe_moas = "-k -K {} \n"

w = IrrQuery(irr)
w.connect_whois()
dct = {}


def parse_obj(asns, dct, query):
    for obj in asns:
        t = w.recv_timeout(w.request_whois(obj, query))
        dct.update(w.parse_irr_out(t))
    return dct


def parse_moas(dct, query):
    for k, v in dct.items():
        z = w.recv_timeout(w.request_whois(k, query))
        x = w.parse_irr_out(z)
        for ke, va in x.items():
            if ke == k:
                if va[0] not in v:
                    v.append(va[0])
    return dct


if irr == "ripe":
    parse_obj(asns, dct, ripe_query)
    parse_moas(dct, ripe_moas)
if irr == "radb":
    parse_obj(asns, dct, radb_query)
    parse_moas(dct, radb_moas)

# print(dct)
with open("prefixes.json", "w") as json_file:
    json.dump(dct, json_file)
