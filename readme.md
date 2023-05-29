# Installation

Here are the [Red](https://github.com/Cog-Creators/Red-DiscordBot) commands to add this repository (use your bot's prefix in place of `[p]`):
```
[p]repo add BotC-Red-Cogs https://github.com/burnacid/Botc-Red-Cogs
```

You may be prompted to respond with "I agree" after that.

# Slash Commands

These cog used the `slash` cog for registering slash commands. Make sure the cog is loaded.
```
[p]load slash
```

# Cogs

You can install individual cogs like this:
```
[p]cog install BotC-Red-Cogs [cog]
[p]slash enablecog [cog]
```

Just replace `[cog]` with the name of the cog you want to install.

After you loaded all the cogs and enabled their Slash Commands. You need to sync the slash commands to discord using:
```
[p]slash sync
```

## BotC

This cog helps you run games of Blood on the Clocktower. 

### Commands

| Command               | Description |
| -----------           | ----------- |
| `[p]botc setup`       | This runs the setup for the channel and roles structure. If anything is broken you can rerun this to remove the old and create new channels |
| `[p]botc clean`       | This command lets you enable auto cleanup of the game chat text channels |
| `/storyteller [member]`        | This command assigns you or someone else as storyteller. The storytellers can only use the other slash commands below |
| `/start`              | This command starts the game of BotC. Effectively prohibiting players to assign themselves as storyteller. Only existing storytellers can add new extra storytellers at that point |
| `/stop`               | This command stops the game of BotC. Unlocking the `/storyteller` command again |
| `/day`                | This command moves all players from night channels to town square |
| `/night`              | This command moves all players from day to night channels |
| `/startday <minutes> [automatic]`           | This command sets a timer for the day chats. Sends a reminder in chat 1 minute before the timer is up. And moves all players back to town square when the timer is up. You can disable this automatic move. |

## Follow

This cog lets you follow another member through voice channels. To start following. You need to be in a voice channel. And you need to be able to connect to the voice channel the other member is in.
After that your permissions do not matter. You will follow along even if you can connect of see the voice channels they move to.

### Commands

| Command            | Description |
| ------------------ | ----------- |
| `/follow <member>`        | Follows a member arround |
| `/unfollow`        | Stop following whoever you are following |
| `/removefollow [member]`        | Remove a member or all members from following you |