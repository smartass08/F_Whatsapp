from email import message_from_bytes
from email.header import decode_header
from imaplib import IMAP4_SSL
from re import findall
from time import sleep
from traceback import print_exc
from typing import List, Set

from decouple import config, Csv

from helpers.telegram import Telegram


# monstrous regex I found on stackoverflow
# this scares me but it works
_mail_regex = r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"


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

        # get all links from body
        self.links: Set[str] = set()
        for link in list(map(lambda x: x.strip(), config('Links-to-Check', cast=Csv()))):
            self.links.update([x for x in findall(_mail_regex, body) if link in x])


class MailService:
    """
    Class to represent a mail _service
    """

    def __init__(self):
        self._tg = Telegram()
        self._links_to_check = list(map(lambda x: x.strip(), config('Links-to-Check', cast=Csv())))

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
                        email.sender.replace("<", "&lt;").replace(">", "&gt;"), email.subject, "\n".join(email.links)
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
