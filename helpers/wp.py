import asyncio
import os
from re import compile, sub
from signal import SIGINT

from decouple import config, Csv
from webwhatsapi.async_driver import WhatsAPIDriverAsync
from webwhatsapi.objects.message import Message

from helpers.DB import DB
from helpers.telegram import Telegram


class Whatsapp:
    def __init__(self, loop):
        self._links_to_check = config('Links-to-Check', cast=Csv(strip=' %*', cast=lambda x: x.lower()))
        self._loop = loop
        self._db = DB()
        self._driver = None
        self._tg = Telegram()
        self.is_cancelled = False
        self._config_dir = os.path.join(".", "firefox_cache")
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir)

    async def make(self):
        self._db.save_json()
        await self.sleep(10)
        self._driver = WhatsAPIDriverAsync(
            loadstyles=True,
            loop=self._loop,
            profile=self._config_dir,
            client="remote",
            command_executor=os.environ["SELENIUM"],
        )

    async def sleep(self, sleep_time):
        await asyncio.sleep(sleep_time, loop=self._loop)

    async def start(self):
        await self.make()
        self._loop.add_signal_handler(SIGINT, self.stop)
        task1 = self.monitor_messages()
        await asyncio.wait([task1], loop=self._loop)

    async def monitor_messages(self):
        print(self._links_to_check)
        print("Connecting...")
        await self._driver.connect()
        print("Wait for login...")
        # get qr code
        login_status = await self._driver.wait_for_login()
        if not login_status:
            filepath = await self._driver.get_qr()
            print("The QR is at", filepath.replace("/tmp", "qrs"))
        # wait for user to login
        while not login_status:
            print("Wait for login...")
            login_status = await self._driver.wait_for_login()
        await self._driver.save_firefox_profile(remove_old=True)
        self._db.add_json()
        while True:
            try:
                print("Checking for more messages, status", await self._driver.get_status())
                for cnt in await self.get_unread_messages():
                    if self.is_cancelled:
                        break
                    for message in cnt.messages:
                        if isinstance(message, Message):
                            shit = message.get_js_obj()
                            name = message.sender.push_name
                            if name is None:
                                name = message.sender.get_safe_name()
                            chat = shit['chat']['contact']['formattedName']

                            mail_regex = compile(
                                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
                            )
                            links_to_search = compile(f".*({'|'.join(self._links_to_check)}).+")

                            # get all links in the message that we are checking for
                            links = set(
                                sub(r"(<.+>|<|>)", "", x)
                                for x in mail_regex.findall(message.content)
                                if links_to_search.match(x.lower())
                            )

                            # By default, message should be sent
                            send: bool = True
                            if links:
                                filter_mode = config('Filter-Mode', None)
                                if filter_mode:
                                    # If we have any filters, assume message shouldn't be sent
                                    send = False
                                    if filter_mode == 'blacklist':
                                        # Retrieve a comma-separate list of disallowed text
                                        disallowed_text = config('blacklist', cast=Csv(cast=lambda x: x.lower(), strip=' %*'))
                                        for text in disallowed_text:
                                            # If any of the disallowed phrases are in the message content, do not send the message
                                            if text in message.content:
                                                send = False
                                                break
                                    else:
                                        # Retrieve a comma-separate list of disallowed text
                                        allowed_text = config('whitelist', cast=Csv(cast=lambda x: x.lower(), strip=' %*'))
                                        for text in allowed_text:
                                            # If any of the allowed phrases are in the message content, send the message
                                            if text in message.content:
                                                send = True
                                                break
                                try:
                                    if send:
                                        self._tg.log_link(chat, name, message.content)
                                except Exception as e:
                                    self._tg.log_message(
                                        f"New invite link failed to deliver!, Check phone asap | error log_message = {e}"
                                    )
            except Exception as e:
                print(e)
                continue

            await self.sleep(3)

    def stop(self, *args, **kwargs):
        self.is_cancelled = True

    async def get_unread_messages(self):
        cnts = []
        for contact in await self._driver.get_unread():
            print(f"Found Contact: {contact}")
            cnts.append(contact)
        return cnts
