import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# সরাসরি কোডের ভেতরে টোকেন ও কনফিগারেশন সেট করা হলো
GITHUB_TOKEN = "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"
GITHUB_OWNER = "AhyanCreationsLTD"
GITHUB_REPO = "Ymy"
WORKFLOW_FILE = "live.yml"
TELEGRAM_TOKEN = "8907004985:AAE7Hqyob8VHwk2o4oQg81HiF2hA7TQtVIs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # টেলিগ্রাম চ্যাট বক্সের নিচে স্থায়ী বাটন তৈরি করার লেআউট
    keyboard = [
        ["🚀 লাইভ শুরু করুন", "🛑 লাইভ বন্ধ করুন"],
        ["ℹ️ সাহায্য/নিয়মাবলী"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🤖 বট সক্রিয় আছে!\n\n"
        "নিচের বাটনগুলো ব্যবহার করে অথবা সরাসরি কমান্ড লিখে কাজ করতে পারেন:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 **ব্যবহারের নিয়ম:**\n\n"
        "লাইভ শুরু করতে এই ফরম্যাটে লিখুন:\n"
        "`/live [Video_URL] [Stream_Key]`\n\n"
        "উদাহরণ:\n"
        "`/live https://example.com/video.mp4 your_stream_key_here`\n\n"
        "অথবা লাইভ বন্ধ করতে `/stop` লিখুন।"
    )

async def start_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ইউজার যদি বাটন চাপেন কিংবা সরাসরি কমান্ড লেখেন, দুটো থেকেই হ্যান্ডেল করার লজিক
    args = context.args
    
    # যদি ইউজার সরাসরি "🚀 লাইভ শুরু করুন" বাটন চাপেন কিন্তু লিংক না দেন
    if not args or len(args) < 2:
        await update.message.reply_text(
            "❌ সঠিক ফরম্যাটে লিংক দিন!\n\n"
            "ব্যবহারের নিয়ম:\n"
            "`/live [Video_URL] [Stream_Key]`"
        )
        return

    video_url = args[0]
    stream_key = args[1]
    rtmp_full_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

    # GitHub API কল করে Workflow Dispatch ট্রিগার করা
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "action_type": "stream",
            "video_url": video_url,
            "rtmp_url": rtmp_full_url
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 204:
        await update.message.reply_text("✅ সফল! আপনার ইউটিউব লাইভ স্ট্রিম শুরু হয়ে গেছে।")
    else:
        await update.message.reply_text(f"❌ লাইভ শুরু করতে সমস্যা হয়েছে: {response.text}")

async def stop_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 লাইভ বন্ধ করার প্রক্রিয়া চলছে...")
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    runs_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs?status=in_progress"
    res = requests.get(runs_url, headers=headers)
    
    if res.status_code == 200:
        runs = res.json().get("workflow_runs", [])
        if runs:
            run_id = runs[0]["id"]
            cancel_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}/cancel"
            cancel_res = requests.post(cancel_url, headers=headers)
            
            if cancel_res.status_code == 202:
                await update.message.reply_text("✅ লাইভ সফলভাবে বন্ধ (Cancel) করা হয়েছে!")
                return
                
    await update.message.reply_text("⚠️ কোনো রানিং লাইভ স্ট্রিম পাওয়া যায়নি বা বন্ধ করতে সমস্যা হয়েছে।")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", start_live))
    app.add_handler(CommandHandler("stop", stop_live))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot is running with buttons...")
    app.run_polling()

if __name__ == "__main__":
    main()
