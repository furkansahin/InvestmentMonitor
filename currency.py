from copy import deepcopy
import requests
import time
import telepot

users = {}
token = raw_input('token:')
bot = telepot.Bot(token)
currencies = {"USD", "TRY", "GBP", "CHF", "JPY", "EUR"}
currencies_in_usage = set()


def fetch_currency():
    url = "http://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json"

    response = requests.get(url)

    data = response.json()

    cur_values = {}
    if data:
        for cur in currencies_in_usage:
            if cur is not "USD":
                cur_values["USD/" + cur] = 0

        for resource in data["list"]["resources"]:
            if str(resource['resource']['fields']['name']) in cur_values:
                cur_values[str(resource['resource']['fields']['name'])] = float(resource['resource']['fields']["price"])

    cur_values["USD/USD"] = 1
    return cur_values


def current_investment(cur_values, money, to_cur):
    sum_investment = 0.0

    for mon in money:
        sum_investment += (cur_values["USD/" + to_cur] / cur_values["USD/" + mon]) * money[mon]

    return sum_investment


def send_message(msg_type, user, name, money=" ", user_dict={}):
    msg = ""

    if msg_type == "welcome":
        msg = "Hello " + name + ", welcome to the investment monitor. \nTo start to use the bot, you can use the " \
                                     "command \usage \nThe very first thing to do is to indicate the currency you " \
                                "live in by the command /to_cur XYZ "
    elif msg_type == "usage":
        msg = "To use the bot you can use the following commands " \
              "\n /to_cur [CURRENCY] (e.g. /to_cur TRY) : indicates the currency you live in. " \
              "\n /add [AMOUNT] [CURRENCY] (e.g. /add 5000 USD) : adds the indicated amount to your account." \
              "\n /rem [AMOUNT] [CURRENCY] (e.g. /rem 3000 USD) : removes the indicated amount from your account." \
              "\n /info lists all of the money in your account and gives the sum. " \
              "\n /min [AMOUNT] indicates the minimum threshold to be notified" \
              "\n /max [AMOUNT] indicates the maximum threshold to be notified"
    elif msg_type == "add_money":
        msg = "Dear " + name + ", " + money + " is added to your account"
    elif msg_type == "rem_money":
        msg = "Dear " + name + ", " + money + " is subtracted from your account"
    elif msg_type == "rem_money_neg":
        msg = "Dear " + name + ", " + money + " could not be subtracted from your account, probably you don't have " \
                                              "enough balance."
    elif msg_type == "info":
        if "money" in user_dict[user]:
            msg = "Dear " + name + ", your balance is as the following;\n"
            for money in user_dict[user]["money"]:
                msg += str(user_dict[user]["money"][money]) + " " + str(money) + "\n"
            cur_investment = current_investment(fetch_currency(), users[user]["money"], users[user]["to_cur"])
            msg += "And in total you have " + str(cur_investment) + " " + users[user]["to_cur"]
        else:
            msg = "First you need to add some money into your account by the /add command"
    elif msg_type == "none_to_cur":
        msg = "Dear " + name + ", please first define the currency you live in with the command /to_cur CUR"
    elif msg_type == "lower":
        msg = "Dear " + name + ", you are losing money! Your total investment value is now "
        cur_investment = current_investment(fetch_currency(), users[int(user)]["money"], users[user]["to_cur"])
        msg += str(cur_investment) + users[user]["to_cur"]
    elif msg_type == "higher":
        msg = "Dear " + name + ", you are making money! Your total investment value is now "
        cur_investment = current_investment(fetch_currency(), users[int(user)]["money"], users[user]["to_cur"])
        msg += str(cur_investment) + users[user]["to_cur"]

    bot.sendMessage(user, msg)


def is_valid(txt):
    if "/add" in txt or "/rem" in txt:
        parts = txt.split(" ")
        if parts[0] == "/add" or parts[0] == "/rem":
            amount = 0
            try:
                amount = float(parts[1])
            except ValueError:
                return False

            currency = parts[2]
            if currency in currencies:
                return True
    elif "/to_cur" in txt:
        parts = txt.split(" ")
        if parts[0] == "/to_cur" and parts[1] in currencies:
            return True
    elif "/max" in txt or "/min" in txt:
        parts = txt.split(" ")
        if parts[0] == "/max" or parts[0] == "/min":
            amount = 0
            try:
                amount = float(parts[1])
            except ValueError:
                return False
            return True
    elif txt == "/info" or txt == "/usage" or txt == "/start":
        return True

    return False


def message_handler(message):
    txt = str(message['text'])
    user = message['from']['id']
    name = message['from']['first_name']

    if is_valid(txt):
        if user not in users:
            users[int(user)] = {}
            users[int(user)]["name"] = str(name)
        if txt == "/start":
            send_message("welcome", int(user), str(name))
        elif txt == "/usage":
            send_message("usage", int(user), str(name))
        elif "/add" in txt:
            parts = txt.split(" ")
            if "to_cur" not in users[int(user)]:
                send_message("none_to_cur", int(user), str(name))
            else:
                if "money" not in users[int(user)]:
                    users[int(user)]["money"] = {}
                if parts[2] not in users[int(user)]["money"]:
                    users[int(user)]["money"][parts[2]] = 0

                currencies_in_usage.add(parts[2])
                users[int(user)]["money"][parts[2]] += float(parts[1])
                send_message("add_money", int(user), str(name), parts[1] + " " + parts[2])
        elif "/rem" in txt:
            subtracted = False
            parts = txt.split(" ")
            if "money" in users[int(user)]:
                if parts[2] in users[int(user)]["money"]:
                    if users[int(user)]["money"][parts[2]] > float(parts[1]):
                        users[int(user)]["money"][parts[2]] -= float(parts[1])
                        send_message("rem_money", int(user), str(name), parts[1] + " " + parts[2])
                        subtracted = True

            if not subtracted:
                send_message("rem_money_neg", int(user), str(name), parts[1] + " " + parts[2])
        elif "/info" == txt:
            send_message("info", int(user), str(name), user_dict=users)
        elif "/to_cur" in txt:
            users[int(user)]["to_cur"] = txt.split(" ")[1]
            currencies_in_usage.add(users[int(user)]["to_cur"])
        elif "/min" in txt:
            users[int(user)]["min"] = float(txt.split(" ")[1])
        elif "/max" in txt:
            users[int(user)]["max"] = float(txt.split(" ")[1])


def main():
    bot.message_loop(message_handler)

    while 1:
        for user in users:
            if "to_cur" in users[int(user)] and "money" in users[int(user)]:
                cur_investment = current_investment(fetch_currency(), users[int(user)]["money"], users[int(user)]["to_cur"])
                if "max" in users[int(user)] and cur_investment > users[int(user)]["max"]:
                    send_message("higher", int(user), users[int(user)]["name"])
                elif "min" in users[int(user)] and cur_investment < users[int(user)]["min"]:
                    send_message("lower", int(user), users[int(user)]["name"])
        time.sleep(10)


if __name__ == "__main__":
    main()
