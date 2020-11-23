import logging
import os

import pymongo
from decouple import config


class DB:
    def __init__(self):
        self.__dblink = config('DB')
        self.__db = self.config()
        if not os.path.exists(os.path.join(".", "firefox_cache")):
            os.makedirs(os.path.join(".", "firefox_cache"))
        self.__json = "{}/{}".format(os.path.join(".", "firefox_cache"), "localStorage.json")

    def config(self):
        client = pymongo.MongoClient(self.__dblink)
        return client.access

    def get_json_db(self):
        cursor = self.__db.json.find()
        for c in cursor:
            return c.get("access_token")
        return ""

    def add_json(self):
        logging.info("Adding access token to DB")
        with open(self.__json) as f:
            data = f.read()
        previous_token = self.get_json_db()
        cur_filter = {"access_token": previous_token}
        self.__db.json.update_one(cur_filter, {'$set': {"access_token": data}}, upsert=True)

    def save_json(self):
        try:
            os.remove(self.__json)
        except Exception:
            logging.info("No access token found on local")
        logging.info("Getting access token from the DB")
        data = self.get_json_db()
        if len(data) == 0:
            logging.info("No access token found in DB, Assuming first time run")
            return
        file = open(self.__json, "w+")
        file.write(data)
