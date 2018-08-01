#!/usr/bin/env python3
# coding: utf-8

import irc.bot
import threading
import time
import ssl
from . import utils
from .notification import Notification

from .formatting import I2DFormatter

irc.client.ServerConnection.buffer_class.errors = 'replace'


class IRCClient(irc.bot.SingleServerIRCBot):
    def __init__(self, configuration):
        self.h_server     = configuration['irc']["server"]
        self.h_port       = int(configuration['irc']["port"])
        self.h_ssl        = configuration['irc']['ssl']
        self.h_nickname   = configuration['irc']["nickname"]
        self.h_channel    = configuration['irc']["channel"]
        self.h_owner      = configuration['irc']["owner"]
        self.h_cmd_prefix = configuration['irc']["cmd_prefix"]
        self.h_log_events = configuration['irc']["log_events"]
        self.h_output_msg = configuration['irc']["output_msg"]
        self.h_output_cmd = configuration['irc']["output_cmd"]
        self.h_formatter  = I2DFormatter(configuration)
        self.h_discord    = None
        self.h_connection = None
        self.master_bot   = False
        self.callback     = {
        'notification'    : {
            'nick_in_use' :self.unimplemented},
        'message'         : {
            'default'     :self.h_send_message,
            'raw'         :self.h_send_message},
        'user'            : {
            'default'     :self.unimplemented,
            'join'        :self.on_dsc_join,
            'quit'        :self.on_dsc_quit,
            'change_nick' :self.on_dsc_change_nick},
        }

        if 'master_bot' in configuration['irc'].keys():
            self.master_bot = configuration['irc']["master_bot"]

        if self.h_ssl:
            ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            super().__init__([(self.h_server, self.h_port)], self.h_nickname, self.h_nickname, connect_factory=ssl_factory)
        else:
            super().__init__([(self.h_server, self.h_port)], self.h_nickname, self.h_nickname)

    def unimplemented(self, notif):
        print(notif)
        print('This feature is not yet implemented')

    def on_dsc_quit(self, notif):
        if self.master_bot is False:
            self.disconnect()
            self.h_send_notification('notification', 'bot_killed', None, notif.src_user)

    def on_dsc_change_nick(self, notif):
        if self.master_bot is False:
            self.h_connection.nick(notif.dst_user)
            self.h_nickname =  notif.dst_user
            self.h_send_notification('notification', 'bot_ch_nick', None, notif.src_user, notif.dst_user)

    def on_dsc_join(self, notif):
        conf = utils.read_config()
        conf['irc']['nickname'] = notif.src_user
        irc_client = IRCClient(conf)
        irc_client.set_discord(self.h_discord)
        irc_client.h_run()

    def set_discord(self, discord):
        self.h_discord = discord

    def on_welcome(self, server, event):
        self.h_connection = server
        server.join(self.h_channel)
        print("[IRC] Logged in as:")
        print("[IRC] %s" % self.h_nickname)
        if self.master_bot is False:
            # notify dsc that the user is OK only when it's connected to the chan
            self.h_send_notification('notification', 'bot_created', self, self.h_nickname)

    def on_pubmsg(self, server, event):
        username = event.source.nick
        content = self.h_format_text(self.h_discord.hl_nicks(event.arguments[0]).strip())

        """
        Don't reply to itself
        """
        if username == self.h_nickname:
            return

        """
        Admin commands
        """
        if username == self.h_owner:
            pass

        self.h_send_to_discord(username, content)

    def on_action(self, server, event):
        username = event.source.nick
        content = self.h_format_text(event.arguments[0].strip())

        """
        Don't reply to itself
        """
        if username == self.h_nickname:
            return

        """
        Admin commands
        """
        if username == self.h_owner:
            pass

        self.h_raw_send_to_discord("\\* **" + username + "** " + content)


    def on_join(self, server, event):
        if event.source.nick == self.h_nickname:
            return
        if self.h_log_events:
            message = "*%s* has joined the channel" % event.source.nick
            self.h_send_notification('message', 'raw', message, event.source.nick)
            self.h_send_notification('join', None, message, event.source.nick)

    def on_part(self, server, event):
        if event.source.nick == self.h_nickname:
            return
        reason = "*"
        if len(event.arguments) > 0:
            reason = event.arguments[0]
        if self.h_log_events:
            message = "*%s* has left the channel (%s)" % (event.source.nick, reason)
            self.h_send_notification('message', 'raw', message, event.source.nick)
            self.h_send_notification('part', None, message, event.source.nick)

    def on_quit(self, server, event):
        if event.source.nick == self.h_nickname:
            return
        reason = "*"
        if len(event.arguments) > 0:
            reason = event.arguments[0]
        if self.h_log_events:
            message = "*%s* has quit the channel (%s)" % (event.source.nick, reason)
            self.h_send_notification('message', 'raw', message, event.source.nick)
            self.h_send_notification('quit', None, message, event.source.nick)


    def on_kick(self, server, event):
        reason = "*"
        if len(event.arguments) > 1:
            reason = event.arguments[1]
        if self.h_log_events:
            message = "*%s* has been kicked of the channel (%s)" % (event.arguments[0], reason)
            self.h_send_notification('message', 'raw', message, event.arguments[0])
            self.h_send_notification('kick', None, message, event.arguments[0])
        time.sleep(2)
        server.join(self.h_channel)

    def on_nicknameinuse(self, server, event):
        if self.master_bot is True:
            server.nick((self.h_nickname + "_"))
            self.h_nickname = self.h_nickname+'_'
        else:
            # user bot. If the nickname is already in use, we suppose that the user is connected onto DSC & IRC
            # so we just kill the connection and notify the discord class, in order to drop it from the list
            print('User already in use on IRC. Killing thread & notifying the discord class')
            self.h_send_notification('notification', 'nick_in_use', None, self.h_nickname)
            self.die()

    def h_send_to_discord(self, username, content):
        if self.master_bot is True:
            message = self.h_output_msg.replace(":username:", username).replace(":message:", content)
            print("[IRC] %s" % message)

            if content.startswith(self.h_cmd_prefix):
                self.h_send_notification('message', 'raw', self.h_output_cmd.replace(":username:", username), username)
                self.h_send_notification('message', 'raw', content, username)
            else:
                self.h_send_notification('message', None, content, username)

    def h_raw_send_to_discord(self, message):
        if self.master_bot is True:
            print("[IRC] %s" % message)
            self.h_send_notification('message', 'raw', message, None)

    # notification system

    def h_send_notification(self, n_type, subtype=None, content=None, username=None, dst_username=None):
        notif = Notification(n_type, subtype, content, username, dst_username)
        self.h_discord.get_notification(notif)

    def get_notification(self, notif):
        self.callback[notif.n_type][notif.subtype](notif)

    # irc sending

    def h_send_message(self, notif):
        if self.master_bot is True or self.h_nickname == notif.src_user:
            self.h_connection.privmsg(self.h_channel,notif.message)

    def h_format_text(self, message):
        return self.h_formatter.format(message)

    def h_run(self):
        t = threading.Thread(target=self.start)
        t.daemon = True
        t.start()
