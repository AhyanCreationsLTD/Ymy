import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# গিটহাব এবং বটের কনফিগারেশন (এগুলো এনভায়রনমেন্ট ভেরিয়েবলে বা ইউজারের সেটিংসে থাকবে)
GITHUB_TOKEN = "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"
GITHUB_OWNER = "AhyanCreationsLTD"
GITHUB_REPO = "Ymy"
WORKFLOW_FILE = "live.yml"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "স্বাগতম! লাইভ শুরু করতে নিচের নিয়মে কমান্ড দিন:\n\n"
        "/live [Video_URL] [Stream_Key]\n\n"
        "উদাহরণ:\n/live https://example.com/video.mp4 rtmp://a.rtmp.youtube.com/live2/xxxx-xxxx"
    )

async def start_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("ভুল ফরম্যাট! দয়া করে Video URL এবং YouTube Stream Key দিন।")
        return

    video_url = args[0]
    stream_key = args[1]
    rtmp_full_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

    # GitHub API কল করে Workflow Dispatch ট্রিগার করা
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "vnd.github+json"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "video_url": video_url,
            "rtmp_url": rtmp_full_url
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 204:
        await update.message.reply_text("✅ সফল! আপনার ইউটিউব লাইভ স্ট্রিম শুরু হয়ে গেছে। বন্ধ করতে চাইলে /stop কমান্ড দিন।")
    else:
        await update.message.reply_text(f"❌ লাইভ শুরু করতে সমস্যা হয়েছে: {response.text}")

async def stop_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # রানিং থাকা অ্যাকশন খুঁজে বের করে তা ক্যানসেল করার লজিক এখানে যুক্ত করতে হবে
    await update.message.reply_text("🛑 লাইভ বন্ধ করার প্রক্রিয়া চলছে...")
    
    # গিটহাব থেকে রানিং অ্যাকশনের Run ID বের করে তা ক্যানসেল করার API কল এখানে বসাতে হবে।
    # (প্রয়োজনে এর সম্পূর্ণ কোডটি পরে দিয়ে দেওয়া যাবে)

def main():
    app = ApplicationBuilder().token("8907004985:AAE7Hqyob8VHwk2o4oQg81HiF2hA7TQtVIs").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", start_live))
    app.add_handler(CommandHandler("stop", stop_live))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
