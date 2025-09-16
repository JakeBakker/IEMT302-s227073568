## Lost & Found Telegram Chatbot (spaCy + python-telegram-bot)

This project adapts a Telegram chatbot template into a practical Lost & Found assistant for a campus or community. The bot lets users report items they have lost or found and searches for potential matches. It uses spaCy to parse free-text messages for intent (lost/found/search) and key attributes such as item, color, location, and date.

### Problem the application addresses

Lost items are frequently reported across fragmented channels (word-of-mouth, group chats, posters). Matches are often missed. This bot provides a single interface where:

- Lost item owners can submit structured reports from natural language.
- People who find items can quickly log what they found.
- Users can query existing found reports to locate matches.

The bot extracts core details and suggests likely matches based on item, color, location, and date.

### How it works (high level)

- `lfbot/nlp.py` uses spaCy and simple rules to infer intent and extract fields.
- `lfbot/storage.py` stores reports in a local JSON file and provides a naive scoring-based search.
- `bot.py` wires the Telegram message flow using `python-telegram-bot`.

### Requirements

- Python 3.9+
- A Telegram bot token from BotFather

### Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env
edit .env  # put your TELEGRAM_BOT_TOKEN
```

### Run the bot

```bash
python bot.py
```

The bot will start polling. Send your bot a message on Telegram. Try:

- "I lost my red wallet at the library yesterday"
- "Found a blue water bottle near the gym"
- "Looking for a black backpack near cafeteria"

### How to verify it works

1. After starting the bot, send a "found" message (e.g., "Found black backpack near cafeteria today"). The bot should confirm it saved the report.
2. Send a corresponding "lost" message (e.g., "I lost my black backpack near the cafeteria"). The bot should reply with a potential match including the previously saved report details.
3. Send a "search" message (e.g., "Looking for black backpack near cafeteria"). The bot should return similar matches from stored reports.

### Limitations and behavior on unexpected input

- The NLP is intentionally lightweight. If the bot cannot confidently infer intent, it asks for a clearer message containing "lost" or "found".
- Field extraction (item/color/location/date) is heuristic. Vague or unusual phrasing may yield missing or incorrect fields.
- Storage is local JSON without authentication; all reports are saved in `data/reports.json`. Do not place sensitive data.
- Matching is a simple scoring mechanism; it may produce false positives or miss true matches.
- No background notifications are implemented; matching occurs at message time only.
- If the spaCy model `en_core_web_sm` is not installed, the bot raises a clear error with installation instructions.

### Repository and environment notes

- `.gitignore` excludes `.venv/`, build artifacts, and runtime data.
- `requirements.txt` allows you to recreate the environment.
- Use a virtual environment as shown above; do not commit it to the repo.

### File overview

- `bot.py`: Telegram bot entrypoint and handlers (single root-level .py as entry point).
- `lfbot/nlp.py`: spaCy-based parsing of intent and attributes.
- `lfbot/storage.py`: JSON persistence and naive search.
- `lfbot/config.py`: Environment configuration loader.
- `.env.example`: Template for required environment variables.
- `requirements.txt`: Dependencies.
- `.gitignore`: Excludes `.venv/` and other artifacts.
- `examples/BeautifulSoup.py`: Moved example script (not part of the bot). 
