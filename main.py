import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from sessions import SessionManager

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
session_manager = SessionManager()

# Configuration - Dynamic settings
SESSION_CHANNEL_ID = 1555296270057218148
SESSION_MANAGER_ROLE_ID = 1555296192424841217

# Store settings in memory (you could also use a database)
settings = {
    "session_channel_id": SESSION_CHANNEL_ID,
    "session_manager_role_id": SESSION_MANAGER_ROLE_ID
}

def has_session_manager_role(interaction: discord.Interaction) -> bool:
    """Check if user has the Session Manager role"""
    if interaction.user.guild_permissions.administrator:
        return True
    
    role = interaction.guild.get_role(settings["session_manager_role_id"])
    if role and role in interaction.user.roles:
        return True
    
    return False

async def post_to_session_channel(bot: commands.Bot, embed: discord.Embed):
    """Post an embed to the session channel"""
    try:
        channel = bot.get_channel(settings["session_channel_id"])
        if channel:
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Error posting to session channel: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} connected to Discord!")
    print(f"Session Channel ID: {settings['session_channel_id']}")
    print(f"Session Manager Role ID: {settings['session_manager_role_id']}")
    print("Slash commands ready")
    print("------")

# ADMIN CONFIGURATION COMMANDS

@bot.tree.command(name="setsessionchannel", description="Set the channel where sessions are posted (Admin only)")
@app_commands.describe(channel="The channel to post sessions to")
async def set_session_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Set the session channel - Admin only"""
    
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can change the session channel.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Update the setting
    settings["session_channel_id"] = channel.id
    
    embed = discord.Embed(
        title="✅ Session Channel Updated",
        description=f"Session notifications will now be posted to {channel.mention}",
        color=discord.Color.green()
    )
    embed.add_field(name="Channel ID", value=f"`{channel.id}`", inline=False)
    embed.add_field(name="Channel Name", value=f"`{channel.name}`", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setsessionrole", description="Set the role required to manage sessions (Admin only)")
@app_commands.describe(role="The role that can manage sessions")
async def set_session_role(interaction: discord.Interaction, role: discord.Role):
    """Set the session manager role - Admin only"""
    
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can change the session manager role.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Update the setting
    settings["session_manager_role_id"] = role.id
    
    embed = discord.Embed(
        title="✅ Session Manager Role Updated",
        description=f"Only users with {role.mention} can now manage sessions.",
        color=discord.Color.green()
    )
    embed.add_field(name="Role ID", value=f"`{role.id}`", inline=False)
    embed.add_field(name="Role Name", value=f"`{role.name}`", inline=False)
    
    await interaction.response.send_message(embed=embed)

# SLASH COMMANDS

@bot.tree.command(name="startsession", description="Start a new ER:LC session")
@app_commands.describe(
    game_type="Example: prison, police, firefighter, medic, casual",
    player_count="Max players in the session (default: 6)",
    image="Optional: JPG image to display in the session embed"
)
async def start_session(interaction: discord.Interaction, game_type: str, player_count: int = 6, image: discord.Attachment = None):
    """Start a new gaming session - Session Manager only"""
    
    # Check permissions
    if not has_session_manager_role(interaction):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description=f"Only users with the <@&{settings['session_manager_role_id']}> role can start sessions.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Validate image if provided
    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            embed = discord.Embed(
                title="❌ Invalid Image",
                description="Please attach a valid image file (JPG, PNG, etc.)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    try:
        session = session_manager.create_session(
            host_id=interaction.user.id,
            host_name=interaction.user.name,
            game_type=game_type.lower(),
            max_players=player_count
        )

        embed = discord.Embed(
            title="🎮 New Session Started!",
            color=discord.Color.green()
        )
        embed.add_field(name="Session ID", value=f"`{session['id']}`", inline=False)
        embed.add_field(name="Game Type", value=session["game_type"].capitalize(), inline=True)
        embed.add_field(name="Host", value=interaction.user.mention, inline=True)
        embed.add_field(name="Max Players", value=f"{session['current_players']}/{session['max_players']}", inline=True)
        embed.add_field(name="Status", value="🟢 Active", inline=True)
        embed.set_footer(text="Use /joinsession to join!")
        
        # Add image to embed if provided
        if image:
            embed.set_image(url=image.url)
        
        # Send to user
        await interaction.response.send_message(embed=embed)
        
        # Post to session channel
        await post_to_session_channel(bot, embed)
        
    except ValueError as e:
        embed = discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="joinsession", description="Join an active ER:LC session")
@app_commands.describe(session_id="The session ID to join")
async def join_session(interaction: discord.Interaction, session_id: str):
    """Join an existing session"""
    
    success, message = session_manager.join_session(session_id, interaction.user.id, interaction.user.name)

    if success:
        session = session_manager.get_session(session_id)
        embed = discord.Embed(
            title="✅ Joined Session!",
            description=message,
            color=discord.Color.blue()
        )
        embed.add_field(name="Session ID", value=f"`{session_id}`", inline=True)
        embed.add_field(name="Game Type", value=session["game_type"].capitalize(), inline=True)
        embed.add_field(name="Players", value=f"{session['current_players']}/{session['max_players']}", inline=True)
        await interaction.response.send_message(embed=embed)
        
        # Post to session channel
        join_embed = discord.Embed(
            title="👤 Player Joined Session",
            description=f"{interaction.user.mention} joined session `{session_id}`",
            color=discord.Color.blue()
        )
        join_embed.add_field(name="Current Players", value=f"{session['current_players']}/{session['max_players']}", inline=True)
        await post_to_session_channel(bot, join_embed)
    else:
        embed = discord.Embed(
            title="❌ Could not join",
            description=message,
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="leavesession", description="Leave your current session")
async def leave_session(interaction: discord.Interaction):
    """Leave your current session"""
    
    success, message = session_manager.leave_session(interaction.user.id)

    if success:
        embed = discord.Embed(
            title="👋 Left Session",
            description=message,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        
        # Post to session channel
        leave_embed = discord.Embed(
            title="👤 Player Left Session",
            description=f"{interaction.user.mention} left their session",
            color=discord.Color.greyple()
        )
        await post_to_session_channel(bot, leave_embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="sessions", description="List all active ER:LC sessions")
async def list_sessions(interaction: discord.Interaction):
    """Display all active sessions"""
    
    sessions = session_manager.get_active_sessions()

    if not sessions:
        embed = discord.Embed(
            title="❌ No Active Sessions",
            description="Start a new session with `/startsession`",
            color=discord.Color.greyple()
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(
        title="🎮 Active ER:LC Sessions",
        color=discord.Color.gold()
    )

    for session in sessions:
        player_list = "\n".join([f"<@{pid}>" for pid in session["players"][:5]])
        if len(session["players"]) > 5:
            player_list += f"\n... and {len(session['players']) - 5} more"

        embed.add_field(
            name=f"**ID:** `{session['id']}`",
            value=f"**Type:** {session['game_type'].capitalize()}\n**Host:** <@{session['host_id']}>\n**Players:** {session['current_players']}/{session['max_players']}\n**Status:** {session['status']}",
            inline=False
        )

    embed.set_footer(text="Use /joinsession <id> to join a session")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sessioninfo", description="Get detailed info about a session")
@app_commands.describe(session_id="The session ID to inspect")
async def session_info(interaction: discord.Interaction, session_id: str):
    """Get detailed information about a session"""
    
    session = session_manager.get_session(session_id)

    if not session:
        embed = discord.Embed(
            title="❌ Session Not Found",
            description=f"Session `{session_id}` does not exist.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    player_mentions = ", ".join([f"<@{pid}>" for pid in session["players"]])

    embed = discord.Embed(
        title=f"Session Info - `{session_id}`",
        color=discord.Color.blue()
    )
    embed.add_field(name="Game Type", value=session["game_type"].capitalize(), inline=True)
    embed.add_field(name="Host", value=f"<@{session['host_id']}>", inline=True)
    embed.add_field(name="Status", value=session["status"], inline=True)
    embed.add_field(name="Players", value=f"{session['current_players']}/{session['max_players']}", inline=True)
    embed.add_field(name="Created", value=session["created_at"][:10], inline=True)
    embed.add_field(name="Started", value=session["started_at"][:10] if session["started_at"] else "Not started", inline=True)
    embed.add_field(name="Member List", value=player_mentions, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mysession", description="View the session you're currently in")
async def my_session(interaction: discord.Interaction):
    """Get info about your current session"""
    
    session = session_manager.get_player_session(interaction.user.id)

    if not session:
        embed = discord.Embed(
            title="❌ Not in a Session",
            description="You are not currently in any session",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    player_mentions = ", ".join([f"<@{pid}>" for pid in session["players"]])

    embed = discord.Embed(
        title=f"Your Session - `{session['id']}`",
        color=discord.Color.green()
    )
    embed.add_field(name="Game Type", value=session["game_type"].capitalize(), inline=True)
    embed.add_field(name="Host", value=f"<@{session['host_id']}>", inline=True)
    embed.add_field(name="Status", value=session["status"], inline=True)
    embed.add_field(name="Players", value=f"{session['current_players']}/{session['max_players']}", inline=True)
    embed.add_field(name="Member List", value=player_mentions, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="stopsession", description="Stop a session (Session Manager only)")
@app_commands.describe(
    session_id="The session ID to stop",
    image="Optional: JPG image to display in the shutdown embed"
)
async def stop_session(interaction: discord.Interaction, session_id: str, image: discord.Attachment = None):
    """End a session - Session Manager only"""
    
    # Check permissions
    if not has_session_manager_role(interaction):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description=f"Only users with the <@&{settings['session_manager_role_id']}> role can stop sessions.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Validate image if provided
    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            embed = discord.Embed(
                title="❌ Invalid Image",
                description="Please attach a valid image file (JPG, PNG, etc.)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    session = session_manager.get_session(session_id)

    if not session:
        embed = discord.Embed(
            title="❌ Session Not Found",
            description=f"Session `{session_id}` does not exist.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # End the session
    session_manager.end_session(session_id)

    embed = discord.Embed(
        title="🛑 Session Stopped",
        description=f"Session `{session_id}` has been ended by {interaction.user.mention}",
        color=discord.Color.orange()
    )
    embed.add_field(name="Game Type", value=session["game_type"].capitalize(), inline=True)
    embed.add_field(name="Total Players", value=session["current_players"], inline=True)
    embed.add_field(name="Status", value="⚫ Ended", inline=True)
    
    # Add image to embed if provided
    if image:
        embed.set_image(url=image.url)

    await interaction.response.send_message(embed=embed)
    
    # Post to session channel
    await post_to_session_channel(bot, embed)

@bot.tree.command(name="help", description="Show all available commands")
async def show_help(interaction: discord.Interaction):
    """Show help information"""
    
    embed = discord.Embed(
        title="🎮 ER:LC Session Bot - Commands",
        description="Here are all available slash commands",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Session Manager Commands",
        value="`/startsession` - Start a new session (optional: add JPG image)\n`/stopsession` - Stop a session (optional: add JPG image)",
        inline=False
    )

    embed.add_field(
        name="Player Commands",
        value="`/joinsession` - Join a session\n`/leavesession` - Leave your session\n`/mysession` - View your current session",
        inline=False
    )

    embed.add_field(
        name="Info Commands",
        value="`/sessions` - List all active sessions\n`/sessioninfo` - Get details about a session\n`/help` - Show this menu",
        inline=False
    )

    embed.add_field(
        name="Admin Commands",
        value="`/setsessionchannel` - Set where sessions are posted\n`/setsessionrole` - Set the session manager role",
        inline=False
    )

    embed.add_field(
        name="Game Types",
        value="`prison` • `police` • `firefighter` • `medic` • `casual`",
        inline=False
    )
    
    embed.add_field(
        name="Session Channel",
        value=f"<#{settings['session_channel_id']}>",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN is missing. Add it to your .env file.")
        raise SystemExit(1)
    bot.run(TOKEN)
