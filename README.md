# GALACTIC REAPERS - twitch stream interactive game overlay
*MINE* asteroids - *STORE* resources - *UPGRADE* ships - *PURCHASE* facilities - *KILL* hostiles - *TRADE* with others - *PROTECT* incoming cargo

## The Why

This game is a passion project developed to increase engagement, and for the entertainment of viewers of my twitch stream  [Mupersega Twitch](https://www.twitch.tv/mupersega). Users can type commands in twitch chat to control their ships and facilities mid-stream. The idea of this game was to not BE the content of the stream but to simply enhance it and gives viewers something more to engage with, hopefully increasing retention. 

## The How

### Requirements
- Python 3.8
- pygame 2.0.1
- SQLite3 (not used in demo mode, but still required)

### Display
This game is meant to be viewed during a twitch streaming session, that is, overlayed on top of streamed content. To do this the game will be run locally and then fed as a display source to OBS(the streaming software), whereupon all the black background is color-keyed out, leaving just the game's elements moving around the screen. Ultimately I might enhance the game to a point where I can host it indefinitely with game mechanics that support endless play.

### Viewer Interaction

Users/viewers interact with the game using twitch chat. Commands are prefaced with "!" and are processed by an IRC chat bot developed and stored in a private repo for security reasons. Some example commands may read:
- !play (get into the game)
- !upgrade bay 1 thrusters (upgrade thrusters of the ship in bay 1)
- !redeem starseeker (redeem a hostile-seeking cluster missile!)

I run the chat bot separately from the game as it is the simplest way for me to address the game blocking, while the chat bot also blocks. They communicate with each other via an SQLite "database" (a single table) where:

```
# bot (listening)
for every chat message
  if potential command
    if valid command
      in TABLE store username, subscription status, message args, processed bool

# game (watch every n seconds)
for every entry in TABLE where not processed
  spool up a process_command thread
    process_command
    set processed True
for every entry in TABLE where processed
  remove entry
```

**MANY MORE DOCS TO COME...**
