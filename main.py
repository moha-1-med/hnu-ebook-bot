import os
import re
import json
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8434370493:AAEI0vpHNqZbx4V40QzMfbvh6hcv6YSRLkY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت كتب جامعة حلوان!\n"
        "أرسل لي رابط الكتاب من المنصة أو رقم الـ Storage ID (مثلاً: 23564) وسأقوم بتحميله وتجهيزه لك كملف PDF و EPUB فوراً!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    match = re.search(r'storage/(\d+)', text)
    book_id = match.group(1) if match else (text if text.isdigit() else None)

    if not book_id:
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يحتوي على storage/رقم أو إرسال الرقم فقط.")
        return

    msg = await update.message.reply_text(f"⏳ جاري فحص الكتاب رقم {book_id} وسحب الملفات من السيرفر...")

    base_url = f"https://e-books.hnu.edu.eg/storage/{book_id}/"
    pkg_url = f"{base_url}epub/EPUB/package.xml"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(pkg_url) as resp:
                if resp.status != 200:
                    await msg.edit_text("❌ لم يتم العثور على هذا الكتاب على السيرفر!")
                    return
                xml_content = await resp.text()
        except Exception as e:
            await msg.edit_text(f"❌ حدث خطأ أثناء الاتصال: {str(e)}")
            return

    # استخراج عنوان الكتاب
    title_match = re.search(r'<dc:title[^>]*>(.*?)</dc:title>', xml_content)
    book_title = title_match.group(1) if title_match else f"Book_{book_id}"

    await msg.edit_text(f"📖 تم العثور على: {book_title}\nجاري سحب الصفحات وتجهيز الملفات...")

    # هنا يتم استدعاء نفس دالة تجميع الملفات والتحويل
    # ثم إرسال الملف الناتج للمستخدم:
    # await update.message.reply_document(document=open(pdf_path, 'rb'), caption=f"📄 {book_title}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
