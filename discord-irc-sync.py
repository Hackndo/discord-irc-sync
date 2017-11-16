#!/usr/bin/env python3

import json
import os
import sys

from src.ircclient import IRCClient
from src.discordclient import DiscordClient

config_file = os.path.join("config", "config.json")

if len(sys.argv) == 2:
    config_file = sys.argv[1]

if not os.path.isfile(config_file):
    sys.exit("File %s doesn't exist" % config_file)

with open(config_file, encoding="utf-8") as f:
    settings = json.loads(f.read())

discord_client = DiscordClient(settings)
irc_client = IRCClient(settings)

discord_client.set_irc(irc_client)
irc_client.set_discord(discord_client)


irc_client.start()
irc_client.h_run()
discord_client.h_run()
