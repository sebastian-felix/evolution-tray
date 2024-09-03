#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# C'est pas pubsub mais plutôt observer pattern
# dans pubsub il y aurait un troisième élément intermédiaire, un "message broker" 

from pyroute2 import IPRoute
from pyroute2.netlink.exceptions import NetlinkError


class Network:
    def __init__(self):
        self._is_network_down = False
        self._ip_has_changed = False
        self._state_has_changed = False
        _, self._previous_ip = self._check()

        self._subscribers_list = list()


    def subscribe(self, obj):
        if not hasattr(obj, "get_state"):
            raise Exception("L'objet doit avoir une méthode 'get_state' qui prend deux booléens en paramètre")

        self._subscribers_list.append(obj)
    

    def _publish(self):
        for obj in self._subscribers_list:
            obj.get_state(self._state_has_changed, self._is_network_down)
    

    def _check(self):
        _is_network_down = False
        _actual_ip = ""
        
        with IPRoute() as ip:
            try:
                route = ip.route('get', dst='8.8.8.8')[0]
            except NetlinkError:
                _is_network_down = True
        
            if not _is_network_down:
                _actual_ip = route.get_attr("RTA_PREFSRC")
        
        return _is_network_down, _actual_ip


    # Check si le réseau est up et si l'ip a changé depuis le check précédent
    def check(self):
        _ip_has_changed = False
        
        _is_network_down, _actual_ip = self._check()
        
        if not _is_network_down:
            _ip_has_changed = self._previous_ip != _actual_ip
        
        if (self._is_network_down, self._ip_has_changed) != (_is_network_down, _ip_has_changed):
            self._state_has_changed = True
        else:
            self._state_has_changed = False
        
        self._is_network_down, self._ip_has_changed = _is_network_down, _ip_has_changed
        self._previous_ip = _actual_ip
    
        self._publish()



