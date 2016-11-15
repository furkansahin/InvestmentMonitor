import sys
from copy import deepcopy
from threading import Thread

import requests
import time
import telepot
import psycopg2

conn_string = "port=9700"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
users = set()


def fetch_currency(sources, targets):
    result_dictionary = {}
    targets_serialize = ""
    url_base = "http://apilayer.net/api/live"
    access_key = "XXXXXX"

    #   fetch for sources 0, than we are going to calculate for ourselves
    source = sources[0]
    targets.extend(sources[1:])

    for target in targets:
        targets_serialize += target + ","
    targets_serialize = targets_serialize[:-1]
    url = url_base + "?access_key=" + access_key + "&source = " + str(
        source) + "& currencies=" + targets_serialize + "&format=1"

    response = requests.get(url)

    data = response.json()
    if data["success"]:

        for i in range(len(targets) - len(sources) + 1):
            result_dictionary[sources[0] + targets[i]] = data["quotes"][sources[0] + targets[i]]

        for i in range(1, len(sources)):
            for j in range(len(targets) - len(sources) + 1):
                result_dictionary[sources[i] + targets[j]] = (result_dictionary[sources[0] + targets[j]]) / \
                                                             data["quotes"][sources[0] + targets[j + len(sources) - 1]]
    return (result_dictionary)


def current_investment(from_arr, to_arr, investments):
    current_currencies = fetch_currency(from_arr, deepcopy(to_arr))
    sum_invest = 0.0
    index = 0
    for frm in from_arr:
        for to in to_arr:
            sum_invest += (current_currencies[frm + to] * float(investments[index]))
        index += 1
    print(sum_invest)
    return sum_invest


def storeUsers():
    bot = telepot.Bot('XXXXXX')
    response = bot.getUpdates()

    last_message_index = len(response)
    while True:
        response = bot.getUpdates()
        for message in response:
            chat_id = message['message']['chat']['id']

            sql = "INSERT INTO users VALUES('%s', ARRAY[\'USD\', \'EUR\'], \'TRY\',\'{1000,1000}\'::int[],6000,6500);"
            cursor.execute(sql, (chat_id,))
            conn.commit()


def notify(jackpot, sum_invest):
    bot = telepot.Bot('XXXXXX')
    response = bot.getUpdates()

    ##### response[len(response)-1]['message']['chat']['id']
    ##### len(response)-1 gives us the last user
    if jackpot:
        for user in users:
            bot.sendMessage(user, "hello! Your total investment value is " + str(sum_invest))
            #        bot.sendMessage((response[len(response)-1]['message']['chat']['id']),"hello! Your total investment value is " + str(sum_invest))
    else:
        for user in users:
            bot.sendMessage(user, "hello! Your total investment value is " + str(sum_invest))


# bot.sendMessage((response[len(response)-1]['message']['chat']['id']),"hello! Your total investment value is " + str(sum_invest))


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
    user_thread = Thread(target=storeUsers)
    user_thread.start()
#    sum_invest = current_investment(from_arr[1:], to_arr, investments)
 #   print(sum_invest)

    threshold_min = float(input("enter your min threshold: "))
    threshold_max = float(input("enter your max threshold: "))
    conn_string = "port=9700"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    while True:
        cursor.execute("SELECT user_id FROM users;")
        for i in cursor:
            users.add(i[0])

        sum_invest = current_investment(from_arr[1:], to_arr, investments)
        for i in range(360):

            if sum_invest <= threshold_min:
                notify(False, sum_invest)
            elif sum_invest >= threshold_max:
                notify(True, sum_invest)
            time.sleep(10)
            # time.sleep(3600)


if __name__ == "__main__":
    main()
