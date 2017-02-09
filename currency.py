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
    if data["success"]:
        for cur in currencies_in_usage:
            if cur is not "USD":
                cur_values["USD/" + cur] = 0

        for resource in data["list"]["resources"]:
            if data["list"]["resources"][resource]["name"] in cur_values:
                cur_values[data["list"]["resources"][resource]["name"]] = float(data["list"]["resources"][resource]["price"])

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
        msg = "Hello " + str(name) + "welcome to the investment monitor. \n To start to use the bot, you can use the " \
                                     "command \info "
    elif msg_type == "usage":
        msg = "To use the bot you can use the following commands " \
              "\n /to_cur [CURRENCY] (e.g. /to_cur TRY) : indicates the currency you live in. " \
              "\n /add [AMOUNT] [CURRENCY] (e.g. /add 5000 USD) : adds the indicated amount to your account." \
              "\n /rem [AMOUNT] [CURRENCY] (e.g. /rem 3000 USD) : removes the indicated amount from your account." \
              "\n /info lists all of the money in your account and gives the sum. "
    elif msg_type == "add_money":
        msg = "Dear " + name + ", " + money + " is added to your account"
    elif msg_type == "rem_money":
        msg = "Dear " + name + ", " + money + " is subtracted from your account"
    elif msg_type == "rem_money_neg":
        msg = "Dear " + name + ", " + money + "could not be subtracted from your account, \nprobably you don't have " \
                                              "enough balance."
    elif msg_type == "info":
        msg = "Dear " + name + ", your balance is as the following;\n"
        for money in user_dict[user]["money"]:
            msg += user_dict[user]["money"][money] + " " + money + "\n"
    elif msg_type == "none_to_cur":
        msg = "Dear " + name + ", please first define the currency you live in with the command /to_cur CUR"

    bot.sendMessage(user, msg)


def is_valid(txt):
    if "/add" in txt:
        parts = txt.split(" ")
        if parts[0] == "/add":
            amount = 0
            try:
                amount = float(parts[1])
            except ValueError:
                return False

            currency = parts[2]
            if currency in currencies:
                return True
    elif "/rem" in txt :
        parts = txt.split(" ")
        if parts[0] == "/rem":
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

    elif txt == "/info" or txt == "/usage" or txt == "/start":
        return True

    return False


def message_handler(message):
    txt = str(message['text'])
    user = message['from']['id']
    name = message['from']['first_name']

    if is_valid(txt):
        if user not in users:
            users[user]["name"] = name
        if txt == "/start":
            send_message("welcome", user, name)
        elif txt == "/usage":
            send_message("usage", user, name)
        elif "/add" in txt:
            parts = txt.split(" ")
            if "to_cur" not in users[user]:
                send_message("none_to_cur", user, name)
            else:
                if "money" not in users[user]:
                    users[user]["money"] = {}
                if parts[2] not in users[user]["money"]:
                    users[user]["money"][parts[2]] = 0

                currencies_in_usage.add(parts[2])
                users[user]["money"][parts[2]] += float(parts[1])
                send_message("add_money", user, name, parts[1] + " " + parts[2])
        elif "/rem" in txt:
            subtracted = False
            parts = txt.split(" ")
            if "money" in users[user]:
                if parts[2] in users[user]["money"]:
                    if users[user]["money"][parts[2]] > float(parts[1]):
                        users[user]["money"][parts[2]] -= float(parts[1])
                        send_message("rem_money", user, name, parts[1] + " " + parts[2])
                        subtracted = True

            if not subtracted:
                send_message("rem_money_neg", user, name, parts[1] + " " + parts[2])
        elif "/info" == txt:
            send_message("info", user, name, user_dict=users)
        elif "/to_cur" in txt:
            users[user]["to_cur"] = txt.split(" ")[1]
            currencies_in_usage.add(users[user]["to_cur"])


def main():
    bot.message_loop(message_handler)

    while 1:
        for user in users:
            if user["to_cur"] is not None and user["money"] is not None:
                cur_investment = current_investment(fetch_currency(), user["money"], user["to_cur"])
                if cur_investment > user["max"]:
                    send_message("higher", user, user["name"])
        time.sleep(10)


if __name__ == "__main__":
    main()
