#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import configparser
import secretstorage

from tray.config import Config


class EvolutionAccountsList:
    def __init__(self, dirpath=Config.EVOLUTION_CONFIG_DIR):
        self._dirpath = dirpath
        self._accounts = list()
        self._get_accounts()


    def _get_accounts(self):
        conn = secretstorage.dbus_init()
        sec_coll = secretstorage.get_default_collection(conn)

        for filepath in self._get_sources_files_list():
            account = EvolutionAccount(filepath)
            
            if account.has_authentication:
                account.get_password(sec_coll)
                self._accounts.append(account)
        
        conn.close()
        

    def _get_sources_files_list(self):
        for entry in os.scandir(self._dirpath):
            if not entry.name.startswith('.') and entry.is_file():
                yield entry.path
    

    def __iter__(self):
        self._n = 0
        return self
    

    def __next__(self):
        if self._n < len(self._accounts):
            item = self._accounts[self._n]
            self._n += 1
            return item
        else:
            raise StopIteration
    
            

class EvolutionAccount:
    def __init__(self, filepath):
        self.filepath = filepath

        self.uid = os.path.splitext(os.path.split(filepath)[1])[0]
        self.name = None

        self.host = None
        self.port = None
        self.user = None
        self.password = None

        self.has_parent = False
        self.is_enabled = None
        self.has_authentication = None

        self.is_goa = False

        self.read_config()
    

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.filepath)

        self.name = config["Data Source"]["DisplayName"]
        self.has_parent = config["Data Source"]["parent"] != ""
        self.is_enabled = config["Data Source"]["Enabled"]

        # Je m'occupe que du SMTP pour l'instant
        self.is_goa = "GNOME Online Accounts" in config

        if not self.has_parent and self.is_enabled and not self.is_goa:
            if "Authentication" in config:
                self.has_authentication = True
                self.host = config["Authentication"]["Host"]
                self.port = config["Authentication"]["Port"]
                self.user = config["Authentication"]["User"]
    

    def get_password(self, secret_collection):
        if self.has_authentication:
            res =  list(secret_collection.search_items({"e-source-uid": self.uid}))
            if len(res) == 1:
                self.password = res[0].get_secret().decode()
            else:
                raise Exception("Impossible de récupérer le mote de passe pour {}".format(self.uid))


if __name__ == "__main__":
    acclist = EvolutionAccountsList()

    for acc in acclist:
        print(acc.name, acc.host, acc.port, acc.user, acc.password)
