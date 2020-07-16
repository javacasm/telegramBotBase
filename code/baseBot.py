#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages, get MQTT connection

"""

# basado en el código de @inopya https://github.com/inopya/mini-tierra

import logging
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.error import NetworkError, Unauthorized
import requests
import time # The time library is useful for delays
import os

import sys
import config
import utils
import TelegramBase

v = '0.9.5'

update_id = None

# 'keypad' buttons
user_keyboard = [['/help','/info'],['/ejemplo1','/ejemplo2'],['/fichero']]

# user_keyboard_markup = ReplyKeyboardMarkup(user_keyboard, one_time_keyboard=True)
user_keyboard_markup = ReplyKeyboardMarkup(user_keyboard)

commandList = '/help, /info, /ejemplo1, /ejemplo2, /fichero'



welcomeMsg = "Bienvenido al Bot de ejemplo " + v



def init():
    global welcomeMsg
    utils.myLog(welcomeMsg)

def sendMsg2Admin(message):
    utils.myLog(message)
    if config.ADMIN_USER != None:
        TelegramBase.send_message(utils.getStrDateTime()+ " " + message, config.ADMIN_USER)
    else:
        utils.myLog('No admin user id')

def main():
    """Run the bot."""
    global update_id
    global chat_id

    init()

    bot = telegram.Bot(config.TELEGRAM_API_TOKEN)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    last_Beat = int(round(time.time() * 1000))

    sendMsg2Admin(welcomeMsg)

    while True:
        try:
            now = int(round(time.time() * 1000))
            if (now - last_Beat) > 60000: # 60 segundos
                utils.myLog('BotTest')
                last_Beat = now
            updateBot(bot)
        except NetworkError:
            time.sleep(0.1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1
        except KeyboardInterrupt:
            utils.myLog('Interrupted')
            sys.exit(0
        except Exception as e:
            utils.myLog('Excepcion!!: ' + str(e))

# Update and chat with the bot
def updateBot(bot):
    """Answer the message the user sent."""
    global update_id
    global chat_id


    #utils.myLog('Updating telegramBot')
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Proccess the incoming message
            comando = update.message.text  # message text
            command_time = update.message.date # command date 
            user = update.message.from_user #User full objetct
            chat_id = int(update.message.from_user.id)
            user_real_name = user.first_name #USER_REAL_NAME
            if chat_id not in config.ALLOWED_USERS:
                message = 'User: {} not allowed. Chat_id {} command: {}. Will be reported'.format( str(user_real_name), str(chat_id), comando)
                sendMsg2Admin(message)
                break
            TelegramBase.chat_ids[user_real_name] = [command_time,chat_id]
            utils.myLog('Command: '+comando+' from user ' + str(user_real_name )+' in chat id:' + str(chat_id)+ ' at '+str(command_time))
            if comando == '/start':
                update.message.reply_text(welcomeMsg, reply_markup=user_keyboard_markup)
            elif comando == 'hi':
                update.message.reply_text('Hello {}'.format(update.message.from_user.first_name), reply_markup=user_keyboard_markup)
            elif comando == '/info':
                answer = 'Info: ' + utils.getStrDateTime() + '\n==========================\n\n Detalles sobre el bot'
                update.message.reply_text(answer,parse_mode=telegram.ParseMode.MARKDOWN,reply_markup = user_keyboard_markup)
            elif comando == '/help':
                bot.send_message(chat_id = chat_id, text = commandList, reply_markup = user_keyboard_markup)
            elif comando == '/users':
                sUsers = TelegramBase.getUsersInfo()
                TelegramBase.send_message (sUsers,chat_id)
            elif comando == '/fichero':
                answer = 'FicheroQueDebeExistir.txt'
                utils.myLog(answer)
                TelegramBase.send_document(answer, chat_id)
                update.message.reply_text(answer,parse_mode=telegram.ParseMode.MARKDOWN,reply_markup = user_keyboard_markup)        
            elif comando.startswith('/Ejemplo'):
                numero = int(comando[7:])
                answer = 'Respuesta {} a Ejemplo{}'.format(numero,numero)
                utils.myLog(answer)
                update.message.reply_text(answer,parse_mode=telegram.ParseMode.MARKDOWN,reply_markup = user_keyboard_markup)
            else:
                update.message.reply_text('echobot: '+update.message.text, reply_markup=user_keyboard_markup)                

if __name__ == '__main__':
    main()
