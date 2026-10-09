import os, asyncio, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtubesearchpython import VideosSearch
import yt_dlp

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Main Rahul Bot hu 🎵\n/play <gaana> - Gaana bhejunga\nEx: /play kesariya")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gaane ka naam likh! Ex: /play apna bana le")
        return
    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 '{query}' search...")
    try:
        search = VideosSearch(query, limit=1)
        video = search.result()['result'][0]
        title=video['title']; link=video['link']
        await msg.edit_text(f"⬇️ '{title}' download...")
        ydl_opts={'format':'bestaudio/best','outtmpl':'/tmp/%(title)s.%(ext)s','postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192',}],'quiet':True,'noplaylist':True,}
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                fname = ydl.prepare_filename(info)
                return fname.rsplit('.',1)[0]+".mp3"
        mp3_file = await asyncio.to_thread(download)
        await msg.edit_text(f"📤 Bhej raha hu...")
        with open(mp3_file,'rb') as f:
            await update.message.reply_audio(audio=f, title=title[:64], caption=f"🎵 {title}\n{link}")
        os.remove(mp3_file)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.run_polling()

if __name__ == "__main__":
    main()
