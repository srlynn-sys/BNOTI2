import asyncio
import logging
import requests
from telegram import Bot

# --- CONFIGURATION (Your Credentials) ---
TELEGRAM_BOT_TOKEN = "9265969326:AAGw_2OSQkE0bkLlJSJ5ffX8UW2gajKMaUw"
TELEGRAM_CHAT_ID = "5050699658"

# သင် စောင့်ကြည့်ချင်သော Creator နှစ်ဦး၏ Profile IDs များ
TARGET_CREATORS = [
    {"name": "Creator - C-H-I-N-A-", "user_id": "C-H-I-N-A-"},
    {"name": "Creator - Square-Creator", "user_id": "Square-Creator-d7802adf30bfd"},
]

CHECK_INTERVAL = 30  
seen_post_ids = set()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_latest_posts(user_id):
    url = "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    params = {
        "pageCode": "SQUARE_PROFILE",
        "pageSize": 5,
        "pageNo": 1,
        "keyword": user_id  # Creator အလိုက် ရှာဖွေရန်
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("catalogs", [])
        return []
    except Exception as e:
        logging.error(f"Error fetching posts for {user_id}: {e}")
        return []

async def send_telegram_message(title, body, url, creator_name):
    message = (
        f"🚨 **Binance Square Post အသစ် ရောက်ရှိလာပါပြီ!**\n\n"
        f"👤 **Creator:** {creator_name}\n"
        f"📌 **Title:** {title}\n\n"
        f"📝 {body[:300]}...\n\n"
        f"🔗 [Post ကို ဖတ်ရှုရန် ဒီမှာနှိပ်ပါ]({url})"
    )
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        logging.info(f"Notification sent for post: {title}")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

async def monitor_square():
    logging.info("Binance Square Real-time Monitoring စတင်နေပါပြီ...")
    
    # ပထမအကြိမ် စဖွင့်ချိန်တွင် ရှိပြီးသား Post ဟောင်းများကို မှတ်ထားမည် (ပလုံပလန်း မဖြစ်စေရန်)
    for creator in TARGET_CREATORS:
        posts = fetch_latest_posts(creator["user_id"])
        for post in posts:
            post_id = post.get("id")
            if post_id:
                seen_post_ids.add(post_id)

    while True:
        for creator in TARGET_CREATORS:
            creator_name = creator["name"]
            user_id = creator["user_id"]
            posts = fetch_latest_posts(user_id)
            
            for post in posts:
                post_id = post.get("id")
                title = post.get("title", "No Title")
                summary = post.get("brief", "No Content Preview")
                post_url = f"https://www.binance.com/en/square/post/{post_id}"
                
                if post_id and post_id not in seen_post_ids:
                    seen_post_ids.add(post_id)
                    await send_telegram_message(title, summary, post_url, creator_name)
                        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(monitor_square())
