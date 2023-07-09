import asyncio
from datetime import timedelta
from telegram.ext import ConversationHandler

import functions
from functions import *
import sheet_file
from functions import menu_button, bot

ADMIN_MODE, MEMBER_START, SHEET_OPTION, DATE_RANGE, PROCEED_PAYMENT, PAYMENT_FOR_TASK, CHECK_PASSWORD = range(7)


async def task_id(update, context):
    message = update.message
    chat_id = message.chat_id
    if message.chat.type in ['group', 'supergroup']:
        return ConversationHandler.END
    username = message.from_user.username
    reply_keyboard = [["cancel"]]
    await context.bot.send_message(chat_id=chat_id, text="Enter the task ID to go settings",
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True),
                                   reply_to_message_id=update.message.message_id)
    return ADMIN_MODE


async def admin_mode(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if 'task_id' in context.user_data:
        text = context.user_data['task_id']
    if text == "cancel":
        await menu_button(update, context)
        return ConversationHandler.END

    if not text.isnumeric():
        await bot.send_message(chat_id=chat_id, text="Task ID must be a number")
        return ADMIN_MODE

    task_details = tasks_col.find_one({"task_id": int(text)})
    if not task_details:
        await bot.send_message(chat_id=chat_id, text="Task ID incorrect")
        return ADMIN_MODE
    flex_text = f"Task ID: {task_details['title']}\nChoose options"
    context.user_data["task_id"] = text
    context.user_data['group_id'] = task_details['group_id']
    context.user_data['title'] = task_details['title']
    context.user_data['task_type'] = task_details['task_type']

    # if username in admin_list:
    reply_keyboard = [["Show records", "Edit task"], ['back']]
    await bot.send_message(
        chat_id=chat_id,
        text=flex_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
        reply_to_message_id=update.message.message_id
    )
    return MEMBER_START


async def member_start(update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text.lower()
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Data retrieve request cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    if text == "show records":
        await bot.send_message(chat_id=chat_id, text=f"Enter the start and end date to retrieve the data\n"
                                                     f"Example: 01-01-2023 30-03-2023")
        return SHEET_OPTION
    elif text == "back":
        await menu_button(update, context)
        return ConversationHandler.END
    else:
        await bot.send_message(chat_id=chat_id, text="Please select a valid option")
        return MEMBER_START


async def sheet_option(update, context):
    text = update.message.text
    chat_id = update.message.chat_id
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Data retrieve request cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    date_li = text.split(" ")
    try:
        start_date = time_fun.strptime(date_li[0], "%d-%m-%Y")
        context.user_data['start_date'] = start_date
        end_date = time_fun.strptime(date_li[1], "%d-%m-%Y")
        context.user_data['end_date'] = end_date if len(date_li) == 2 else start_date
    except:
        await bot.send_message(chat_id=chat_id, text="Date format wrong")
        return SHEET_OPTION
    await bot.send_message(chat_id=chat_id, text="Do you need spreadsheet for each date separately ? yes/no")
    return DATE_RANGE


async def date_range(update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text.lower()
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Data retrieve request cancelled")
        await menu_button(update, context)
        return ConversationHandler.END

    sheet = True if text == 'yes' else False
    await bot.send_message(chat_id=chat_id, text="Great , Wait some moment")
    start_date = context.user_data['start_date']
    end_date = context.user_data['end_date']
    current_date = start_date
    group_id = context.user_data["group_id"]
    dict_payment = dict()
    total_dates = tasks_col.find_one({"group_id": group_id})['collection']
    while current_date <= end_date:
        other_date = current_date.strftime("%d-%m-%Y")
        # each_date = db.reference(f"tasks/{group_id}/collection/{other_date}").get() or {}
        each_date = {} if other_date not in total_dates else total_dates[other_date]
        if len(each_date) <= 0:
            current_date += timedelta(days=1)
            continue
        dict_each_date = dict()
        for i in each_date:
            user = i['username']
            if user not in dict_payment:
                get_user = peoples_col.find_one({"chat_id": i['chat_id']})
                if get_user and "binance" in get_user:
                    dict_payment[user] = {'count': 1, 'username': user, 'binance': get_user['binance'],
                                          'chat_id': get_user['chat_id']}
                else:
                    upi = get_user['upi'] if 'upi' in dict_payment else "None"
                    dict_payment[user] = {'count': 1, 'username': user, 'chat_id': get_user['chat_id'], 'upi': upi}
            else:
                dict_payment[user]['count'] += 1

            dict_each_date[user] = 1 if user not in dict_each_date else dict_each_date[user] + 1

        # send counts via message for each date
        each_date_text = f"Count for {current_date.strftime('%d-%m-%Y')}\n"
        for i in dict_each_date:
            each_date_text += f"{i} : {dict_each_date[i]}\n"
        await bot.send_message(chat_id=chat_id, text=each_date_text)
        # send via sheet
        if sheet:
            await sheet_file.spreadsheet(chat_id, context.user_data['task_id'],
                                         current_date.strftime('%d-%m-%Y'))
        current_date += timedelta(days=1)

    # Send total counts statistics for range of dates
    context.user_data['dict_payment'] = dict_payment
    text = f"Total counts from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}\n\n"
    for i in dict_payment.values():
        text += f"{i['username']} : {i['count']}\n"
    await bot.send_message(chat_id=chat_id, text=text)
    await bot.send_message(chat_id=chat_id, text="Process payment distribution for binance user? yes/no")
    return PROCEED_PAYMENT


async def proceed_payment(update, context):
    message = update.message
    text = message.text.lower()
    if text == "yes":
        await bot.send_message(chat_id=message.chat_id,
                               text="Ok, Now send the payment for each task completion in TUSD")
        return PAYMENT_FOR_TASK
    elif text == "no":
        await bot.send_message(chat_id=message.chat_id, text="Returning to admin mode")
        return ADMIN_MODE
    else:
        await menu_button(update, context)
        return ConversationHandler.END


async def payment_for_task(update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text
    pay_text = "Payment allocation:\n\n"
    try:
        text = float(text)
    except:
        await bot.send_message(chat_id=chat_id, text="Not a number")
        return PAYMENT_FOR_TASK
    total_cost = float()
    context.user_data['cost'] = text
    dict_payment = context.user_data['dict_payment']
    for user in dict_payment.values():
        amount = float("%.2f" % (text * user['count']))
        dict_payment[user['username']]['amount'] = amount
        pay_text += f"{user['username']} - {amount}\n"
        total_cost += amount
    pay_text += f"\nTotal Cost: {total_cost}\n\nConfirm the above data and enter password to start distribution"
    context.user_data['total_cost'] = total_cost
    await bot.send_message(chat_id=chat_id, text=pay_text)
    return CHECK_PASSWORD


async def check_password(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="payment distribution canceled")
        await menu_button(update, context)
        return ConversationHandler.END
    if text == "groove123":
        await bot.send_message(chat_id=chat_id, text="Got the confirmation , starting distribution")
        # Run distribute_payment() concurrently using asyncio
        asyncio.create_task(
            functions.distribute_payment(update, context, context.user_data['dict_payment'],
                                         total_cost=context.user_data['total_cost'])
        )
        await menu_button(update, context)
        return ConversationHandler.END
    else:
        await bot.send_message(chat_id=chat_id, text="wrong password")
        return CHECK_PASSWORD
