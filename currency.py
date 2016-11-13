import sys
import json
from copy import deepcopy
import requests
import httplib, urllib
import time

def fetch_currency(sources, targets):
    result_dictionary = {}
    targets_serialize = ""
    url_base = "http://apilayer.net/api/live"
    access_key = "XXXXXXXXXXXXXXXX"

    #   fetch for sources 0, than we are going to calculate for ourselves
    source = sources[0]
    targets.extend(sources[1:])

    for target in targets:
        targets_serialize += target + ","
    targets_serialize = targets_serialize[:-1]
    url = url_base + "?access_key=" + access_key + "&source = " + str(
        source) + "& currencies=" + targets_serialize + "&format=1"

    data = json.loads(requests.get(url).content)

    if data["success"]:

        for i in xrange(len(targets) - len(sources) + 1):
            result_dictionary[sources[0] + targets[i]] = data["quotes"][sources[0] + targets[i]]

        for i in xrange(1, len(sources)):
            for j in xrange(len(targets) - len(sources) + 1):
                result_dictionary[sources[i] + targets[j]] = (result_dictionary[sources[0] + targets[j]]) / \
                                                             data["quotes"][sources[0] + targets[j + len(sources) - 1]]
    return result_dictionary


def current_investment(from_arr, to_arr, investments):
    current_currencies = fetch_currency(from_arr, deepcopy(to_arr))
    sum_invest = 0.0
    index = 0
    for frm in from_arr:
        for to in to_arr:
            sum_invest += (current_currencies[frm + to] * float(investments[index]))
        index += 1

    return sum_invest


def notify(bool):
    api_token = "XXXXXXXXXXXXXXXX"
    user_key = "XXXXXXXXXXXXXXXX"

    conn = httplib.HTTPSConnection("api.pushover.net:443")
    if bool:
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode({
                         "token": api_token,
                         "user": user_key,
                         "message": "Wanna buy a car u faggot?",
                     }), {"Content-type": "application/x-www-form-urlencoded"})
    else:
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode({
                         "token": api_token,
                         "user": user_key,
                         "message": "U poor bastard! Watch out your money.",
                     }), {"Content-type": "application/x-www-form-urlencoded"})

    return conn.getresponse()


def main():
    from_arr = []
    to_arr = []

    to = False
    index = 1
    for arg in sys.argv:
        index += 1
        if arg == "to":
            to = True
            continue
        elif arg == "done":
            index -= 1
            break

        if to:
            to_arr.append(arg)
        else:
            from_arr.append(arg)

    investments = []
    for investment in sys.argv[index:]:
        investments.append(investment)

    sum_invest = current_investment(from_arr[1:], to_arr, investments)
    print sum_invest

    threshold_min = float(raw_input("enter your min threshold: "))
    threshold_max = float(raw_input("enter your max threshold: "))

    while True:
        sum_invest = current_investment(from_arr[1:], to_arr, investments)
        if sum_invest <= threshold_min:
            notify(False)
        elif sum_invest >= threshold_max:
            notify(True)
        time.sleep(60)


if __name__ == "__main__":
    main()
