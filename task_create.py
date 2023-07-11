from firebase_admin import db
from telegram.ext import ConversationHandler
from functions import *

TITLE, TASK_TYPE, CHAT_ID, USER_TARGET, DAILY_TARGET, MEMBERS_LIST, CONFIRM = range(7)


async def create_task(update, context):
    message = update.message
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        return ConversationHandler.END
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    reply_keyboard = [["cancel"]]
    await bot.send_message(chat_id=chat_id, text="Send the task title",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True),
                           reply_to_message_id=update.message.message_id)
    return TITLE


async def title(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    if len(text) >= 5:
        context.user_data["title"] = text
        reply_keyboard = [["Filter", "Normal"], ["cancel"]]
        await bot.send_message(chat_id=chat_id, text=f"Task title set to : {text}\n\n"
                                                     f"Select the task type",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True),
                               reply_to_message_id=update.message.message_id)
        return TASK_TYPE
    else:
        await bot.send_message(chat_id=chat_id, text=f"Title too short , re-try",
                               reply_to_message_id=update.message.message_id)
        return TITLE


async def task_type(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    text = text.lower()
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    task_li = ["filter", "normal"]
    if text in task_li:
        context.user_data["task_type"] = text
        reply_keyboard = [["cancel"]]
        await bot.send_message(chat_id=chat_id, text=f"Chat type set to : {text} type\n\n"
                                                     f"Now send the group id",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True),
                               reply_to_message_id=update.message.message_id)
        return CHAT_ID
    else:
        await bot.send_message(chat_id=chat_id, text=f"Type only can be {task_li}",
                               reply_to_message_id=update.message.message_id)
        return TASK_TYPE


async def chat_id(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END

    group_type = 0
    chat_info = ""
    if not text.isnumeric():
        await bot.send_message(chat_id=chat_id, text="Chat id must be number",
                               reply_to_message_id=update.message.message_id)
        return CHAT_ID
    try:
        # use the get_chat method to retrieve information about the chat
        chat_info = await bot.get_chat(chat_id=int("-" + str(text)))
    except:
        # Handle the error if the chat ID is invalid
        try:
            chat_info = await bot.get_chat(chat_id=int("-100" + str(text)))
        except:
            await bot.send_message(chat_id=chat_id,
                                   text="Invalid group id , Add me in the group and send the proper group id")
            return CHAT_ID
    if not chat_info['permissions']['can_send_messages']:
        await bot.send_message(chat_id=chat_id, text=f"I must need admin permission in : {chat_info['title']}")
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    if chat_info.type == 'group':
        group_type = "group"
    elif chat_info.type == 'supergroup':
        group_type = "supergroup"
    else:
        await bot.send_message(chat_id=chat_id, text="It is not a group or supergroup",
                               reply_to_message_id=update.message.message_id)
        return CHAT_ID
    context.user_data["group_type"] = group_type
    context.user_data["group_id"] = chat_info['id']
    context.user_data["group_title"] = chat_info.title
    flexible_text = "Now set the daily user tweet target" if context.user_data[
                                                                 "task_type"] == "filter" else "Now send the daily user message target"
    await bot.send_message(chat_id=chat_id, text=f"Id set to : {text}\n"
                                                 f"Chat type: {group_type}\n"
                                                 f"Now send the {flexible_text}",
                           reply_to_message_id=update.message.message_id)
    return USER_TARGET


async def user_target(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END

    if text.isdigit():
        context.user_data["user_target"] = text
        flexible_text = f"Telegram message daily user target set to : {text}" if context.user_data[
                                                                                     "task_type"] == "normal" else f"Twitter tweet daily user target set to {text}"

        flexible = "Now set the daily total tweet target" if context.user_data[
                                                                 "task_type"] == "filter" else "Now send the daily " \
                                                                                               "message target"
        await bot.send_message(chat_id=chat_id, text=f"{flexible_text}\n\n"
                                                     f"{flexible}",
                               reply_to_message_id=update.message.message_id)
        return DAILY_TARGET
    else:
        await bot.send_message(chat_id=chat_id, text=f"Tweet limit only can be a number, re-try",
                               reply_to_message_id=update.message.message_id)
        return USER_TARGET


async def daily_target(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END

    if text.isdigit():
        context.user_data["daily_target"] = text
        flexible_text = f"Telegram message daily target set to : {text}" if context.user_data[
                                                                                "task_type"] == "normal" else f"Twitter tweet daily target set to {text}"
        await bot.send_message(chat_id=chat_id, text=f"{flexible_text}\n\n"
                                                     f"Now send workers telegram handle with comma separated\n"
                                                     f"NOTE: Don't include @",
                               reply_to_message_id=update.message.message_id)
        return MEMBERS_LIST
    else:
        await bot.send_message(chat_id=chat_id, text=f"Tweet limit only can be a number, re-try",
                               reply_to_message_id=update.message.message_id)
        return DAILY_TARGET


async def members_list(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    await bot.send_message(chat_id=chat_id, text="Got it , Now please confirm the above details once again",
                           reply_to_message_id=update.message.message_id)
    reply_keyboard = [["confirm", "cancel"]]
    await bot.send_message(chat_id=chat_id, text=f"Title: {context.user_data['title']}\n"
                                                 f"Chat_id: {context.user_data['group_id']}\n"
                                                 f"Task type: {context.user_data['task_type']}\n"
                                                 f"User target: {context.user_data['user_target']}\n"
                                                 f"Daily target: {context.user_data['daily_target']}\n"
                                                 f"Members: {text}",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True),
                           reply_to_message_id=update.message.message_id)
    context.user_data["workers"] = text
    return CONFIRM


async def confirm(update, context):
    chat_id = update.message.chat_id
    text = update.message.text.lower()
    if text == "cancel":
        await bot.send_message(chat_id=chat_id, text="Task creation Cancelled")
        await menu_button(update, context)
        return ConversationHandler.END
    username = update.message.chat.username
    if text == "confirm":
        group_id = context.user_data["group_id"]
        mem_list = context.user_data["workers"].replace(" ", "").replace('@', '').split(",")
        # ref_id = db.reference('last_task').get() or {}
        ref_id = db['last_task'].find_one({"id": "stable"})
        get_id = 0 if not ref_id else ref_id["task_id"]
        tasks_col.insert_one({
            'group_id': group_id,
            'title': context.user_data['title'],
            'task_id': get_id + 1,
            'user_target': context.user_data['user_target'],
            'daily_target': context.user_data['daily_target'],
            'created_by': username,
            'group_title': context.user_data['group_title'],
            'group_type': context.user_data['group_type'],
            'task_type': context.user_data['task_type'],
            'workers': mem_list,
            'status': 'active'
        })
        db['last_task'].update_one({"_id": 'stable'}, {"$set": {"task_id": get_id + 1}})

        await bot.send_message(chat_id=chat_id, text=f"Task created! Task ID : {get_id}")
        await menu_button(update, context)
        return ConversationHandler.END
    else:
        await bot.send_message(chat_id=chat_id, text="Please 'confirm' or 'cancel'")
        return CONFIRM
