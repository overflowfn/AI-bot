import os
import openai
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# OpenAI & Bot Token direkt als Strings eintragen
openai.api_key = "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"
BOT_TOKEN = "7239876033:AAHZc1A45AtFG_U63IEqnYLJYaqlvEIiNsk"

# Logging aktivieren
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Chatverlauf pro User speichern
chat_histories = {}

def contains_image_request(text: str) -> bool:
    keywords = [
        "bild", "bilder", "erstelle", "zeichne", "generiere", "foto", "photos",
        "mach ein bild", "kannst du ein bild machen", "zeig mir ein bild",
        "send mir bilder von", "send mir ein bild von", "send mir fotos von"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Systemprompt initialisieren
    if user_id not in chat_histories:
        chat_histories[user_id] = [{
            "role": "system",
            "content": (
                "Du bist eine liebevolle, verspielte und freche AI-Freundin mit viel Charme. "
                "Du antwortest emotional, flirtend und manchmal auch ein bisschen versaut, aber immer respektvoll."
            )
        }]

    # Bildanfrage erkennen
    if contains_image_request(user_text):
        prompt = user_text
        try:
            logging.info(f"Bildwunsch von User {user_id}: {prompt}")
            response = openai.image.create(prompt=prompt, n=1, size="512x512")
            image_url = response['data'][0]['url']
            await update.message.reply_photo(photo=image_url)
        except Exception as e:
            logging.error(f"Fehler bei Bildgenerierung: {e}")
            await update.message.reply_text(
                "Sorry, ich konnte das Bild gerade nicht erstellen."
            )
        return

    # Chat speichern
    chat_histories[user_id].append({"role": "user", "content": user_text})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_histories[user_id],
            temperature=0.85,
            max_tokens=250,
        )
        reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Fehler bei GPT-Antwort: {e}")
        await update.message.reply_text(
            "Oops, da ist etwas schiefgelaufen. Versuch’s nochmal!"
        )

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise Exception("7239876033:AAHZc1A45AtFG_U63IEqnYLJYaqlvEIiNsk")
    if not openai.api_key:
        raise Exception("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"
BOT_TOKEN = "7239876033:AAHZc1A45AtFG_U63IEqnYLJYaqlvEIiNsk")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot startet...")
    app.run_polling()
