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

1. Go to [Discord developer application](https://discordapp.com/developers/applications/me)
2. Add a new application
3. Create a Bot User
4. Follow https://discordapp.com/oauth2/authorize?&client_id=CLIENT_ID&scope=bot&permissions=0 with your application **Client ID**
5. Choose your server

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
        "server": "irc.server.com",   // IRC Server
        "port": "6667",               // IRC Port
        "channel": "#channel",        // IRC Channel
        "nickname": "h_bot",          // Bot Nickname
        "owner": "username",          // Bot Owner Nickname (admin commands)
        "cmd_prefix": "!"             // Channel commands prefix (if any)
    },
    "discord": {
        "server": "<server id>",      // Discord Server ID
        "channel": "<channel id>",    // Discord Channel ID
        "token": "<bot token>",       // Discord Bot Token
        "owner": "username",          // Discord Bot Owner username (admin commands)
        "cmd_prefix": "!"             // Channel commands prefix (if any)
    },
    "formatting": {
        "irc_to_discord": false,      // Keep bold|underlin|italic from IRC to Discord
        "discord_to_irc": true        // Keep bold|underlin|italic from Discord to IRC
    }
}

```

Usage
-----

```
(discordirc) pixis@kali:~/Tools/discord-irc-sync $ python app.py 
[IRC] Logged in as:
[IRC] hacknbot
[Discord] Logged in as:
[Discord] irc-sync
[Discord] <pixis> : Can you hear me IRC Tom? 😃
[IRC] <pixis> : Yes, I can
```


TODO
----

- [X] Format message from Discord to IRC~~
- [X] Format message from IRC to Discord : Difficult because not everything is possible, especially when formatting is overlapping
- [ ] Multi channel
- [ ] Multi server
- [ ] Dynamically relaod conf when changed
- [ ] Change conf with IRC or Discord commands
