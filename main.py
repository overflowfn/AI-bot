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

# === Tokens aus Umgebungsvariablen laden ===
openai.api_key = os.getenv("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")
BOT_TOKEN = os.getenv("7239876033:AAHZc1A45AtFG_U63IEqnYLJYaqlvEIiNsk")

if not BOT_TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN fehlt! In .env oder Umgebungsvariable setzen.")
if not openai.api_key:
    raise Exception("OPENAI_API_KEY fehlt! In .env oder Umgebungsvariable setzen.")

# === Logging aktivieren ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# === Chatverlauf pro User ===
chat_histories = {}

# === Bildanfrage erkennen ===
def contains_image_request(text: str) -> bool:
    keywords = [
        "bild", "bilder", "erstelle", "zeichne", "generiere", "foto", "photos",
        "mach ein bild", "kannst du ein bild machen", "zeig mir ein bild",
        "send mir bilder von", "send mir ein bild von", "send mir fotos von"
    ]
    return any(keyword in text.lower() for keyword in keywords)

# === Haupt-Handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Systemprompt nur einmal pro User
    if user_id not in chat_histories:
        chat_histories[user_id] = [{
            "role": "system",
            "content": (
                "Du bist eine liebevolle, verspielte AI-Freundin. "
                "Du antwortest charmant, emotional und frech, aber respektvoll."
            )
        }]

    # === Bildanfrage verarbeiten ===
    if contains_image_request(user_text):
        try:
            logging.info(f"Bildwunsch von User {user_id}: {user_text}")
            response = openai.images.generate(prompt=user_text, n=1, size="512x512")
            image_url = response.data[0].url
            await update.message.reply_photo(photo=image_url)
        except Exception as e:
            logging.error(f"Fehler bei Bildgenerierung: {e}")
            await update.message.reply_text("Sorry, konnte kein Bild erstellen.")
        return

    # === Textantwort verarbeiten ===
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
        await update.message.reply_text("Oops, da ist was schiefgelaufen.")

# === Bot starten ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Bot startet...")
    app.run_polling()
