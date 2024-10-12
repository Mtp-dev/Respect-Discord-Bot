
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import mysql.connector

# Database setup (Replace with your actual DB credentials)
db = mysql.connector.connect(
    host="your_mysql_host",  # Only the host IP here, no port
    port=3306,  # Specify the port separately
    user="your_mysql_user",
    password="your_mysql_password",
    database="your_mysql_database"
)
cursor = db.cursor()

# Create guilds table to track different servers using the bot
cursor.execute('''
    CREATE TABLE IF NOT EXISTS guilds (
        guild_id BIGINT PRIMARY KEY,
        respect_table_name VARCHAR(255)
    )
''')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Sync the commands globally, or you can specify a specific guild for testing purposes
guild_id = discord.Object(id=your_guild_id)  # Default guild for testing, will be dynamic with /setup

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.tree.sync(guild=None)  # Sync globally for multiple servers

client = MyClient()

# /setup command to initialize a guild with the bot
@client.tree.command(name="setup", description="Setup the bot for your server")
async def setup(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    respect_table_name = f"respect_guild_{guild_id}"

    # Check if the guild is already set up
    cursor.execute("SELECT respect_table_name FROM guilds WHERE guild_id = %s", (guild_id,))
    if cursor.fetchone() is not None:
        await interaction.response.send_message("This server is already set up!", ephemeral=True)
        return

    # Create a new table for this guild's respect data
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {respect_table_name} (
            user_id BIGINT PRIMARY KEY,
            respect_count INT DEFAULT 0,
            last_respect TIMESTAMP NULL
        )
    ''')

    # Store the guild info in the guilds table
    cursor.execute("INSERT INTO guilds (guild_id, respect_table_name) VALUES (%s, %s)", (guild_id, respect_table_name))
    db.commit()

    await interaction.response.send_message(f"Bot has been set up for this server! Respect data will be stored in `{respect_table_name}`.")

# Function to get the respect table for the current guild
def get_respect_table(guild_id):
    cursor.execute("SELECT respect_table_name FROM guilds WHERE guild_id = %s", (guild_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

# Add respect command as a slash command, works per guild
@client.tree.command(name="respect", description="Give respect to another user")
@app_commands.describe(member="The member you want to give respect to")
async def respect(interaction: discord.Interaction, member: discord.Member):
    if interaction.user == member:
        await interaction.response.send_message("You can't give respect to yourself!", ephemeral=True)
        return

    guild_id = interaction.guild.id
    respect_table = get_respect_table(guild_id)

    if respect_table is None:
        await interaction.response.send_message("This server has not been set up yet! Use `/setup` first.", ephemeral=True)
        return

    user_id = member.id
    cursor.execute(f"SELECT respect_count, last_respect FROM {respect_table} WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    current_time = datetime.utcnow()

    if result:
        respect_count, last_respect = result

        if last_respect and current_time - last_respect < timedelta(days=1):
            await interaction.response.send_message(f"{member.name} has already received respect in the last 24 hours. Try again later.", ephemeral=True)
            return
        new_count = respect_count + 1
        cursor.execute(f"UPDATE {respect_table} SET respect_count = %s, last_respect = %s WHERE user_id = %s", (new_count, current_time, user_id))
    else:
        cursor.execute(f"INSERT INTO {respect_table} (user_id, respect_count, last_respect) VALUES (%s, %s, %s)", (user_id, 1, current_time))

    db.commit()
    await interaction.response.send_message(f"{member.name} has been given respect! 🪙 They now have {new_count if result else 1} respect points.")

# Leaderboard command, works per guild
@client.tree.command(name="leaderboard", description="Show top users by respect points")
async def leaderboard(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    respect_table = get_respect_table(guild_id)

    if respect_table is None:
        await interaction.response.send_message("This server has not been set up yet! Use `/setup` first.", ephemeral=True)
        return

    cursor.execute(f"SELECT user_id, respect_count FROM {respect_table} ORDER BY respect_count DESC LIMIT 10")
    leaderboard = cursor.fetchall()

    embed = discord.Embed(
        title="Respect Leaderboard",
        description="Top users by respect points 🪙",
        color=discord.Color.blue()
    )

    for rank, (user_id, respect_count) in enumerate(leaderboard, 1):
        member = await interaction.guild.fetch_member(user_id)
        embed.add_field(name=f"{rank}. {member.name}", value=f"{respect_count} respect points 🪙", inline=False)

    await interaction.response.send_message(embed=embed)

# My respect command, works per guild
@client.tree.command(name="myrespect", description="Show your respect points")
async def myrespect(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    respect_table = get_respect_table(guild_id)

    if respect_table is None:
        await interaction.response.send_message("This server has not been set up yet! Use `/setup` first.", ephemeral=True)
        return

    user_id = interaction.user.id
    cursor.execute(f"SELECT respect_count FROM {respect_table} WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        embed = discord.Embed(
            title="Your Respect Points",
            description=f"You have {result[0]} respect points 🪙.",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="Your Respect Points",
            description="You don't have any respect points yet.",
            color=discord.Color.red()
        )

    await interaction.response.send_message(embed=embed)

# Run the bot
client.run("your_bot_token")
