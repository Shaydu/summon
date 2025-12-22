# Minecraft Bedrock Server Console Commands

Below is a list of common commands you can use in the Bedrock server console. These commands can be entered directly into the console or via the screen session.

## Player Management
- `list` — Lists all players currently online.
- `kick <player>` — Kicks a player from the server.
- `ban <player>` — Bans a player from the server.
- `unban <player>` — Unbans a player.
- `op <player>` — Grants operator status to a player.
- `deop <player>` — Revokes operator status from a player.
- `whitelist add <player>` — Adds a player to the whitelist.
- `whitelist remove <player>` — Removes a player from the whitelist.
- `whitelist list` — Lists all players on the whitelist.

## Server Management
- `stop` — Stops the server.
- `save-all` — Saves the world data to disk.
- `save-on` — Enables automatic world saving.
- `save-off` — Disables automatic world saving.
- `say <message>` — Broadcasts a message to all players.
- `setmaxplayers <number>` — Sets the maximum number of players.

## World and Gameplay
- `gamemode <mode> [player]` — Changes the game mode (survival, creative, adventure, spectator).
- `difficulty <level>` — Sets the difficulty (peaceful, easy, normal, hard).
- `time set <value>` — Sets the time of day.
- `weather <clear|rain|thunder>` — Changes the weather.
- `tp <player> <target>` — Teleports a player to another player or coordinates.
- `give <player> <item> [amount]` — Gives an item to a player.
- `effect <player> <effect> [seconds] [amplifier]` — Applies a status effect to a player.

## Information
- `help` or `?` — Lists all available commands.
- `version` — Shows the server version.

## Notes
- Some commands may require operator (op) privileges.
- Use the `help` command in the console for a full list and details on each command.

---
For more information, see the official Minecraft Bedrock server documentation or type `help` in the server console.
