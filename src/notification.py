#!/usr/bin/env python3


class Notification(object):
    """docstring for Notification"""

    def __init__(self, n_type, subtype=None, message=None, user=None, dest_user=None):
        self.allowed_types = ["notification", "message", "raw_message", "quit", "join"]
        self.src_user = None
        self.dst_user = None
        self.message = None
        self.n_type = None
        self.subtype = None
        self.allowed_types = {
            "notification": ["nick_in_use", "bot_created", "bot_killed", "bot_ch_nick"],
            "message": ["raw"],
            "query": [],
            "quit": [],
            "part": [],
            "join": [],
            "kick": [],
            "user": ["join", "quit", "change_nick"],
        }

        if n_type not in self.allowed_types.keys():
            print('the notification "' + n_type + '" is not yet implemented.')
            return
        else:
            if subtype is not None:
                if subtype not in self.allowed_types[n_type]:
                    print('the subtype "' + subtype + '" is not yet implemented.')
                    return
            else:
                subtype = "default"

            self.n_type = n_type
            self.src_user = user
            self.dst_user = dest_user
            self.message = message
            self.subtype = subtype

    def __str__(self):
        return (
            "Type: " + str(self.n_type) + "\r\n"
            "Subtype: " + str(self.subtype) + "\r\n"
            "Src User: " + str(self.src_user) + "\r\n"
            "Dst User: " + str(self.dst_user) + "\r\n"
            "Msg: " + str(self.message)
        )
