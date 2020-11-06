from decouple import config
from urllib3 import PoolManager
from urllib3.exceptions import ProtocolError

manager = PoolManager()  # create PoolManager object


class Telegram:
    def __init__(self):
        self.__bot_token = config('Bot-Token')
        self.__channel_id = config('Channel-ID')

    # function to log text messages to telegram channel
    def send_message(self, chat_id, message, parse_mode="HTML", **kwargs):
        # chat_id - ID of channel to which text log_message is to be logged
        # log_message - the content of the text log_message to be logged
        # parse_mode - what the text log_message is to be parsed as, defaults to HTML

        # create dictionary with all information passed as arguments to be passed to __send__ function
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
        }
        data.update(kwargs)

        try:
            # POST call to telegram API
            return manager.request("POST", f"https://api.telegram.org/bot{self.__bot_token}/sendMessage", fields=data)
        except ProtocolError as e:
            print(e, e.__class__)

    def log_message(self, message):
        self.send_message(self.__channel_id, message, parse_mode="HTML")

    def log_link(self, name, info, message):
        msg = f"<b>New Invite Arrived!</b>\n{name} | {info}\n\n{message}"
        self.send_message(self.__channel_id, msg, parse_mode="HTML", disable_web_page_preview=True)
