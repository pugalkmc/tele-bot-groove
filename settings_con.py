from firebase_admin import db
from telegram.ext import ConversationHandler
from functions import *

TWITTER_UPDATE, TWITTER_UPDATE_LIST, TWITTER_UPDATE_CONFIRM = range(3)


async def twitter_ids(update, context):
    message = update.message
    if message.chat.type in ['group', 'supergroup']:
        return ConversationHandler.END
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    reply_keyboard = [["Update ID's", "My id's"], ['settings']]
    await bot.send_message(chat_id=chat_id, text="Twitter settings",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True),
                           reply_to_message_id=update.message.message_id)
    return TWITTER_UPDATE


async def twitter_update(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    if "update id's" == text:
        reply_keyboard = [['cancel']]
        await bot.send_message(chat_id=chat_id, text="Now send the all twitter usernames comma(,) separated including "
                                                     "previously added id's\n"
                                                     "Example: @pugalkmc",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True),
                               reply_to_message_id=update.message.message_id)
        return TWITTER_UPDATE_LIST
    elif "my id's" == text:
        get_ids = peoples_col.find_one({'chat_id': chat_id})
        if get_ids and 'twitter' in get_ids:
            form_text = "Twitter id's list:\n"
            for i in get_ids['twitter']:
                form_text += f"@{i} "
            await bot.send_message(chat_id=chat_id, text=form_text)
        else:
            await bot.send_message(chat_id=chat_id, text="No twitter id's found!")
        return await twitter_ids(update, context)
    elif "settings" == text:
        await settings(update, context)
        return ConversationHandler.END


async def twitter_update_list(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    if "cancel" == text.lower():
        return await twitter_ids(update, context)
    ids = text.replace("@", "").replace(" ", "").split(",")
    ids_text = ''
    for i in ids:
        ids_text += f"@{i} "
    context.user_data['twitter_ids'] = ids
    reply_keyboard = [["confirm", "cancel"]]
    await bot.send_message(chat_id=chat_id, text=f"Twitter ID:\n"
                                                 f"{ids_text}\n\n"
                                                 f"Please click confirm or cancel the process",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True)
                           )
    return TWITTER_UPDATE_CONFIRM


