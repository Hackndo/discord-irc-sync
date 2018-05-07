#!/usr/bin/env python3

import json
import src.utils
import sys

from src.ircclient import IRCClient
from src.discordclient import DiscordClient
from src import utils


config_file = sys.argv[1] if len(sys.argv) == 2 else None
settings = utils.read_config(config_file)

settings['irc']['master_bot'] = True
discord_client = DiscordClient(settings)
irc_client = IRCClient(settings)

discord_client.set_irc(irc_client)
irc_client.set_discord(discord_client)


irc_client.h_run()
discord_client.h_run()
