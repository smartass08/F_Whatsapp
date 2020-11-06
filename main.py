import asyncio
import logging
from argparse import ArgumentParser

from helpers.mail import MailService
from helpers.wp import Whatsapp


if __name__ == '__main__':
    parser = ArgumentParser(description="Fetch meeting links and log them to telegram")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-w', '--whatsapp', help="Fetch meeting links from whatsapp", action='store_true')
    group.add_argument('-m', '--mail', help="Fetch meeting links from mail", action='store_true')
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    loop = asyncio.get_event_loop()

    if args.whatsapp:
        wp = Whatsapp(loop)
        loop.run_until_complete(wp.start())
    elif args.mail:
        MailService().log_new_meetings()
