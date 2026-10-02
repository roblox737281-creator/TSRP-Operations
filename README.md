# TSRP Operations - ER:LC Discord Bot

A Discord bot for managing Roblox Emergency: Response Liberty County (ER:LC) gaming sessions with slash commands!

## Features

✅ Create gaming sessions with `/startsession`  
✅ Join sessions with `/joinsession`  
✅ Leave sessions with `/leavesession`  
✅ Stop sessions with `/stopsession`  
✅ View all active sessions with `/sessions`  
✅ Get detailed session info with `/sessioninfo`  
✅ Check your current session with `/mysession`  
✅ Easy help with `/help`  

## Setup Instructions

### 1. Install Python & Dependencies

Make sure you have **Python 3.10+** installed. Then run:

```bash
pip install -r requirements.txt
```

### 2. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name
3. Go to the **"Bot"** tab and click **"Add Bot"**
4. Under **TOKEN**, click **"Copy"** to copy your bot token
5. Go to **"OAuth2"** → **"URL Generator"**
6. Select scopes: `bot`
7. Select permissions:
   - ✓ Send Messages
   - ✓ Embed Links
   - ✓ Read Message History
   - ✓ Read Messages/View Channels
8. Copy the generated URL and open it in your browser to add the bot to your server

### 3. Configure Environment

1. Create a `.env` file in the root directory (copy from `.env.example`)
2. Paste your bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```

### 4. Run the Bot

```bash
python main.py
```

You should see:
```
YourBotName#1234 has connected to Discord!
Slash commands synced!
```

## Commands

### Session Management

| Command | Description |
|---------|-------------|
| `/startsession` | Start a new session |
| `/joinsession` | Join an existing session |
| `/leavesession` | Leave your current session |
| `/stopsession` | Stop a session (host only) |

### Info & Viewing

| Command | Description |
|---------|-------------|
| `/sessions` | List all active sessions |
| `/sessioninfo` | Get details about a session |
| `/mysession` | View your current session |
| `/help` | Show all commands |

## Command Examples

### Start a session
```
/startsession game_type: prison player_count: 4
```

### Join a session
```
/joinsession session_id: a1b2c3d4
```

### Stop a session (you must be the host)
```
/stopsession session_id: a1b2c3d4
```

### View all sessions
```
/sessions
```

### Check your session
```
/mysession
```

## Game Types

- `prison` - Prison-themed gameplay
- `police` - Police response scenarios
- `firefighter` - Firefighter missions
- `medic` - Medical response scenarios
- `casual` - Casual/mixed gameplay

## How It Works

### Creating a Session
1. Use `/startsession` to create a new session
2. You become the **host** of that session
3. The bot assigns a unique session ID
4. Other players can join using that ID

### Joining a Session
1. Find a session ID using `/sessions`
2. Use `/joinsession session_id: <id>`
3. You're added to the session
4. Session size updates automatically

### Stopping a Session
1. Only the **host** can stop a session
2. Use `/stopsession session_id: <id>`
3. Session is marked as ended
4. Players can no longer join

## Project Structure

```
TSRP-Operations/
├── main.py              # Bot commands and main logic
├── sessions.py          # Session management system
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .env                # Your bot token (keep secret!)
└── README.md           # This file
```

## Troubleshooting

### Bot not responding?
- Check that your bot token is correct in `.env`
- Make sure the bot has permissions in your server
- Restart the bot: `python main.py`

### Slash commands not showing up?
- Restart the bot completely
- Wait 1-2 minutes for Discord to sync commands
- Try typing `/` in Discord to refresh the command list

### "DISCORD_TOKEN not found"?
- Create a `.env` file in the root directory
- Add your token: `DISCORD_TOKEN=your_token_here`
- Restart the bot

### Bot crashes on startup?
- Check Python version: `python --version` (need 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check for typos in `.env` file

## Next Steps

- Add role/permission restrictions
- Save sessions to a database
- Add session statistics
- Create web dashboard
- Add voice channel support
- Add session invites

## Support

If you have issues:
1. Check the troubleshooting section above
2. Make sure all files are in the root directory
3. Verify your bot token is correct
4. Check that the bot has permissions in your server

Good luck with your ER:LC sessions! 🎮
