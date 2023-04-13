# Discord-IRC Synchronization

Description
-----------

**Python3.5+** implementation of a synchronization between IRC and Discord

![discordirc](https://user-images.githubusercontent.com/11051803/32892891-f7e0b216-cad7-11e7-8938-e23d82ef0c60.gif)


Requirements
------------

* Python 3.5+
* Discord Bot

Discord Bot
-----------

1. Go to [Discord developer application](https://discord.com/developers/applications)
2. Add a new application
3. Create a Bot User
4. Follow https://discordapp.com/oauth2/authorize?&client_id=CLIENT_ID&scope=bot&permissions=0 with your application **Client ID**
5. Choose your server

Then, enable `Message Content Intent` by navigating to your bot page (https://discord.com/developers/applications then choose your bot), under the bot menu, enable the `Message Content Intent` parameter so the bot can read messages and transfer them to IRC.

Initialization
--------------

```sh
git clone git@github.com:Hackndo/discord-irc-sync.git
cd discord-irc-sync
mkvirtualenv discordirc -p $(which python3)
pip install -r requirements.txt
```

Configuration
-------------

Copy configuration template

```sh
cp config/config.json.dist config/config.json
```

Configuration file looks like this

```javascript
{
    "irc": {
        "server": "irc.server.com",                 // IRC Server
        "port": "6667",                             // IRC Port
        "ssl": false,                               // Use SSL
        "channel": "#channel",                      // IRC Channel
        "nickname": "h_bot",                        // Bot Nickname
        "owner": "username",                        // Bot Owner Nickname (admin commands)
        "cmd_prefix": "!",                          // Channel commands prefix (if any)
        "output_msg": "<:username:> :message:",     // Message format when IRC message is received
        "output_cmd": "CMD by :username:",          // Message format when IRC command is received
        "log_events": true                          // Send part/join/kick/quit to discord
    },
    "discord": {
        "server": <server id>,                      // Discord Server ID
        "channel": <channel id>,                    // Discord Channel ID
        "token": "<bot token>",                     // Discord Bot Token
        "owner": "username",                        // Discord Bot Owner username (admin commands)
        "cmd_prefix": "!",                          // Channel commands prefix (if any)
        "output_msg": "<:username:> :message:",     // Message format when Discord message is received
        "output_cmd": "CMD by :username:",          // Message format when Discord command is received
        "log_events": true                          // Send part/join/kick/quit to IRC
    },
    "formatting": {
        "irc_to_discord": false,                    // Keep bold|underline|italic from IRC to Discord
        "discord_to_irc": true                      // Keep bold|underline|italic from Discord to IRC
    }
}

```

Usage
-----

```
(discordirc) pixis@kali:~/Tools/discord-irc-sync $ python discord-irc-sync.py 
[IRC] Logged in as:
[IRC] hacknbot
[Discord] Logged in as:
[Discord] irc-sync
[Discord] <pixis> : Can you hear me IRC Tom? 😃
[IRC] <pixis> : Yes, I can
```


TODO
----

- [X] Format message from Discord to IRC
- [X] Format message from IRC to Discord : Difficult because not everything is possible, especially when formatting is overlapping
- [ ] Multi channel
- [ ] Multi server
- [ ] Dynamically relaod conf when changed
- [ ] Change conf with IRC or Discord commands
