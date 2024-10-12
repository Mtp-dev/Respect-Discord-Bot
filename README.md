# Respect Discord Bot

This bot allows users to give "respect" to each other and displays leaderboards for users with the most respect points. It supports multiple servers (guilds) with independent data storage for each server. You can configure the bot to store data either in **MySQL** or **locally** as a JSON file. The bot includes the following features:
- `/setup`: Initializes the bot for a specific server.
- `/respect`: Gives respect to another user (with a 24-hour cooldown).
- `/leaderboard`: Displays the top users in the server by respect points.
- `/myrespect`: Shows how much respect the user has.

## Features

- Multi-server support: Each server (guild) can independently track respect data.
- Dynamic respect system with leaderboards.
- Data stored in **MySQL** or **locally**, ensuring persistence across server restarts.
- Slash commands for easy interaction.

## Prerequisites

1. **Python 3.8+** installed on your system.
2. **MySQL** server running and accessible (optional, if using MySQL).
3. Discord bot created on the [Discord Developer Portal](https://discord.com/developers/applications).
4. The following Python libraries installed:
    ```bash
    pip install discord.py mysql-connector-python
    ```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mtp-dev/respect-discord-bot.git
   cd respect-discord-bot
   ```

2. **MySQL Setup (Optional)**:
   - If you are using MySQL, ensure your MySQL database is running.
   - Create a new database for the bot (or use an existing one) and add the credentials to the bot.

   Example SQL to create a database:
   ```sql
   CREATE DATABASE discord_respect;
   ```

3. **Configure the Bot**:
   - Open the `discord_bot.py` file.
   - Replace the following placeholder values with your actual information:
     - `your_mysql_host`
     - `your_mysql_user`
     - `your_mysql_password`
     - `your_mysql_database`
     - `your_bot_token`
   - Set the `USE_MYSQL` flag to either `True` (to use MySQL) or `False` (to use local storage).

4. **Run the Bot**:
   ```bash
   python discord_bot.py
   ```

5. **Invite the Bot** to your server:
   - Create a bot invite link on the Discord Developer Portal by selecting the necessary permissions (like `Send Messages`, `Manage Messages`, and `Use Slash Commands`).
   - Use the generated invite link to add the bot to your Discord server.

## Commands

- **/setup**: Initializes the bot for your server. This command must be run by a server admin before using other commands.
- **/respect**: Give respect to another user. You can only give respect once every 24 hours.
- **/leaderboard**: Displays the top users in the server by respect points.
- **/myrespect**: Shows how many respect points you have.

## Data Storage Options

You can choose to store the respect data either in MySQL or locally (using a JSON file).

### MySQL (Remote Database)

- Set `USE_MYSQL = True` in the bot's configuration.
- Provide the necessary MySQL credentials.

### Local Storage

- Set `USE_MYSQL = False` in the bot's configuration.
- The data will be stored in a local JSON file (`local_respect_data.json`) in the bot's directory.

## Example Usage

1. A server admin runs `/setup` to initialize the bot for their server.
2. Users can give respect to others by running `/respect @username`.
3. Users can check how much respect they have with `/myrespect`.
4. Server members can view the top respected users by using `/leaderboard`.

## Contributing

Feel free to open issues or pull requests if you find any bugs or want to add new features!

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