async def twitter_update_confirm(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    text = text.lower()
    if "confirm" == text:
        print(context.user_data['twitter_ids'])
        peoples_col.update_one({"chat_id": chat_id}, {"$set": {"twitter": context.user_data['twitter_ids']}},
                               upsert=True)
        await bot.send_message(chat_id=chat_id, text="Your twitter id's are updated")
        return await twitter_ids(update, context)
    elif "cancel" == text:
        return await twitter_ids(update, context)
    else:
        await bot.send_message(chat_id=chat_id, text="Please correct option 'confirm' or 'cancel'")
        return TWITTER_UPDATE_CONFIRM


BINANCE_OPTIONS, SET_BINANCE = range(2)


async def binance_start(update, context):
    message = update.message
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        return ConversationHandler.END
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    get_data = peoples_col.find_one({"chat_id": chat_id})
    if get_data and 'binance' in get_data:
        reply_keyboard = [["change binance", "settings"]]
        await bot.send_message(chat_id=chat_id, text=f"Your binance ID : {get_data['binance']}",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        context.user_data['status'] = 'set'
    else:
        reply_keyboard = [["set binance", "settings"]]
        await bot.send_message(chat_id=chat_id, text=f"Your binance not set",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        context.user_data['status'] = 'not set'
    return BINANCE_OPTIONS


async def binance_option(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    if context.user_data['status'] == 'set':
        option_1 = "change binance"
    else:
        option_1 = "set binance"

    if option_1 == text:
        reply_keyboard = [["cancel"]]
        await bot.send_message(chat_id=chat_id, text=f"Now send the binance ID to set",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        return SET_BINANCE
    elif "settings" == text:
        await settings(update, context)
        return ConversationHandler.END
    else:
        await bot.send_message(chat_id=chat_id, text="Please select valid option")
        return BINANCE_OPTIONS


async def set_binance(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    if "cancel" == text:
        await settings(update, context)
        return ConversationHandler.END
    if text.isnumeric():
        peoples_col.update_one({"chat_id": chat_id}, {"$set": {"binance": text}}, upsert=True)
        return await binance_start(update, context)
    else:
        await bot.send_message(chat_id=chat_id, text="Binance ID must be a number")
        return SET_BINANCE


DISCORD_OPTIONS, SET_DISCORD = range(2)


async def discord_start(update, context):
    message = update.message
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        return ConversationHandler.END
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    get_data = peoples_col.find_one({"chat_id": chat_id})
    if get_data and 'discord' in get_data:
        reply_keyboard = [["change discord", "settings"]]
        await bot.send_message(chat_id=chat_id, text=f"Your discord username : {get_data['discord']}",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        context.user_data['status'] = 'set'
    else:
        reply_keyboard = [["set discord", "settings"]]
        await bot.send_message(chat_id=chat_id, text=f"Your discord username not set",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        context.user_data['status'] = 'not set'
    return DISCORD_OPTIONS


async def discord_option(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    if context.user_data['status'] == 'set':
        option_1 = "change discord"
    else:
        option_1 = "set discord"

    if option_1 == text:
        reply_keyboard = [["cancel"]]
        await bot.send_message(chat_id=chat_id, text=f"Now send the discord username to set\n"
                                                     f"Example: PugalKMC#5040",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        return SET_DISCORD
    elif "settings" == text:
        await settings(update, context)
        return ConversationHandler.END
    else:
        await bot.send_message(chat_id=chat_id, text="Please select valid option")
        return DISCORD_OPTIONS


async def set_discord(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    if "cancel" == text.lower():
        await settings(update, context)
        return ConversationHandler.END
    if "#" in text:
        peoples_col.update_one({"chat_id": chat_id}, {"$set": {"discord": text}}, upsert=True)
        return await discord_start(update, context)
    else:
        await bot.send_message(chat_id=chat_id, text="Invalid discord username")
        return SET_DISCORD


UPI_OPTIONS, SET_UPI = range(2)


async def upi_start(update, context):
    message = update.message
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        return ConversationHandler.END
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    get_data = peoples_col.find_one({"chat_id": chat_id})
    if get_data and 'upi' in get_data:
        reply_keyboard = [["Change UPI", "Settings"]]
        await bot.send_message(chat_id=chat_id, text=f"Your UPI ID: {get_data['upi']}",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        context.user_data['status'] = 'set'
    else:
        reply_keyboard = [["Set UPI", "Settings"]]
        await bot.send_message(chat_id=chat_id, text=f"Your UPI ID not set",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        context.user_data['status'] = 'not set'
    return UPI_OPTIONS


async def upi_option(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text.lower()
    if context.user_data['status'] == 'set':
        option_1 = "change upi"
    else:
        option_1 = "set upi"

    if option_1 == text:
        reply_keyboard = [["cancel"]]
        await bot.send_message(chat_id=chat_id, text=f"Now send the UPI ID to set\n"
                                                     f"Example: 9344776097@paytm",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True)
                               )
        return SET_BINANCE
    elif "settings" == text:
        await settings(update, context)
        return ConversationHandler.END
    else:
        await bot.send_message(chat_id=chat_id, text="Please select a valid option")
        return UPI_OPTIONS


async def set_upi(update, context):
    message = update.message
    chat_id = message.chat_id
    username = message.from_user.username
    text = message.text
    if "cancel" == text.lower():
        await settings(update, context)
        return ConversationHandler.END
    if "@" in text:
        peoples_col.update_one({"chat_id": chat_id}, {"$set": {"upi": text}}, upsert=True)
        return await upi_start(update, context)
    else:
        await bot.send_message(chat_id=chat_id, text="Invalid UPI ID")
        return SET_UPI
