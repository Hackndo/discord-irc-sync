#!/usr/bin/env python3

import json

from ircclient import IRCClient
from discordclient import DiscordClient

with open("config.json", encoding="utf-8") as f:
    settings = json.loads(f.read())

discord_client = DiscordClient(settings['discord'])
irc_client = IRCClient(settings['irc'])

discord_client.set_irc(irc_client)
irc_client.set_discord(discord_client)


irc_client.h_run()
discord_client.h_run()