#!/usr/bin/env python3

import irc.bot
import threading

irc.client.ServerConnection.buffer_class.errors = 'replace'


class IRCClient(irc.bot.SingleServerIRCBot):
    def __init__(self, configuration):
        self.h_server = configuration["server"]
        self.h_port = int(configuration["port"])
        self.h_nickname = configuration["nickname"]
        self.h_channel = configuration["channel"]
        self.h_owner = configuration["owner"]
        self.h_cmd_prefix = configuration["cmd_prefix"]
        self.h_discord = None
        self.h_connection = None

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
        content = event.arguments[0].strip()

        # Don't reply to itself
        if username == self.h_nickname:
            pass

        # Admin commands
        if username == self.h_owner:
            pass

        self.h_send_to_discord(username, content)

    def h_send_to_discord(self, username, content):
        message = "<%s> : %s" % (username, content)
        print("[IRC] %s" % message)

        if content.startswith(self.h_cmd_prefix):
            self.h_discord.h_send_message("Cmd by %s :" % username)
            self.h_discord.h_send_message(content)
        else:
            self.h_discord.h_send_message(message)

    def h_send_message(self, message):
        self.h_connection.privmsg(self.h_channel, message)

    def h_format_text(self, message):
        # @TODO Bold, Underline, Strikethrough 
        return message
        
    def h_run(self):
        t = threading.Thread(target=self.start)
        t.daemon = True
        t.start()