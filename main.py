import os
import re
import telebot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from flask import Flask, request
from model import Participants


TOKEN = os.environ["API_TOKEN"]
URL = os.environ["BOT_URL"]
ADMIN_ID = os.getenv("MY_ID")
COEFFICENTS = (1.29, 3.64)
IS_RUNNING = False

bot = telebot.TeleBot(TOKEN)
# bot.remove_webhook()
# bot.set_webhook(url=URL)


# app = Flask(__name__)

db = Participants("predictions.db")

predictions = {}
money = {}


# @app.route("/", methods=["POST"])
# def hook():
#     update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'OK', 200


kb_bid_reply = InlineKeyboardMarkup()
kb_bid_reply.add(
    InlineKeyboardButton('0.5 BYN', callback_data='kb_bid_btn1'),
    InlineKeyboardButton('1.5 BYN', callback_data='kb_bid_btn2'),
    InlineKeyboardButton('3.5 BYN', callback_data='kb_bid_btn3'),
    InlineKeyboardButton('Custom', callback_data='kb_bid_btn4'),
)


@bot.callback_query_handler(func=lambda c: c.data.startswith('kb_pred'))
def callback_handle_kb_pred(c: CallbackQuery):
    code = c.data[-1]
    if code == "1":
        predictions[c.from_user.id] = "pass"
    else:
        predictions[c.from_user.id] = "fail"
    bot.send_message(c.message.chat.id,
                     text="Gotcha, I saved your prediction!\nNow choose amount of bid.",
                     reply_markup=kb_bid_reply)


@bot.callback_query_handler(func=lambda c: c.data.startswith('kb_bid'))
def callback_handle_kb_bid(c: CallbackQuery):
    global IS_RUNNING
    code = c.data[-1]
    user = c.from_user
    username = user.username
    user_id = user.id
    chat_id = c.message.chat.id

    if code == "1":
        money[user_id] = 0.5
        IS_RUNNING = False
    elif code == "2":
        money[user_id] = 1.5
        IS_RUNNING = False
    elif code == "3":
        money[user_id] = 3.5
        IS_RUNNING = False
    elif code == "4":
        msg = bot.send_message(chat_id, "Enter your amount of money.")
        bot.register_next_step_handler(msg, custom_money_input)
        IS_RUNNING = True

    if not IS_RUNNING:
        db.insert_values((user_id, username, predictions[user_id], money[user_id]))
        bot.send_message(c.message.chat.id, text="Gotcha, I saved your bid!")
        IS_RUNNING = False


def custom_money_input(m: Message):
    global IS_RUNNING
    user = m.from_user
    chat_id = m.chat.id
    user_id = user.id
    username = user.username
    text = m.text

    match = re.match(r'\d+\.*\d*', text)
    if not match:
        msg = bot.send_message(chat_id, "You've forgot some numbers in your input. Try one more time")
        bot.register_next_step_handler(msg, custom_money_input)
        return

    money[user_id] = int(match.group(0))
    db.insert_values((user_id, username, predictions[user_id], money[user_id]))
    bot.send_message(chat_id, text="Gotcha, I saved your bid!")
    IS_RUNNING = False


@bot.message_handler(commands=['bid'])
def bid(m: Message):
    global IS_RUNNING
    if not IS_RUNNING:
        IS_RUNNING = True
        btn_pred_p = InlineKeyboardButton('Pass: 1.29', callback_data='kb_pred_btn1')
        btn_pred_f = InlineKeyboardButton('Fail: 3.64', callback_data='kb_pred_btn2')

        user_prediction = db.get_prediction(m.from_user.id)
        if not user_prediction:
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(btn_pred_p, btn_pred_f)
        elif user_prediction[0] == "pass":
            kb = InlineKeyboardMarkup()
            kb.add(btn_pred_p)
        else:
            kb = InlineKeyboardMarkup()
            kb.add(btn_pred_f)

        bot.send_sticker(m.chat.id, "CAACAgIAAxkBAALb3mAxW_HxbZptc1xq7Oi1f1FSDj88AAJiAwACbbBCA5mTqKDVhSM1HgQ")
        bot.send_message(m.chat.id, "Now i'll send you predictions...", reply_markup=kb)


@bot.message_handler(commands=['getbid'])
def getbids(m: Message):
    user = m.from_user
    value = db.get_value(user.id)
    if not value:
        bot.send_message(m.chat.id, text=f"You've not bet on Tischa's yet.")
        return
    if value[1] == "pass":
        coef = COEFFICENTS[0]
    else:
        coef = COEFFICENTS[1]
    gained = round(value[2]*coef + value[2], 2)
    bot.send_message(m.chat.id, text=f"User {value[0]} bid: {value[2]} on {value[1]}. You'll gain {gained} BYN.")


@bot.message_handler(commands=['getallbids'])
def getallbids(m: Message):
    user_id = str(m.from_user.id)
    chat_id = m.chat.id
    if user_id == ADMIN_ID:
        all_preds = db.get_all()
        sentences = []
        for pred in all_preds:
            sentences.append(f"User {pred[0]} with {pred[1]} nickname bet on {pred[2]} {pred[3]} BYN.")
        msg = '\n'.join(sentences)
        if not msg:
            msg = "No one have bet on Tischa yet."
        bot.send_message(chat_id, msg)
    else:
        bot.send_message(m.chat.id, "You're not allowed to watch this statistics!")


@bot.message_handler(commands=['help'])
def bot_help(m: Message):
    chat_id = m.chat.id
    text = """
This bot allowed you to bet on Tischa's interview imaginary money.
You can make it by pressing /bid command.
To get your summary bids press the /getbids command.
To navigate to Tischa's gorgeous profile on Instagram type /shit command.
    """
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['shit'])
def shit(m: Message):
    chat_id = m.chat.id
    kb = InlineKeyboardMarkup()
    url_btn = InlineKeyboardButton(text="To Tischa's profile:", url="https://www.instagram.com/kristina_evil/")
    kb.add(url_btn)
    bot.send_message(chat_id, text="Think twice before this step...", reply_markup=kb)


@bot.message_handler(commands=['start'])
def start(m: Message):
    chat_id = m.chat.id
    bot.send_message(chat_id, "Hey, vagabond...\nAh, I see you're man of culture as well.")


bot.polling(none_stop=True)
