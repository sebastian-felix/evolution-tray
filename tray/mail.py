#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from multiprocessing import Process
import threading
import time

from imapclient import IMAPClient
from tray.account_checker import AccountChecker
from tray.network import Network

from tray.evolution_accounts import EvolutionAccountsList

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('GSound', '1.0')

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Wnck
from gi.repository import AppIndicator3
from gi.repository import GSound


ICON_NO_MESSAGES = "mail-read-symbolic"
ICON_NEW_MESSAGES =  "mail-unread-symbolic"
SOUND_PATH = "/usr/share/sounds/freedesktop/stereo/message.oga"


class Indicator:
    def __init__(self): 
        self.indicator = AppIndicator3.Indicator.new("mails-unread", ICON_NO_MESSAGES, AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.accounts_list = list()
        self.messages_list = list()

        self.stop = False
        self._needs_reconnect = False
        self._previous_ip = ""

        self._create_menu()

        self.network = Network()
        self._add_accounts()
        self._start_network_check_thread()
        self._start_update_threads()
        self._start_change_status_thread()
        

    def _add_accounts(self):
        eal = EvolutionAccountsList()

        for params in eal:
            account = AccountChecker(params.host, params.user, params.password)
            self.accounts_list.append(account)
            self.network.subscribe(account)


    def _create_menu(self):
        self.menu = Gtk.Menu()

        # messages
        for msgid, msg in self.messages_list:
            item = Gtk.MenuItem(label=msg)
            item.connect("activate", self._launch_evolution)
            self.menu.append(item)

        if len(self.messages_list):
            self.menu.append(Gtk.SeparatorMenuItem())

            mark_read = Gtk.MenuItem(label="Tout marquer comme lu")
            mark_read.connect("activate", self._mark_read)
            self.menu.append(mark_read)

            self.menu.append(Gtk.SeparatorMenuItem())

        quitter = Gtk.MenuItem(label="Quitter")
        quitter.connect("activate", self._quit)
        self.menu.append(quitter)

        self.indicator.set_menu(self.menu)
        self.menu.show_all()


    def _start_update_threads(self):
        self._accounts_thread_list = list()

        for account in self.accounts_list:
            acc = threading.Thread(target=account.check)
            self._accounts_thread_list.append(acc)
            acc.daemon = True
            acc.start()


    def _start_change_status_thread(self):
        self.change_status_thread = threading.Thread(target=self._do_update_indicator)
        self.change_status_thread.daemon = True
        self.change_status_thread.start()


    def _start_check_state_thread(self):
        self.check_state_thread = threading.Thread(target=self._do_check_state_and_reconnect)
        self.check_state_thread.daemon = True
        self.check_state_thread.start()

    def _start_network_check_thread(self):
        self.network_check_thread = threading.Thread(target=self._do_network_check)
        self.network_check_thread.daemon = True
        self.network_check_thread.start()


    def _do_network_check(self):
        while not self.stop:
            GLib.idle_add(self.network.check)
            time.sleep(1)


    def _do_update_indicator(self):
        while not self.stop:
            GLib.idle_add(self._update_indicator)
            time.sleep(1)


    def _has_new_messages(self, new_messages):
        for msg in new_messages:
            if msg not in self.messages_list:
                return True
        return False


    # change l'icone et le menu
    def _update_indicator(self):
        new_messages_list = list()

        for account in self.accounts_list:
            new_messages_list += account.messages

        if new_messages_list != self.messages_list:
            if len(new_messages_list):
                self.indicator.set_icon_full(ICON_NEW_MESSAGES, "Nouveaux messages")
                if self._has_new_messages(new_messages_list):
                    self._play_sound()
            else:
                self.indicator.set_icon_full(ICON_NO_MESSAGES, "Pas de nouveau message")
            
            self.messages_list = new_messages_list

            # on recrée entièrement le menu
            self._create_menu()


    def _mark_read(self, args):
        for account in self.accounts_list:
            account.mark_all_read()


    def _launch_evolution(self, *args):
        screen = Wnck.Screen.get_default()
        screen.force_update()  # recommended per Wnck documentation

        window_list = screen.get_windows()

        evolution_started = False
        for w in window_list:
            if w.get_application().get_name() == "evolution":
                evolution_started = True
                w.make_above()
                break

        if not evolution_started:
            launcher = Process(target = self._do_launch_evolution, daemon=True)
            launcher.start()


    def _do_launch_evolution(self):
        subprocess.run(["evolution"])


    def _play_sound(self):
        ctx = GSound.Context()
        ctx.init()
        ctx.play_simple({ GSound.ATTR_EVENT_ID : "message" })
        GLib.usleep(100000) # nécessaire sinon pas joué

        
    def _quit(self, widget):
        # stop threads
        for account in self.accounts_list:
            account.stop()
        
        for acc in self._accounts_thread_list:
            acc.join()
        
        # stop rafraîchissement interface
        self.stop = True

        Gtk.main_quit()
        

def process_exists(cmd_line):
   
    pid_list = list()
    ret_val = False

    for dirname in os.listdir('/proc'):
        try:
            int(dirname)
        except Exception:
            # N'est pas un pid
            continue

        try:
            with open('/proc/{}/cmdline'.format(dirname), mode='rb') as fd:
                content = fd.read().decode().replace('\x00', " ")
        except FileNotFoundError:
            # Le processus peut ne plus exister à ce moment-là
            continue

        if cmd_line in content:
            content = content.split()
            if "python" in content[0]:
                pid_list.append(content)

    # quand le comptage est fait, la ligne de commande correspondant à l'exécution
    #   de ce fichier est déjà présente. Donc '> 1'
    if len(pid_list) > 1:
        ret_val = True

    return ret_val



def main():
    indicator = Indicator()
    Gtk.main()

def run():
    file_name = __file__.split("/")[-1]
    if process_exists(file_name):
        sys.exit(1)

    main()


if __name__ == "__main__":
    file_name = __file__.split("/")[-1]
    if process_exists(file_name):
        sys.exit(1)

    main()
