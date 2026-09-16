import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# গিটহাব এবং বটের কনফিগারেশন
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "AhyanCreationsLTD")
GITHUB_REPO = os.getenv("GITHUB_REPO", "Ymy")
WORKFLOW_FILE = "live.yml"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 বট সক্রিয় আছে!\n\n"
        "লাইভ শুরু করতে নিচের নিয়মে কমান্ড দিন:\n"
        "/live [Video_URL] [Stream_Key]\n\n"
        "লাইভ বন্ধ করতে কমান্ড দিন:\n"
        "/stop"
    )

async def start_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ ভুল ফরম্যাট! দয়া করে Video URL এবং YouTube Stream Key দিন।\nউদাহরণ: /live https://link.com/video.mp4 xxxx-xxxx-xxxx")
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

    # ১. প্রথমে দেখা যাক বর্তমানে কোন অ্যাকশনটি রানিং আছে (in_progress)
    runs_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs?status=in_progress"
    res = requests.get(runs_url, headers=headers)
    
    if res.status_code == 200:
        runs = res.json().get("workflow_runs", [])
        if runs:
            # রানিং অ্যাকশনের ID বের করে সেটি ক্যানসেল করা
            run_id = runs[0]["id"]
            cancel_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs/{run_id}/cancel"
            cancel_res = requests.post(cancel_url, headers=headers)
            
            if cancel_res.status_code == 202:
                await update.message.reply_text("✅ লাইভ সফলভাবে বন্ধ (Cancel) করা হয়েছে!")
                return
                
    await update.message.reply_text("⚠️ কোনো রানিং লাইভ স্ট্রিম পাওয়া যায়নি বা বন্ধ করতে সমস্যা হয়েছে।")

def main():
    token = os.getenv("TELEGRAM_TOKEN", "8907004985:AAE7Hqyob8VHwk2o4oQg81HiF2hA7TQtVIs")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", start_live))
    app.add_handler(CommandHandler("stop", stop_live))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
