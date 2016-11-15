[![Build Status](https://travis-ci.com/furkansahin/InterviewWork.svg?token=RNbzVctqSpCFa4kK2yzq&branch=master)](https://travis-ci.com/furkansahin/InterviewWork)

# InvestmentMonitor
InvestMonitor is a personal investment monitor implemented in Python.

Investment monitor uses [currency layer](http://currencylayer.com) API to fetch the live currency rates and [Pushover](https://pushover.net) to push notifications to any platform. 

It is created because of @furkansahin's slothful character. :)

If you have an investment as a foreign currency, you may want to check it regularly because of the unstable situation of the economy (in our case, it's Turkey :)) You can just run this script and wait for a notification or start @moneys_watch_bot on Telegram for hourly notifications.

Investment monitor takes inputs such as the amount of currency you have and you are living, waits for a minimum and maximum threshold to be notified and starts to run. You can just forget about your money now, it's gonna remind itself when you need to know.

## Needs
* Python 2.7 for Pushover implementation
* Python 3.x for Telegram bot development
 * Python requests library
 * Python telepot library
* Currency layer account (free if you are okay with 1 check per hour)
* Pushover account (Free for the first 7 days, then just 4.99$ for each platform once)
* Mobile platform having Pushover application installed
* Server(If you don't want to run it 24/7 on your own computer, inappropriate for the creation purpose of the script :D)
* [Telepot](http://telepot.readthedocs.io/en/latest/) for @moneys_watch_bot's development

## How to receive notifications using Pushover
1. Open the script in a text editor
2. Change the access key value with the provided access key from currency layer.
3. Change the api key token with the token provided by Pushover application.
4. Change the user key token with the token provided by Pushover registration system.
5. Upload the script to server.
6. Run the script as follows;

  ```
  python currency.py <Currency names used as from> to <currency names used as to> done <invesment amounts>
  ```
  
  For example
  
  ```
  python currency.py USD EUR to TRY done 1000 1000
  ```
  
7. After the first calculation result it is going to ask for a minimum threshold and a maximum threshold values. Enter them and leave the script as it is.

## How to receive notifications from Telegram
1. Open your Telegram and search for moneys_watch_bot
2. Type in /start and wait for our warm welcome message.
3. If you find the notifications coming in too frequent, you can always change it depending on your preferences.

### Found a bug?
Open up an issue! We follow up really quick.

Note: You can always ping sahinffurkan@gmail.com for your questions.
