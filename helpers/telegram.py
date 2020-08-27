import configparser

from telegram.ext import Updater


class Telegram:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__bot_token = config['config']['Bot-Token']
        self.__channel_id = config['config']['Channel-ID']
        self.__service = self.service()

    def service(self):
        updater = Updater(token=self.__bot_token, use_context=True)
        return updater.dispatcher

    def message(self, message):
        chat = self.__service.bot.getChat(self.__channel_id)
        chat.send_message(message)

    def msg_channel(self, name, info, message):
        chat = self.__service.bot.getChat(self.__channel_id)
        msg = f"<b>New Invite Arrived!</b>\n{name} | {info}\n\n{message}"
        chat.send_message(msg, parse_mode="HTML", disable_web_page_preview=True)


