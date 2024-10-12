import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import mysql.connector
import json
import os

# Toggle between MySQL and local storage
USE_MYSQL = False  # Set to True to use MySQL, False to use local storage

# File for local storage
LOCAL_STORAGE_FILE = 'local_respect_data.json'

# Initialize the local storage if it does not exist
def initialize_local_storage():
    if not os.path.exists(LOCAL_STORAGE_FILE):
        with open(LOCAL_STORAGE_FILE, 'w') as f:
            json.dump({}, f)

if USE_MYSQL:
    # MySQL database setup (Replace with your actual DB credentials)
    db = mysql.connector.connect(
        host="your_mysql_host",  # Replace with your MySQL host
        port=3306,  # Specify the port separately
        user="your_mysql_user",  # Replace with your MySQL user
        password="your_mysql_password",  # Replace with your MySQL password
        database="your_mysql_database"  # Replace with your MySQL database
    )
    cursor = db.cursor()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        try:
            # Sync commands globally to all servers
            await self.tree.sync(guild=None)
            print("Slash commands synced globally.")
        except Exception as e:
            print(f"Error syncing commands: {e}")
        
        if not USE_MYSQL:
            initialize_local_storage()

client = MyClient()

# Helper functions for local storage
def read_local_data():
    with open(LOCAL_STORAGE_FILE, 'r') as f:
        return json.load(f)

def write_local_data(data):
    with open(LOCAL_STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Function to get or create a respect table for the current guild
def get_respect_table(guild_id):
    if USE_MYSQL:
        respect_table_name = f"respect_guild_{guild_id}"
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {respect_table_name} (
                user_id BIGINT PRIMARY KEY,
                respect_count INT DEFAULT 0,
                last_respect TIMESTAMP NULL
            )
        ''')
        return respect_table_name
    else:
        data = read_local_data()
        if str(guild_id) not in data:
            data[str(guild_id)] = {}
            write_local_data(data)
        return str(guild_id)

# /respect command to give respect to another user
@client.tree.command(name="respect", description="Give respect to another user")
@app_commands.describe(member="The member you want to give respect to")
async def respect(interaction: discord.Interaction, member: discord.Member):
    if interaction.user == member:
        await interaction.response.send_message("You can't give respect to yourself!", ephemeral=True)
        return

    guild_id = interaction.guild.id
    respect_table = get_respect_table(guild_id)

    user_id = member.id
    current_time = datetime.utcnow()

    if USE_MYSQL:
        cursor.execute(f"SELECT respect_count, last_respect FROM {respect_table} WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

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
    
    else:
        data = read_local_data()
        if str(user_id) in data[str(guild_id)]:
            respect_data = data[str(guild_id)][str(user_id)]
            last_respect = datetime.fromisoformat(respect_data["last_respect"])
            if current_time - last_respect < timedelta(days=1):
                await interaction.response.send_message(f"{member.name} has already received respect in the last 24 hours. Try again later.", ephemeral=True)
                return
            respect_data["respect_count"] += 1
            respect_data["last_respect"] = current_time.isoformat()
        else:
            data[str(guild_id)][str(user_id)] = {"respect_count": 1, "last_respect": current_time.isoformat()}
        write_local_data(data)
        await interaction.response.send_message(f"{member.name} has been given respect! 🪙 They now have {data[str(guild_id)][str(user_id)]['respect_count']} respect points.")

# /leaderboard command to show top users by respect points with error handling and better data handling
@client.tree.command(name="leaderboard", description="Show top users by respect points")
async def leaderboard(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    respect_table = get_respect_table(guild_id)

    if USE_MYSQL:
        cursor.execute(f"SELECT user_id, respect_count FROM {respect_table} ORDER BY respect_count DESC LIMIT 10")
        leaderboard = cursor.fetchall()
    else:
        data = read_local_data()
        guild_data = data.get(str(guild_id), {})
        leaderboard = sorted(guild_data.items(), key=lambda x: x[1]['respect_count'], reverse=True)[:10]

    embed = discord.Embed(
        title="Respect Leaderboard",
        description="Top users by respect points 🪙",
        color=discord.Color.blue()
    )

    for rank, (user_id, respect_count) in enumerate(leaderboard, 1):
        try:
            if USE_MYSQL:
                member = await interaction.guild.fetch_member(int(user_id))
                points = respect_count  # In MySQL, respect_count is directly available
            else:
                member = await interaction.guild.fetch_member(int(user_id))
                points = respect_count['respect_count']  # For local storage

            embed.add_field(name=f"{rank}. {member.name}", value=f"{points} respect points 🪙", inline=False)
        except discord.NotFound:
            # Skip users who cannot be found in the guild
            continue

    await interaction.response.send_message(embed=embed)

# /myrespect command to show your own respect points
@client.tree.command(name="myrespect", description="Show your respect points")
async def myrespect(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    respect_table = get_respect_table(guild_id)
    user_id = interaction.user.id

    if USE_MYSQL:
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

    else:
        data = read_local_data()
        user_data = data[str(guild_id)].get(str(user_id), {"respect_count": 0})
        respect_count = user_data["respect_count"]

        embed = discord.Embed(
            title="Your Respect Points",
            description=f"You have {respect_count} respect points 🪙.",
            color=discord.Color.blue()
        )

    await interaction.response.send_message(embed=embed)

# Run the bot
client.run("your_bot_token_here")
