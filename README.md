# 🤖 GroupQueueBot

**GroupQueueBot** is a Telegram bot designed to help groups manage and organize queue-based lists. It allows users to create, view, and manage lists of participants for various purposes such as assignments, tasks, or event planning.

## ✨ Features

- 👥 View all users in the group
- 📋 Display all available lists
- ➕ Create new lists
- 🗑️ Delete existing lists
- 🔄 Navigate between different views using intuitive emoji-enhanced buttons

## 📋 Requirements

- 🐍 Python 3.6+
- 📱 `telebot` library
- 🌐 `requests` library
- 🔐 `python-dotenv` library
- 🔑 A Telegram Bot Token (obtained from [@BotFather](https://t.me/botfather))
- 🖥️ A [backend server](https://github.com/xirzo/GroupQueue) running the API endpoints

## 🚀 Installation

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

Copy given envs, and set **TOKEN** in **frontend-bot.env**.

```bash
cp .backend.env backend.env && cp .frontend-bot.env frontend-bot.env 
```

## 🐳 Running with Docker Compose

```bash
docker compose up -d
```

## 💻 Running Locally

To run the bot locally for development or testing:

```bash
python3 main.py
```

## 🌍 Deploying to a Server

### 1️⃣ Create a systemd service file

```bash
sudo nano /etc/systemd/system/groupqueuebot.service
```

### 2️⃣ Add the following content

```
[Unit]
Description=Group Queue Telegram Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/GroupQueueBot
ExecStart=/usr/bin/python3 /path/to/GroupQueueBot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3️⃣ Start and enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl start groupqueuebot
sudo systemctl enable groupqueuebot
```

### 4️⃣ Check the status

```bash
sudo systemctl status groupqueuebot
```
