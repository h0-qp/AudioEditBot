# استخدام نسخة بايثون خفيفة
FROM python:3.10-slim

# تحديد مجلد العمل
WORKDIR /app

# تنصيب برنامج ffmpeg الخاص بقص الصوت مباشرة على السيرفر
RUN apt-get update && apt-get install -y ffmpeg

# نسخ كل ملفات البوت للسيرفر
COPY . /app

# تنصيب المكاتب المطلوبة
RUN pip install -r requirements.txt

# فتح بورت للسيرفر الوهمي حتى المنصة ما تطفي البوت
EXPOSE 8080

# أمر تشغيل البوت (تأكد إن اسم ملفك هو main.py)
CMD ["python", "main.py"]
