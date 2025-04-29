# GroupQueueBot

*GroupQueueBot* is a Telegram bot designed to help groups manage and organize queue-based lists. It allows users to create, view, and manage lists of participants for various purposes such as assignments, tasks, or event planning.

## Features

- 👥 View all users in the group
- 📋 Display all available lists
- ➕ Create new lists
- 🗑️ Delete existing lists
- 🔄 Navigate between different views using intuitive emoji-enhanced buttons

## Requirements

- Python 3.6+
- `telebot` library
- `requests` library
- `python-dotenv` library
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/botfather))
- A [backend server](https://github.com/xirzo/GroupQueue) running the API endpoints

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/GroupQueueBot.git
cd GroupQueueBot
```

### 2. Install dependencies (or through your package manager)

```bash
pip install pyTelegramBotAPI requests python-dotenv
```

### 3. Create environment variables

Create a `.env` file in the root directory with the following variables:

```
TOKEN=your_telegram_bot_token_here
BACKEND_URL=your_backend_server_url_here
```

## Running Locally

To run the bot locally for development or testing:

```bash
python main.py
```

## Deploying to a Server

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/groupqueuebot.service
```

2. Add the following content:

```
[Unit]
Description=Group Queue Telegram Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/GroupQueueBot
ExecStart=/usr/bin/python3 /path/to/GroupQueueBot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Start and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start groupqueuebot
sudo systemctl enable groupqueuebot
```

4. Check the status:

```bash
sudo systemctl status groupqueuebot
```
