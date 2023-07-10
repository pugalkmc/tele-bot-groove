import datetime
import time
import requests
from pymongo import MongoClient
from telegram import ReplyKeyboardMarkup
from telegram._bot import Bot
from binance import Client

time_fun = datetime.datetime

admin_list = ["pugalkmc", "sarankmc", "groovemark", "Riyanmark799", "Dustin_05"]

api_key = '0rILNUx04etsxLKcM5ydIDepAkaGdQ9O6GyNuVvYkbSgQ56RVXDZH7Xz3dZKVBA6'
api_secret = 'CgNIsKOVjun0WFAcuCSWSlWi9mD7fue0xOkR8r3OctFGa5occMkDpALdR5Gt1anB'
client = Client(api_key, api_secret)

mongo_client = MongoClient("mongodb+srv://marketersgroove:pugalsaran143@cluster0.hnxcrow.mongodb.net/")
db = mongo_client["groovedb"]
peoples_col = db["peoples"]
tasks_col = db["tasks"]

BOT_TOKEN = "5638732799:AAFNmRh2tRX4O2ERgMnRFSJR8Dmfu06NrWw"
bot = Bot(token=BOT_TOKEN)


async def menu_button(update, context):
    message = update.message
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        return
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    reply_keyboard = []
    if username in admin_list:
        reply_keyboard = [["settings", "My task"], ["Admin Mode"]]
    else:
        reply_keyboard = [["settings", "My task"]]
    await context.bot.send_message(chat_id=chat_id, text="Choose options",
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True),
                                   reply_to_message_id=update.message.message_id)


async def settings(update, context):
    message = update.message
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        return
    chat_id = update.message.chat_id
    text = update.message.text
    reply_keyboard = [["twitter", "binance", "discord"], ['UPI ID', 'main menu']]
    await context.bot.send_message(chat_id=chat_id, text="Choose options",
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True),
                                   reply_to_message_id=update.message.message_id)


async def distribute_payment(update, context, dict_payment, total_cost):
    chat_id = update.message.chat_id
    text = update.message.text
    tusd_balance = client.get_asset_balance(asset='TUSD')
    balance = float(tusd_balance['free'])
    if balance < total_cost:
        await bot.send_message(chat_id=chat_id, text=f"Available balance on binance: {balance} TUSD\n"
                                                     f"Distribution cancelled")
        return
    for user in dict_payment:
        if 'binance' in user:
            await binance_pay(user['chat_id'], user['binance'], user['amount'], chat_id)
            time.sleep(5)
    await bot.send_message(chat_id=chat_id, text="Distribution completed!")


async def binance_pay(chat_id, binance_id, amount, dev_id=None):
    deposit_address = client.get_deposit_address(coin='TUSD', network="BSC", recvWindow=5000, binance_id=binance_id)
    address = deposit_address['address']
    await bot.send_message(chat_id=chat_id, text=f"Binance id:{binance_id}\n"
                                                 f"Address: {address}")

    response = client.withdraw(
        coin='TUSD',
        address=address,
        amount=amount,
        network='BSC')

    transaction_details = client.get_withdraw_history(asset='TUSD', txId=response['id'])
    transaction_hash = transaction_details['txId']
    hash_count = 0
    while hash_count < 5:
        hash_count = check_transaction_confirmation(transaction_hash)
        time.sleep(1)

    transaction_url = f"https://bscscan.com/tx/{transaction_hash}"
    await bot.send_message(chat_id=chat_id, text="Your reward for the work has been sent to your binance account\n\n"
                                                 "Assest: TUSD\n"
                                                 f"Amount: {amount}\n"
                                                 f"Hash confirmation: {hash_count}\n"
                                                 f"Check transaction: <a href={transaction_url}>DETAIL</a>")


def check_transaction_confirmation(transaction_hash):
    bscscan_api_key = 'ADNU4CKRS8PNSHKZYSF1PQVIYEPYDNIB23'
    api_url = f'https://api.bscscan.com/api?module=transaction&action=gettxreceiptstatus&txhash={transaction_hash}&apikey={bscscan_api_key}'
    response = requests.get(api_url)
    transaction_data = response.json()
    return transaction_data['result']['status']


async def otp_sender(update, context):
    return 1234
    # sender = "c52065dab4368d@sandbox.smtp.mailtrap.io"
    # receiver = "pugalkmc@gmail.com"
    #
    # message = f"""\
    # Subject: Hi Mailtrap
    # To: {receiver}
    # From: {sender}
    #
    # This is a test e-mail message."""
    #
    # with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
    #     server.login("c52065dab4368d", "a7c808b3d4498b")
    #     server.sendmail(sender, receiver, message)
    #     return 1111


import json


def process_json_file():
    with open("peoples.json") as file:
        data = json.load(file)

        # Iterate over each item in the JSON data
        for item in data.values():
            if "binance" in item:
                account_info = client.get_account()
                if "canTrade" in account_info:
                    print(f"{item['binance']} is a valid Binance ID.")
                else:
                    print(f"username:{item['username']} "
                          f"{item['binance']} is not a valid Binance ID")
                    # bot.send_message(chat_id=,
                    #                  text=f"{text} is not a valid Binance ID\nRe-try")
            # peoples_col.insert_one(item)
