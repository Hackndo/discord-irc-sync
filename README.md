# Discord-IRC Synchronization

Description
-----------

**Python3.5+** implementation of a synchronization between IRC and Discord

![discordirc](https://user-images.githubusercontent.com/11051803/32892891-f7e0b216-cad7-11e7-8938-e23d82ef0c60.gif)


Requirements
------------

* Python 3.5+

Initialization
--------------

```sh
git clone git@github.com:Hackndo/discord-irc-sync.git
cd discord-irc-sync
mkvirtualenv discordirc -p $(which python3)
pip install -r requirements.txt
cp config/config.json.dist config/config.json
# Edit config/config.json
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
