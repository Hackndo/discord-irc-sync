#!/usr/bin/env python3
# coding: utf-8

import irc.bot
import threading
import time
import ssl

from .formatting import I2DFormatter

irc.client.ServerConnection.buffer_class.errors = 'replace'


class IRCClient(irc.bot.SingleServerIRCBot):
    def __init__(self, configuration):
        self.h_server = configuration['irc']["server"]
        self.h_port = int(configuration['irc']["port"])
        self.h_ssl = configuration['irc']['ssl']
        self.h_nickname = configuration['irc']["nickname"]
        self.h_channel = configuration['irc']["channel"]
        self.h_owner = configuration['irc']["owner"]
        self.h_cmd_prefix = configuration['irc']["cmd_prefix"]
        self.h_log_events = configuration['irc']["log_events"]
        self.h_output_msg = configuration['irc']["output_msg"]
        self.h_output_cmd = configuration['irc']["output_cmd"]
        self.h_formatter = I2DFormatter(configuration)
        self.h_discord = None
        self.h_connection = None

        if self.h_ssl:
            ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
            super().__init__([(self.h_server, self.h_port)], self.h_nickname, self.h_nickname, connect_factory=ssl_factory)
        else:
            super().__init__([(self.h_server, self.h_port)], self.h_nickname, self.h_nickname)

    def set_discord(self, discord):
        self.h_discord = discord

    def on_welcome(self, server, event):
        self.h_connection = server
        server.join(self.h_channel)
        print("[IRC] Logged in as:")
        print("[IRC] %s" % self.h_nickname)

    def on_pubmsg(self, server, event):
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
        if event.source.nick == self.h_nickname or not self.h_log_events:
            return
        message = "*%s* has joined the channel" % event.source.nick
        self.h_raw_send_to_discord(message)

    def on_part(self, server, event):
        if event.source.nick == self.h_nickname or not self.h_log_events:
            return
        reason = "*"
        if len(event.arguments) > 0:
            reason = event.arguments[0]
        message = "*%s* has left the channel (%s)" % (event.source.nick, reason)
        self.h_raw_send_to_discord(message)

    def on_quit(self, server, event):
        if event.source.nick == self.h_nickname or not self.h_log_events:
            return
        reason = "*"
        if len(event.arguments) > 0:
            reason = event.arguments[0]
        message = "*%s* has quit the channel (%s)" % (event.source.nick, reason)
        self.h_raw_send_to_discord(message)

    def on_kick(self, server, event):
        reason = "*"
        if len(event.arguments) > 1:
            reason = event.arguments[1]
        if self.h_log_events:
            message = "*%s* has been kicked of the channel (%s)" % (event.arguments[0], reason)
            self.h_raw_send_to_discord(message)
        time.sleep(2)
        server.join(self.h_channel)

    def h_send_to_discord(self, username, content):
        message = self.h_output_msg.replace(":username:", username).replace(":message:", content)
        print("[IRC] %s" % message)

        if content.startswith(self.h_cmd_prefix):
            self.h_discord.h_send_message(self.h_output_cmd.replace(":username:", username))
            self.h_discord.h_send_message(content)
        else:
            self.h_discord.h_send_message(message)

    def h_raw_send_to_discord(self, message):
        print("[IRC] %s" % message)
        self.h_discord.h_send_message(message)

    def h_send_message(self, message):
        self.h_connection.privmsg(self.h_channel, message)

    def h_format_text(self, message):
        return self.h_formatter.format(message)
        
    def h_run(self):
        t = threading.Thread(target=self.start)
        t.daemon = True
        t.start()
