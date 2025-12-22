## Sources
- [Official Minecraft Bedrock Dedicated Server Documentation](https://minecraft.fandom.com/wiki/Bedrock_Dedicated_Server)
- [Minecraft Bedrock Edition Commands (Fandom)](https://minecraft.fandom.com/wiki/Commands/Bedrock_Edition)
- [Minecraft Official Help: Server Commands](https://help.minecraft.net/hc/en-us/articles/360034754912-How-to-Use-the-Server-Console)
# Minecraft Bedrock Server Console Commands

This document lists useful commands for the Bedrock server console. Enter these in the server console or via the screen session.

## Player & Object Management
- `list` — List all players currently online.
- `kick <player>` — Kick a player from the server.
- `ban <player>` — Ban a player from the server.
- `unban <player>` — Unban a player.
- `op <player>` — Grant operator status to a player.
- `deop <player>` — Revoke operator status from a player.
- `whitelist add <player>` — Add a player to the whitelist.
- `whitelist remove <player>` — Remove a player from the whitelist.
- `whitelist list` — List all players on the whitelist.
- `gamemode <mode> [player]` — Change a player's game mode (survival, creative, adventure, spectator).
- `tp <player> <target>` — Teleport a player to another player or coordinates.
- `give <player> <item> [amount]` — Give an item to a player. Example: `give Steve diamond_sword 1` adds 1 diamond sword to Steve's inventory.
- `effect <player> <effect> [seconds] [amplifier]` — Apply a status effect to a player.
- `clear <player> [item]` — Clear items from a player's inventory.
- `kill <player>` — Kill a player.
- `summon <entity> [x y z]` — Spawn an entity at the specified location. Example: `summon zombie 100 64 100` spawns a zombie at (100, 64, 100).
	- Player-agnostic spawning: Use explicit coordinates to spawn entities anywhere in the world, regardless of player location. For example:
		- `summon creeper -95.49 69.62 -485.60`
		- `summon creeper -41.21 65.62 -414.18`
		- `summon piglin -41.21 65.62 -414.18`
	- To find a player's coordinates, use the `querytarget <player>` command in the console. The output will include the player's position, which you can use for precise spawning.
- `say <message>` — Broadcast a message to all players. Example: `say Server restarting soon!`

## Server Management
- `stop` — Stop the server.
- `save-all` — Save the world data to disk.
- `save-on` — Enable automatic world saving.
- `save-off` — Disable automatic world saving.
- `say <message>` — Broadcast a message to all players.
- `setmaxplayers <number>` — Set the maximum number of players.
- `difficulty <level>` — Set the difficulty (peaceful, easy, normal, hard).
- `time set <value>` — Set the time of day (e.g., `time set day`, `time set 1000`).
- `weather <clear|rain|thunder>` — Change the weather.
- `title <player> <title|subtitle|actionbar|clear|reset|times> ...` — Show titles to players.
- `me <action>` — Send a message as a player action.
- `gamerule <rule> <value>` — Set a game rule (e.g., `gamerule keepinventory true`).
- `clone <begin> <end> <destination>` — Clone blocks from one region to another.
- `fill <from> <to> <block>` — Fill a region with a block.
- `setworldspawn [<x> <y> <z>]` — Set the world spawn point.
- `spawnpoint [<player>] [<x> <y> <z>]` — Set a player's spawn point.
- `reload` — Reloads server properties and some resource packs.

## Information & Debugging
- `help` or `?` — List all available commands.
- `version` — Show the server version.
- `seed` — Show the world seed.
- `locate <structure>` — Find the coordinates of a structure (e.g., `locate village`).
- `listd` — List all dimensions.
- `tickingarea add|remove|list` — Manage ticking areas.

## Notes
- Some commands require operator (op) privileges.
- Use the `help` command in the console for a full list and details on each command.
- For command syntax, use `/` in-game or omit `/` in the console.

---
For more, see the official Minecraft Bedrock server documentation or type `help` in the server console.