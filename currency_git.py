import sys
import requests
import json
from copy import deepcopy


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

    currencies = fetch_currency(from_arr[1:], deepcopy(to_arr))

    sum = 0.0
    for frm in from_arr[1:]:
        for to in to_arr:
            sum += (currencies[frm + to] * float(sys.argv[index]))
        index += 1

    print sum


if __name__ == "__main__":
    main()
