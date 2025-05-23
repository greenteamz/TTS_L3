import os
import re
import time
import requests
from bs4 import BeautifulSoup
#from gtts import gTTS
from datetime import datetime

# ======= Config =======
MAX_PAGES = 2310
OUTPUT_DIR = "stories_text"
STORY_SELECTOR = "h2.entry-title a"
CONTENT_SELECTOR = "div.entry-content"
BASE_URL = "https://tamilsexstories.info/page/{}/"
DELAY_SECONDS = 0
# ======================

now = datetime.now()
date_str = now.strftime("%Y%m%d")
time_str = now.strftime("%H%M")

os.makedirs(OUTPUT_DIR, exist_ok=True)
debug_log_path = os.path.join(OUTPUT_DIR, f"debug_{date_str}_{time_str}.txt")

# 🟡 Step 1: Load existing titles from saved .wav files
existing_titles = set()
for f in os.listdir(OUTPUT_DIR):
    if f.endswith(".wav"):
        match = re.match(r"Story_(.+?)_\d{8}_\d{4}_Page\d+_\d+_\d+\.wav", f)
        if match:
            existing_titles.add(match.group(1))

debug_entries = []
count = 8245

# 🟡 Step 2: Start scraping
for page in range(1201, MAX_PAGES + 1):
    try:
        page_url = BASE_URL.format(page)
        print(f"\n📄 Page {page} -> {page_url}")
        res = requests.get(page_url)
        soup = BeautifulSoup(res.content, "html.parser")

        links = soup.select(STORY_SELECTOR)

        for idx, link in enumerate(links, start=1):
            title = link.get_text(strip=True)
            #title = title.strip()
            story_url = link["href"]
            print(f"▶️  [{count}] Page {page} - {title}")

            # Make safe title
            #safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
            safe_title = re.sub(r"[^\w\s-]", "", title).strip()
            
            # Only remove these 9 illegal characters for Windows
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()

            safe_title = safe_title.replace(" ", "_")


            if safe_title in existing_titles:
                print(f"⏭️  Skipping (already processed): {safe_title}")
                continue

            # Fetch story content
            story_res = requests.get(story_url)
            story_soup = BeautifulSoup(story_res.content, "html.parser")
            content_div = story_soup.select_one(CONTENT_SELECTOR)

            if not content_div:
                print("⚠️  No content found.")
                continue

            content = content_div.get_text(separator="\n", strip=True)
            content = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", "", content)
            
            # Truncate from 'Like'
            cut_index = content.lower().find("like")
            if cut_index != -1:
                content = content[:cut_index].strip()

            # ✅ Add watermark line
            watermark = "\n\nஇந்தக் கதை முடிந்தது. தொடர்ந்து கதைகளை அனுபவிக்கவும்.    Like    Subscribe   share and Comment what you want. உங்களுக்கு என்ன வேணும்னு"
            content += watermark
            
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M")

            base_name = f"{count}_{page}_{idx}_{date_str}_{time_str}_{safe_title}"
            txt_path = os.path.join(OUTPUT_DIR, base_name + ".txt")
            #wav_path = os.path.join(OUTPUT_DIR, base_name + ".wav")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(content)

            #tts = gTTS(text=content, lang="ta")
            #tts.save(wav_path)

            debug_entries.append(f"{count}. Page {page}, Title: {title}\nURL: {story_url}\n")
            existing_titles.add(safe_title)  # Add to set after saving
            count += 1

            time.sleep(DELAY_SECONDS)

    except Exception as e:
        print(f"❌ Error on page {page}: {e}")
        continue

# 🟡 Step 3: Write debug log
with open(debug_log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(debug_entries))

print(f"\n✅ Done. {count - 1} stories processed and saved in '{OUTPUT_DIR}'.")
