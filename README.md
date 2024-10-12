# MyRespect Discord Bot

**MyRespect** is a Discord bot that allows users to give respect to others, track their respect points, and display leaderboards of the most respected users in a server. The bot can be configured to store data in either a MySQL database or locally in a JSON file.

## Features
- **Give Respect**: Users can give respect to other members once every 24 hours.
- **Respect Leaderboard**: Displays the top respected users in the server.
- **View Your Respect**: Users can view how many respect points they have received.
- **MySQL and Local Storage Support**: Data can be stored in a MySQL database or locally, depending on your configuration.

## Requirements
- Python 3.10+
- Discord.py (version 2.0+)
- MySQL Connector (for MySQL support)

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/MyRespectBot.git
cd MyRespectBot
```

### Step 2: Install Dependencies
Use the following command to install the required dependencies from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Step 3: Configure the Bot
You need to configure the bot by setting up either MySQL or local storage.

#### Option 1: MySQL Setup
1. In the bot's source code, set the `USE_MYSQL` flag to `True`:
   ```python
   USE_MYSQL = True
   ```

2. Update the MySQL credentials in the following part of the code:
   ```python
   db = mysql.connector.connect(
       host="your_mysql_host",
       port=3306,
       user="your_mysql_user",
       password="your_mysql_password",
       database="your_mysql_database"
   )
   ```

#### Option 2: Local Storage Setup
1. If you prefer to store the respect data locally, set the `USE_MYSQL` flag to `False`:
   ```python
   USE_MYSQL = False
   ```

2. The bot will automatically create and store data in a `local_respect_data.json` file.

### Step 4: Add Your Bot Token
Replace `"your_bot_token"` in the `client.run()` line with your actual Discord bot token:
```python
client.run("your_bot_token")
```

### Step 5: Run the Bot
To start the bot, run the following command:
```bash
python app.py
```

The bot will sync all commands globally and be ready to use in your server.

## Commands

### `/respect`
Give respect to another user in the server. You can only give respect to a user once every 24 hours.

**Usage**:
```bash
/respect @user
```

### `/leaderboard`
Displays the top users with the most respect points in the server.

**Usage**:
```bash
/leaderboard
```

### `/myrespect`
Displays your current respect points.

**Usage**:
```bash
/myrespect
```

## Storing Data
The bot stores respect data either in a MySQL database or locally, depending on the `USE_MYSQL` flag:
- **MySQL**: Respect data is stored in a table that is created for each guild.
- **Local Storage**: Respect data is stored in the `local_respect_data.json` file, where each guild's data is stored separately.

## Syncing Commands
All commands are automatically synced globally when the bot starts. If you want to ensure all commands are available across all servers where the bot is present, simply start the bot, and the commands will sync globally.

## License
This project is licensed under the MIT License.
