#!/usr/bin/env python3

import discord
import asyncio
import threading
import re

from .formatting import D2IFormatter

class DiscordClient(discord.Client):
    def __init__(self, configuration):
        self.h_token = configuration['discord']['token']
        self.h_server_id = configuration['discord']['server']
        self.h_channel_id = configuration['discord']['channel']
        self.h_owner = configuration['discord']["owner"]
        self.h_cmd_prefix = configuration['discord']["cmd_prefix"]
        self.h_output_msg = configuration['discord']["output_msg"]
        self.h_output_cmd = configuration['discord']["output_cmd"]
        self.h_log_events = configuration['discord']["log_events"]
        self.h_formatter = D2IFormatter(configuration)
        self.h_channel = None
        self.h_irc = None

        super().__init__()

    def set_irc(self, irc):
        self.h_irc = irc

    async def on_ready(self):
        print("[Discord] Logged in as:")
        print("[Discord] " + self.user.name)

        if len(self.servers) == 0:
            print("[Discord] Bot is not yet in any server.")
            await self.close()
            return
        
        if self.h_server_id == "":
            print("[Discord] You have not configured a server to use in settings.json")
            print("[Discord] Please put one of the server IDs listed below in settings.json")
            
            for server in self.servers:
                print("[Discord] %s: %s" % (server.name, server.id))
            
            await self.close()
            return
        
        findServer = [x for x in self.servers if x.id == self.h_server_id]
        if not len(findServer):
            print("[Discord] No server could be found with the specified id: " + self.h_server_id)
            print("[Discord] Available servers:")
            
            for server in self.servers:
                print("[Discord] %s: %s" % (server.name, server.id))
                
            await self.close()
            return
        
        server = findServer[0]
        
        if self.h_channel_id == "":
            print("[Discord] You have not configured a channel to use in settings.json")
            print("[Discord] Please put one of the channel IDs listed below in settings.json")
            
            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    print("[Discord] %s: %s" % (channel.name, channel.id))
            
            await self.close()
            return
        
        find_channel = [x for x in server.channels if x.id == self.h_channel_id and x.type == discord.ChannelType.text]
        if not len(find_channel):
            print("[Discord] No channel could be found with the specified id: " + self.h_server_id)
            print("[Discord] Note that you can only use text channels.")
            print("[Discord] Available channels:")
            
            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    print("[Discord] %s: %s" % (channel.name, channel.id))
            
            await self.close()
            return
        
        self.h_channel = find_channel[0]

    async def on_message(self, message):
        """
        Don't reply to itself
        """
        if message.author == self.user:
            return

        """
        Only forward messages from configuration channel
        """
        if message.channel != self.h_channel:
            return

        username = self.get_nick(message.author)

        content = message.clean_content


        """
        Admin commands
        """
        if message.author.name == self.h_owner:
            if content == "!quit":
                await self.close()
                return

        """
        Send to IRC
        """
        for c in content.split('\n'):
            message = "<%s> : %s" % (username, c)
            print("[Discord] %s" % message)
            self.h_send_to_irc(username, self.h_format_text(c.strip()))

    async def on_member_join(self, member):
        """
        Don't update itself
        """
        if member == self.user:
            return

        """
        Don't log if not set
        """
        if not self.h_log_events:
            return

        username = self.get_nick(member)

        message = self.h_format_text("*%s* has joined the server" % username)

        self.h_raw_send_to_irc(message)


    async def on_member_remove(self, member):
        """
        Don't update itself
        """
        if member == self.user:
            return

        """
        Don't log if not set
        """
        if not self.h_log_events:
            return

        username = self.get_nick(member)

        message = self.h_format_text("*%s* has quit the server" % username)

        self.h_raw_send_to_irc(message)

    async def on_member_update(self, member_before, member_after):
        """
        Don't update itself
        """
        if member_before == self.user:
            return

        """
        Don't log if not set
        """
        if not self.h_log_events:
            return

        username_b = self.get_nick(member_before)
        username_a = self.get_nick(member_after)

        """
        Nick change
        """
        if username_a != username_b:
            message = self.h_format_text("*%s* is now known as *%s*" % (username_b, username_a))
            self.h_raw_send_to_irc(message)
        username = username_b

        """
        Status change
        """
        if member_before.status == discord.Status.offline and member_after.status != discord.Status.offline:
            message = self.h_format_text("*%s* has joined" % (username,))
            self.h_raw_send_to_irc(message)
        if member_before.status != discord.Status.offline and member_after.status == discord.Status.offline:
            message = self.h_format_text("*%s* has quit" % (username,))
            self.h_raw_send_to_irc(message)

    def get_nick(self, member):
        if member.nick is not None:
            return member.nick
        return member.name

    def hl_nicks(self, message):
        for client in self.get_all_members():
            nick = self.get_nick(client)
            message = re.sub(r'\b(' + nick + r')\b', client.mention, message, flags=re.IGNORECASE)
        return message

    def de_hl_nick(self, nick):
        special_chars = {
            'a':'а',
            'A':'А',
            'B':'В',
            'S':'Ѕ',
            'M':'М',
            'O':'О',
            'o':'о',
            'p':'р',
            'P':'Р',
            'c':'с',
            'y':'у',
            'x':'х',
            's':'ѕ',
            'i':'і',
            'j':'ј',
            'e':'е',
            '0':'ѳ',
            'h':'Һ'
        }
        output = [c for c in nick]
        for key, letter in enumerate(nick):
            if letter in special_chars:
                output[key] = special_chars[letter]
                return ''.join(output)
        return nick[0] + "'" + nick[1:]

    def h_raw_send_to_irc(self, message):
        print("[Discord] %s" % message)
        self.h_irc.h_send_message(message)

    def h_send_to_irc(self, username, content):
        message = self.h_output_msg.replace(":username:", self.de_hl_nick(username)).replace(":message:", content)

        if content.startswith(self.h_cmd_prefix):
            self.h_irc.h_send_message(self.h_output_cmd.replace(":username:", username))
            self.h_irc.h_send_message(content)
        else:
            self.h_irc.h_send_message(message)

    def h_send_message(self, message):
        asyncio.run_coroutine_threadsafe(self.h_send_message_async(message), self.loop)

    async def h_send_message_async(self, message):
        await self.send_message(self.h_channel, message)

    def h_format_text(self, message):
        return self.h_formatter.format(message)

    def h_run(self):
        self.run(self.h_token)
