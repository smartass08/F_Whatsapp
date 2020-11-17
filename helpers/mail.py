from email import message_from_bytes
from email.header import decode_header
from imaplib import IMAP4_SSL
from re import compile, sub
from time import sleep
from traceback import print_exc
from typing import List, Set

from decouple import config, Csv

from helpers.telegram import Telegram


# monstrous regex I found on stackoverflow
# this scares me but it works


class Email:
    """
    Class to represent a single email
    """

    def __init__(self, mail_bytes: bytes):
        """
        Initialize the object
        :param mail_bytes: bytes object representing the mail
        """
        email = message_from_bytes(mail_bytes)

        # get sender
        self.sender, _ = decode_header(email.get('From'))[0]
        if isinstance(self.sender, bytes):
            self.sender = self.sender.decode('utf-8')

        # get subject
        self.subject = decode_header(email['Subject'])[0][0]
        if isinstance(self.subject, bytes):
            self.subject = self.subject.decode('utf-8')

        # get message body
        if email.is_multipart():
            body = ""
            for part in email.walk():
                if "text" in part.get_content_type():
                    try:
                        body += part.get_payload(decode=True).decode('utf-8')
                    except:
                        continue
        else:
            body = email.get_payload(decode=True).decode('utf-8')

        send: bool = True
        # Check if any filter mode is enabled
        filter_mode = config('Filter-Mode', None)
        if filter_mode:
            # If we have any filters, assume message shouldn't be sent
            send = False
            if filter_mode == 'blacklist':
                # Retrieve a comma-separate list of disallowed text
                disallowed_text = config('blacklist', cast=Csv(cast=lambda x: x.lower(), strip=' %*'))
                for text in disallowed_text:
                    # If any of the disallowed phrases are in the links, do not send the message
                    if text in body:
                        send = False
                        break
            else:
                # Retrieve a comma-separate list of disallowed text
                allowed_text = config('whitelist', cast=Csv(cast=lambda x: x.lower(), strip=' %*'))
                for text in allowed_text:
                    # If any of the allowed phrases are in the message content, send the message
                    if text in body:
                        send = True
                        break

        mail_regex = compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+%]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        links_to_check = config('Links-to-Check', cast=Csv(cast=lambda x: x.lower(), strip=' %*'))
        meeting_regex = compile(f"^http[s]?://(?!www.google.com).*({'|'.join(links_to_check)}).+")

        if send:
            # get all needed links from body
            self.links: Set[str] = set(
                sub(r"(<.+>.*|<|>)", "", x) for x in mail_regex.findall(body) if meeting_regex.match(x.lower())
            )
        else:
            self.links = set()


class MailService:
    """
    Class to represent a mail _service
    """

    def __init__(self):
        self._tg = Telegram()
        self._links_to_check = config('Links-to-Check', cast=Csv(strip=' %*'))

        self._service = IMAP4_SSL(config('Email-IMAP'))
        status, _ = self._service.login(config('Email-ID'), config('Email-Password'))  # login

    def _get_new_meetings(self) -> List[Email]:
        """
        Fetch all the unread emails
        :return: List of all unread email objects
        """
        # fetch unread emails
        print("fetching unread mails")
        self._service.select('inbox')
        status, mail_ids = self._service.search(None, '(UNSEEN)')

        # format all mails into Email objects
        mails = []  # list of all mails to be logged
        all_mails = mail_ids[0].decode('utf-8').split()  # list of all unread mails
        for n, mail_id in enumerate(all_mails):
            # fetch the mail
            print(f"fetching mail {n+1}/{len(all_mails)}")
            status, mail_content = self._service.fetch(mail_id, '(RFC822)')
            if status != "OK":
                continue

            for content in mail_content:
                if isinstance(content, tuple):
                    email = Email(content[1])
                    if email.links:
                        mails.append(email)
                    else:
                        # mark the mail as unread
                        self._service.store(mail_id, '-FLAGS', r'\SEEN')

        return mails

    def log_new_meetings(self):
        """
        Function to log all unread mails with meeting links to telegram channel
        """
        while True:
            mails = self._get_new_meetings()
            for n, email in enumerate(mails):
                try:
                    print(f"logging mail {n+1}/{len(mails)}")
                    response = self._tg.log_link(
                        email.sender.replace("<", "&lt;").replace(">", "&gt;"), email.subject, "\n\n".join(email.links)
                    )
                    if response.status != 200:
                        self._tg.log_message(
                            f"<b>New invite link failed to deliver!\nCheck mail asap</b>\n\n"
                            f"response status = <code>{response.status}</code>\n"
                            f"response data = <code>{response.data.decode('utf-8')}</code>\n"
                        )
                except Exception as e:
                    self._tg.log_message(
                        f"New invite link failed to deliver!\nCheck mail asap\n\nerror log_message = <code>{e}</code>"
                    )
                    print_exc()

            sleep(3)
