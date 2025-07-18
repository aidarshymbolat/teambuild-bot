from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

BOT_TOKEN = "7956103174:AAGag6FAferuuNSWq8wJJZNqKWiazE_wZQo"

# Состояния анкеты
FULL_NAME, AGE, COUNTRY, CONTACT, LOOKING_FOR, PURPOSE = range(6)

# Память профилей
user_profiles = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TeamBuild Bot!\n\n"
        "Available commands:\n"
        "/create - Create your profile\n"
        "/search - Search other profiles (one by one)\n"
        "/delete - Delete your profile"
    )

# === Шаги создания анкеты ===
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's create your profile! 📝\n\n What is your full name?")
    return FULL_NAME

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("How old are you?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("What country are you from?")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["country"] = update.message.text
    await update.message.reply_text("Please share your Telegram username or WhatsApp number:")
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    await update.message.reply_text("Who are you looking for? (e.g. co-founder, volunteer, teammate)")
    return LOOKING_FOR

async def get_looking_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["looking_for"] = update.message.text
    await update.message.reply_text("What is the purpose? (e.g. hackathon, startup, competition)")
    return PURPOSE

async def save_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["purpose"] = update.message.text
    user_id = update.message.from_user.id
    user_profiles[user_id] = context.user_data.copy()
    await update.message.reply_text("✅ Your profile has been created!")
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Profile creation cancelled.")
    return ConversationHandler.END

# Поиск анкет
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_profiles:
        await update.message.reply_text("There are no profiles yet. Try again later.")
        return

    user_id = update.message.from_user.id
    all_profiles = list(user_profiles.values())
    index = context.user_data.get("search_index", 0)

    if index >= len(all_profiles):
        await update.message.reply_text("✅ You've seen all profiles.")
        context.user_data["search_index"] = 0
        return

    profile = all_profiles[index]
    context.user_data["search_index"] = index + 1

    msg = (
        f"👤 Name: {profile['full_name']}\n"
        f"🎂 Age: {profile['age']}\n"
        f"🌍 Country: {profile['country']}\n"
        f"📱 Contact: {profile['contact']}\n"
        f"🔎 Looking for: {profile['looking_for']}\n"
        f"🎯 Purpose: {profile['purpose']}"
    )
    await update.message.reply_text(msg)

# Удаление анкеты
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_profiles:
        del user_profiles[user_id]
        await update.message.reply_text("🗑️ Your profile has been deleted.")
    else:
        await update.message.reply_text("❗ You don’t have a profile yet.")

# Главная функция
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            LOOKING_FOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_looking_for)],
            PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_profile)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("delete", delete))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
