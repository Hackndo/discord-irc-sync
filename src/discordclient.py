#!/usr/bin/env python3

import discord
import asyncio
import threading
from .formatting import D2IFormatter

class DiscordClient(discord.Client):
    def __init__(self, configuration):
        self.h_token = configuration['discord']['token']
        self.h_server_id = configuration['discord']['server']
        self.h_channel_id = configuration['discord']['channel']
        self.h_owner = configuration['discord']["owner"]
        self.h_cmd_prefix = configuration['discord']["cmd_prefix"]
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

        username = message.author.name
        if message.author.nick is not None:
            username = message.author.nick
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

    def h_send_to_irc(self, username, content):
        message = "<%s> : %s" % (username, content)

        if content.startswith(self.h_cmd_prefix):
            self.h_irc.h_send_message("Cmd by %s :" % username)
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
