from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

QUANTITY, CONFIRM = range(2)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CARD_NUMBER = os.getenv("CARD_NUMBER")
CARD_OWNER = os.getenv("CARD_OWNER")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buyurtma bermoqchi bolgan mahsulot kodini tashlang:")
    return QUANTITY

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_code = update.message.text.strip()
    if not product_code:
        await update.message.reply_text("❌ Iltimos, mahsulot kodini kiriting!")
        return QUANTITY
    context.user_data["product_code"] = product_code
    await update.message.reply_text(f"✅ Mahsulot kodi: {product_code}\n\nTo'lovni tasdiqlaysizmi? (ha/yo'q)")
    return CONFIRM

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text == "ha":
        product_code = context.user_data.get("product_code")
        payment_text = f"💳 To'lov ma'lumotlari:\n\nKarta: {CARD_NUMBER}\nEgasi: {CARD_OWNER}\n\nMahsulot kodi: {product_code}\n\nTo'lovni amalga oshirgandan so'ng, screenshotni yuboring."
        await update.message.reply_text(payment_text)
        admin_text = f"🔔 Yangi buyurtma!\n\nFoydalanuvchi: {update.message.from_user.first_name}\nID: {update.message.from_user.id}\nMahsulot kodi: {product_code}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        return ConversationHandler.END
    elif text == "yo'q":
        await update.message.reply_text("❌ Bekor qilindi. /start ni bosing.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❓ Iltimos, 'ha' yoki 'yo'q' deb yozing.")
        return CONFIRM

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_payment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()