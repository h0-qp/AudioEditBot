import os
import threading
import asyncio
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, APIC
from pyromod import listen # for ask
from sqldb import db
import static_ffmpeg

# تفعيل ffmpeg حتى يشتغل قص الصوت بدون مشاكل على سيرفرات Render
static_ffmpeg.add_paths()

# --- إعداد السيرفر الوهمي (Flask) لـ Render ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "البوت يعمل بنجاح على Render!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()
# ----------------------------------------------

db.autocommit = True

api_id = 28222279
api_hash = "bf76ce65a3af59f3565f63501800aa14" 
bot_token = os.getenv("BOT_TOKEN") 

app_name = "audiobot"
if os.path.exists(f"{app_name}.session"):
    os.remove(f"{app_name}.session")
if os.path.exists(f"{app_name}.session-journal"):
    os.remove(f"{app_name}.session-journal")

app = Client(app_name, api_id=api_id, api_hash=api_hash, bot_token=bot_token)

TEMP_DIR = "downloads/"
if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)

in_msg = """
✨ دخل عضو جديد للبوت
👤 الاسم: {} 🆔 الايدي: {} 🌐 المعرف: @{}
📊 عدد أعضاء البوت الآن: {} عضو
"""

# ايدي المطور (أنت)
dev_id = 1160471152 

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user = message.from_user
    id = user.id
    name = user.first_name
    username = user.username
    mention = user.mention
    await message.reply("مرحبا بك! في بوت تعديل الصوت وقصه. فقط أرسل الملف الصوتي واتبع التعليمات :).")
    
    try:
        members = db.get("users")
        if members is None:
            members = [] # في حال كانت القاعدة فارغة
            
        if id not in members:
            members.append(id)
            db.set("users", members)
            number = len(members)
            # تصحيح الخطأ: تم تغيير bot الى client وإضافة dev_id
            await client.send_message(dev_id, in_msg.format(mention, id, username, number))
    except Exception as e:
        print(f"Database Error: {e}")

@app.on_message(filters.audio)
async def get_audio(client, message: Message):
    user = message.from_user
    id = user.id
    name = user.first_name
    username = user.username
    mention = user.mention
    await client.send_message(
        dev_id,
        f"""
عضو يستخدم البوت الان
معلوماته:
اسمه: {mention}
ايديه: {id}
يوزره: @{username}
        """
    )
    
    # تأمين اسم الملف
    safe_file_name = message.audio.file_name if message.audio.file_name else f"audio_{id}.mp3"
    file_name = os.path.join(TEMP_DIR, safe_file_name)
    await message.download(file_name)
    
    ask_for_song_name = await message.chat.ask("تم استلام الملف الصوتي! أرسل اسم الأغنية:", filters=filters.text)
    song_name = ask_for_song_name.text
    
    ask_for_fnan = await message.chat.ask("تم تسجيل اسم الأغنية! أرسل اسم الفنان:", filters=filters.text)
    artist_name = ask_for_fnan.text
    
    photo = await message.chat.ask("تم تسجيل اسم الفنان! أرسل الصورة:", filters=filters.photo)
    image = await photo.download()
    image_path = f"{image}"
    
    start_and_end = await message.chat.ask("تم استلام الصورة! إذا كنت تريد قص الصوت، أرسل الوقت (من - إلى) بالشكل: 0:30-1:00، أو أرسل 'تخطي':", filters=filters.text)
    
    output_file = "output.mp3"
    try:
        start, end = None, None
        if start_and_end.text.lower() != "تخطي":
            times = start_and_end.text.split("-")
            start = int(times[0].split(":")[0]) * 60 + int(times[0].split(":")[1])
            end = int(times[1].split(":")[0]) * 60 + int(times[1].split(":")[1])
            
        audio = AudioSegment.from_file(file_name)
        
        if start is not None and end is not None:
            audio = audio[start * 1000:end * 1000]
            
        audio.export(output_file, format="mp3")
        audio_file = MP3(output_file, ID3=EasyID3)
        duration = int(audio_file.info.length)
        audio_file["title"] = song_name
        audio_file["artist"] = artist_name
        audio_file.save()
        print("تم قص المقطع الصوتي وحفظه بنجاح مع إضافة الصورة والبيانات.")
        
        await message.reply_audio(
            output_file,
            title=song_name,
            performer=artist_name,
            thumb=image_path,
            duration=duration,
            caption="تم تعديل الصوت بنجاح!\nBy: @jj8jjj8"
        )
    except Exception as e:
        await message.reply(f"حدث خطأ: {e}")
    finally:
        if os.path.exists(output_file): os.remove(output_file)
        if os.path.exists(file_name): os.remove(file_name)
        if os.path.exists(image_path): os.remove(image_path)

if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر بالخلفية
    print("The Bot Is Starting...")
    app.run() # تشغيل البوت بشكل مستمر
