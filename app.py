from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from deep_translator import GoogleTranslator
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YGO_API = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

# Smart translator function
def smart_translate(text, target="tr"):
    """
    Translate text but:
    - Leave all words in quotes ("…") intact
    - Leave card names (for now) intact
    """
    # Find quoted words
    quotes = re.findall(r'\".*?\"', text)
    placeholders = {f"__QUOTE_{i}__": q for i, q in enumerate(quotes)}

    # Replace quoted words with placeholders
    temp_text = text
    for key, q in placeholders.items():
        temp_text = temp_text.replace(q, key)

    # Translate the remaining text
    try:
        translated = GoogleTranslator(source="en", target=target).translate(temp_text)
    except Exception as e:
        print("Translation error:", e)
        translated = temp_text

    # Put quotes back
    for key, q in placeholders.items():
        translated = translated.replace(key, q)

    return translated

@app.get("/card")
def get_card(name: str, target_lang: str = "tr"):
    r = requests.get(YGO_API, params={"name": name})
    data = r.json()

    if "data" not in data:
        return {"error": "Card not found"}

    card = data["data"][0]

    desc = card["desc"]
    name_en = card["name"]

    return {
        "name": name_en,                 # Keep original card name
        "desc": desc,                     # Original effect
        "desc_translated": smart_translate(desc, target_lang),
        "image": card["card_images"][0]["image_url"],
    }