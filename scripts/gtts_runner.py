import os
from gtts import gTTS
import time

STORY_DIR = "stories_text"
OUTPUT_DIR = "gtts"
COUNT_FILE = "processed_count.txt"
STORIES_PER_RUN = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read processed count
if os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, "r") as f:
        processed_count = int(f.read().strip())
else:
    processed_count = 0

# Collect files and reverse
all_files = sorted([f for f in os.listdir(STORY_DIR) if f.endswith(".txt")], reverse=True)
to_process = all_files[processed_count : processed_count + STORIES_PER_RUN]

success_count = 0

for i, filename in enumerate(to_process, start=processed_count + 1):
    txt_path = os.path.join(STORY_DIR, filename)
    base_name = os.path.splitext(filename)[0]
    mp3_path = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")

    #with open(txt_path, "r", encoding="utf-8") as f:
    #    text = f.read().replace('\n', ' ').strip()
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read().replace('\n', ' ').strip()
    
    # Add closing watermark and disclaimer
    closing_note = (
        " comment பண்ணுங்ங்கக.                                                                                    "
        "This video is part of an artistic Tamil audio series that explores the emotional and psychological depth "
        "of human relationships through narrated fiction. All characters and events are fictional and intended for "
        "mature literary appreciation."
    )
    
    text += closing_note
    
    try:
        tts = gTTS(text=text, lang='ta')
        tts.save(mp3_path)
        print(f"✅ Converted: {filename} to {mp3_path}")
        success_count += 1
    except Exception as e:
        success_count += 1
        print(f"❌ Error processing {filename}: {e}")
        break  # ❗ Stop further processing on any failure

    time.sleep(10)

# Update count based on successful conversions only
with open(COUNT_FILE, "w") as f:
    f.write(str(processed_count + success_count))
    print(f"✅ Count: {processed_count} + {success_count}")
