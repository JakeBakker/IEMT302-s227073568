#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict
from uuid import uuid4

import spacy  # noqa: F401
import telegram  # noqa: F401

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from lfbot.config import load_config
from lfbot.nlp import LostFoundNLP
from lfbot.storage import add_report, initialize_storage, search_reports


def _format_report(record: Dict) -> str:
    parts = [
        f"Type: {record.get('type').title()}",
        f"Item: {record.get('item') or 'Unknown'}",
        f"Color: {record.get('color') or 'Unknown'}",
        f"Location: {record.get('location') or 'Unknown'}",
        f"Date: {record.get('date_iso') or 'Unknown'}",
        f"User: @{record.get('username') or record.get('user_id')}"
    ]
    return "\n".join(parts)


class LostFoundBot:
    def __init__(self, token: str) -> None:
        self.application = Application.builder().token(token).build()
        self.nlp = LostFoundNLP()
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("report", self.handle_report))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Hi! I help match lost and found items.\n"
            "Describe what you lost/found, for example:\n"
            "- I lost my red wallet at the library yesterday\n"
            "- Found a blue water bottle near the gym\n"
            "Or search: 'Looking for a black backpack near cafeteria'"
        )

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Tips:\n\n"
            "Include item, color, location, and date/time if possible.\n"
            "Examples:\n"
            "- I lost my gray headphones in Room 204 on Monday\n"
            "- I found a set of keys by Parking Lot B today\n"
            "- Looking for a calculator left in the library"
        )

    async def handle_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Please send a message describing the item. Example: 'I lost my red wallet at the library yesterday'"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is None:
            return
        text = update.message.text
        parsed = self.nlp.parse(text)
        intent = parsed.get("intent")

        if intent in {"lost", "found"}:
            record = {
                "id": str(uuid4()),
                "type": intent,
                "item": parsed.get("item"),
                "color": parsed.get("color"),
                "location": parsed.get("location"),
                "date_iso": parsed.get("date_iso"),
                "user_id": update.effective_user.id if update.effective_user else None,
                "username": update.effective_user.username if update.effective_user else None,
                "text": text,
            }
            add_report(record)

            opposite_type = "found" if intent == "lost" else "lost"
            matches = search_reports(
                {
                    "type": opposite_type,
                    "item": record.get("item"),
                    "color": record.get("color"),
                    "location": record.get("location"),
                    "date_iso": record.get("date_iso"),
                }
            )

            if matches:
                formatted = "\n\n".join(_format_report(m) for m in matches)
                await update.message.reply_text(
                    f"Thanks! I saved your {intent} report. Here are potential matches:\n\n{formatted}"
                )
            else:
                await update.message.reply_text(
                    f"Thanks! I saved your {intent} report. No immediate matches, but I'll keep looking."
                )
            return

        if intent == "search":
            matches = search_reports(
                {
                    "type": "found",
                    "item": parsed.get("item"),
                    "color": parsed.get("color"),
                    "location": parsed.get("location"),
                    "date_iso": parsed.get("date_iso"),
                }
            )
            if matches:
                formatted = "\n\n".join(_format_report(m) for m in matches)
                await update.message.reply_text(f"Here are possible matches:\n\n{formatted}")
            else:
                await update.message.reply_text(
                    "I couldn't find any matches. Try adding color, location, or date."
                )
            return

        await update.message.reply_text(
            "I didn't quite get that. Please say if you 'lost' or 'found' something, "
            "for example: 'I lost my red wallet at the library yesterday'."
        )

    def run(self) -> None:
        initialize_storage()
        self.application.run_polling()


def main() -> None:
    config = load_config()
    bot = LostFoundBot(config.telegram_bot_token)
    bot.run()


if __name__ == "__main__":
    main()

