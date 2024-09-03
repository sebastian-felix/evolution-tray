#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

class Config:
    # temps en secondes avant renouvellement de la connexion avec le serveur
    IDLE_TIMEOUT = 900

    # interval de check de la présence de nouveaux emails (n'implique pas d'échange supplémentaire avec le serveur)
    IDLE_CHECK_TIMEOUT = 1

    # répertoire des comptes d'Evolution
    EVOLUTION_CONFIG_DIR = os.path.expanduser("~/.config/evolution/sources/")
