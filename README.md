# Social Media Post Rephrasing Bot

A Telegram bot that fetches posts from social media platforms and rephrases them using AI before publishing to a channel.

## Features

- **Twitter/X Integration** (the infrastructure is ready for integration with other social networks): Extract posts using URLs or IDs
- **AI Rephrasing**: With Gemini or another Gen AI API
- **Manual Editing**: Edit posts manually before publishing
- **Channel Publishing**: Automatically publish to Telegram channels
- **Media Support**: Handle images and videos from original posts

## Quick Start

1. **Clone and install dependencies**:
   ```bash
   git clone https://github.com/Malnormalulos-git/crooked-mirror-bot
   cd crooked-mirror-bot
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials:
   - `BOT_TOKEN`: Telegram bot token (Create bot and get token here [@BotFather](https://t.me/BotFather))
   - `ADMIN_ID`: Your Telegram user ID (You can gat it from [@JsonDumpCUBot](https://t.me/JsonDumpCUBot))
   - `TWITTER_AUTH_TOKEN` & `TWITTER_CT0`: Twitter cookies
   - `LLM_API_KEY`: Google Gemini API key (You can get it from [Google AI Studio](https://aistudio.google.com/app/apikey))
   - `CHANNEL_ID`: Target Telegram channel ID (You can get it from [@JsonDumpCUBot](https://t.me/JsonDumpCUBot)) (Bot must be an admin of the provided channel)

3. **Run the bot**:
   ```bash
   python main.py
   ```

## Docker

1. **Ensure you set up `.env` file.**

2. In terminal run:
   ```bash
   docker build -t crooked-mirror-bot .
   ```

3. And finally:
   ```bash
   docker run crooked-mirror-bot
   ```


## Usage

1. Start the bot with `/start`
2. Click "🔄 Rephrase post 📜" or send a post URL/ID
3. Preview the original post
4. Choose to:
   - Publish as-is
   - Edit manually
   - Rephrase with AI (with optional custom instructions)
5. Publish to your channel