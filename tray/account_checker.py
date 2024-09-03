#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mets en idle
# si durée idle > 15 minutes, logout et reconnecte

# mettre dans thread

import threading

from imapclient import IMAPClient, SocketTimeout, SEEN
import email.header
import time

from tray.config import Config


class AccountChecker(threading.Thread):
    def __init__(self, host, username, password):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password

        self.messages = list()

        self.socket_timeout = SocketTimeout(connect=10, read=5) # timeout en secondes sur le socket
        self.idle_timeout = Config.IDLE_TIMEOUT # pour renouvellement low level connections
        self._idle_check_timeout = Config.IDLE_CHECK_TIMEOUT # C'est un:  while not timeout: socket.poll (pas d'échanges avec le serveur)
        
        self._server = None

        self._stop_check = False
        self._network_is_down = False
        self._needs_reconnect = True
        self._mark_has_read = False


    def get_state(self, state_has_changed, is_network_down):
        self._network_is_down = is_network_down

        if state_has_changed:
            self._needs_reconnect = True


    def check(self):
        self._reconnect_if_needed()

        while True:
            try:
                self._idle_check()
            except Exception as e:
                self._needs_reconnect = True
            
            self._reconnect_if_needed()
                
            if self._stop_check:
                break

        self._server.logout()
    

    def mark_all_read(self):
        self._mark_has_read = True


    def stop(self):
        self._stop_check = True


    def _connect_and_fetch(self):
        self._server = IMAPClient(self.host, timeout=self.socket_timeout)
        self._server.login(self.username, self.password)

        self._server.select_folder('INBOX')

        self._fetch_unseen()


    # suite à timeout sur self._server.idle_done()
    # je suppose qu'il faut se reconnecter
    def _reconnect_if_needed(self, idle=False):
        nbr_tentatives = 0
        
        while self._needs_reconnect:
            if not self._network_is_down:
                nbr_tentatives += 1
                try:
                    self._server.idle_done()
                    self._server.logout()
                except:
                    pass

                try:
                    self._connect_and_fetch()
                    if idle:
                        self._server.idle()
                    self._needs_reconnect = False
                except Exception as e:
                    print("Sleeping {}".format(pow(nbr_tentatives, 3)))
                    time.sleep((pow(nbr_tentatives, 3)))
            else:
                time.sleep(1)


    # La boucle principale
    def _idle_check(self):
        started_at = time.time()
        self._server.idle()
    
        while True:
            response = self._server.idle_check(timeout=self._idle_check_timeout)

            if response:
                if not response ==  [(b'OK', b'Still here')]:
                    self._fetch_unseen(idle=True)

            if self._needs_reconnect:
                break

            if self._mark_has_read:
                self._messages_seen(idle=True)
                

            if self._stop_check or time.time() - started_at > self.idle_timeout:
                self._server.idle_done()
                break
        
        
    def _messages_seen(self, idle=False):
        if len(self.messages):
            if idle:
                self._server.idle_done()

            for msgid, _ in self.messages:
                self._server.add_flags(msgid, [SEEN])

            self._fetch_unseen()

            if idle:
                self._server.idle()
        
        self._mark_has_read = False

    def _fetch_unseen(self, idle=False):
        if idle:
            self._server.idle_done()

        self.messages = list()
        non_lus = self._server.search('UNSEEN')

        for msgid, data in self._server.fetch(non_lus, ['ENVELOPE']).items():
            envelope = data[b'ENVELOPE']
            subject = self._decode_header(envelope.subject.decode())
            user = self.username.split("@")[0]
            msg_str = "{user} - '{subject}' de  {from_}".format(user=user, subject=subject, from_=envelope.from_[0].mailbox.decode() + "@" + envelope.from_[0].host.decode())
            self.messages.append((msgid, msg_str))
        
        if idle:
            self._server.idle()


    def _decode_header(self, txt):
        result = ""

        for part in email.header.decode_header(txt):
            if not part[1]:
                if isinstance(part[0], bytes):
                    result += part[0].decode()
                else:
                    result += part[0]
            else:
                result += part[0].decode(part[1])
        
        return result
