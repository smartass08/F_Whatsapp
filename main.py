import logging
import asyncio
from helpers.wp import Whatsapp


async def lol(loop):
    whatsapp = Whatsapp(loop)
    await whatsapp.start()


def main():
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO,
                        datefmt="%H:%M:%S")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(lol(loop))


if __name__ == '__main__':
    main()
