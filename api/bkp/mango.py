from pymongo import MongoClient

# client = MongoClient("mongodb://localhost:27017/")
client = MongoClient("mongodb+srv://tcguser:A539ouca6IWf671S@cluster0.gb3pk.mongodb.net/?retryWrites=true&w=majority")
db = client["tcg"]
fab_collection = db["fab_cards"]
onepiece_collection = db["onepiece_cards"]
sorcery_collection = db["sorcery_cards"]
riftbound_collection = db["riftbound_cards"]
yugi_collection = db["yugioh_cards"]

def contar_docs(collec, query):
    return db[collec].count_documents(query)

def yugi_cole(query, page, limit):
    cursor = (
        yugi_collection.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = []
    for card in cursor:
        formatted = {
            "id": str(card.get("id")),
            "code": str(card.get("id")),
            "name": card.get("name"),
            "type": card.get("type"),
            "attribute": card.get("attribute"),
            "race": card.get("race"),
            "level": card.get("level"),
            "atk": card.get("atk"),
            "def": card.get("def"),
            "archetype": card.get("archetype"),
            "effect": card.get("desc"),
            "images": {"small": None, "large": None},
            "variants": []
        }

        images = card.get("card_images", [])
        if isinstance(images, list) and images:
            img = images[0]
            formatted["images"]["small"] = img.get("image_url_small")
            formatted["images"]["large"] = img.get("image_url")

        card_sets = card.get("card_sets", [])
        for s in card_sets:
            formatted["variants"].append({
                "set_code": s.get("set_code"),
                "set_rarity": s.get("set_rarity"),
                "set_price": s.get("set_price"),
                "tcgplayerId": s.get("tcgplayerId"),
                "juSTname": s.get("juSTname"),
                "condition": s.get("condition"),
                "language": s.get("language"),
                "lowPrice": s.get("lowPrice"),
                "midPrice": s.get("midPrice"),
                "marketPrice": s.get("marketPrice"),
                "highPrice": s.get("highPrice")
            })

        data.append(formatted)
    return data

def fab_cole(query, page, limit):
    cursor = (
        fab_collection.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = []
    for card in cursor:
        formatted = {
            "id": card.get("unique_id"),
            "code": card.get("unique_id"),
            "name": card.get("name"),
            "color": card.get("color"),
            "type": card.get("type_text"),
            "types": card.get("types", []),
            "traits": card.get("traits", []),
            "keywords": card.get("card_keywords", []),
            "cost": card.get("cost"),
            "pitch": card.get("pitch"),
            "power": card.get("power"),
            "defense": card.get("defense"),
            "hp": card.get("health"),
            "intelligence": card.get("intelligence"),
            "effect": card.get("functional_text"),
            "effect_plain": card.get("functional_text_plain"),
            "playedHorizontally": card.get("played_horizontally", False),
            "legalities": {
                "blitz": card.get("blitz_legal", False),
                "classicConstructed": card.get("cc_legal", False),
                "commoner": card.get("commoner_legal", False),
                "upfBanned": card.get("upf_banned", False)
            },
            "variants": []
        }

        printings = card.get("printings", [])
        for p in printings:
            formatted["variants"].append({
                "set_code": p.get("set_id"),
                "rarity": p.get("rarity"),
                "foiling": p.get("foiling"),
                "edition": p.get("edition"),
                "artist": p.get("artists", [None])[0] if p.get("artists") else None,
                "image": p.get("image_url"),
                "tcgplayer_id": p.get("tcgplayer_product_id"),
                "tcgplayer_url": p.get("tcgplayer_url"),
                "set_printing_id": p.get("set_printing_unique_id"),
                "unique_id": p.get("unique_id"),
            })

        if formatted["variants"]:
            formatted["images"] = {
                "small": formatted["variants"][0]["image"],
                "large": formatted["variants"][0]["image"]
            }
        else:
            formatted["images"] = {"small": None, "large": None}

        data.append(formatted)
    return data

def sorcery_cole(query, page, limit):
    cursor = (
        sorcery_collection.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = []
    for card in cursor:
        formatted = {
            "id": str(card.get("id")),
            "code": str(card.get("id")),
            "name": card.get("name"),
            "element": card.get("elements"),
            "type": card.get("guardian", {}).get("type"),
            "subTypes": card.get("subTypes", []),
            "rarity": card.get("guardian", {}).get("rarity"),
            "cost": card.get("guardian", {}).get("cost"),
            "effect": card.get("guardian", {}).get("rulesText"),
            "images": {"small": None, "large": None},
            "variants": []
        }

        # achata sets[] e variants[] como no seu código original
        unified_variants = []
        for s in card.get("sets", []):
            set_name = s.get("name", "")
            for v in s.get("variants", []):
                flat = {
                    "set": set_name,
                    "finish": v.get("finish"),
                    "product": v.get("product"),
                    "image": v.get("image"),
                }
                unified_variants.append(flat)
        formatted["variants"] = unified_variants

        # define imagem principal
        if formatted["variants"]:
            img = formatted["variants"][0].get("image")
            formatted["images"] = {"small": img, "large": img}
        else:
            formatted["images"] = {"small": None, "large": None}

        data.append(formatted)
    return data

def rift_cole(query, page, limit):
    cursor = (
        riftbound_collection.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = []
    for card in cursor:
        formatted = {
            "id": card.get("id"),
            "code": card.get("code") or card.get("number"),
            "name": card.get("name"),
            "type": card.get("cardType"),
            "rarity": card.get("rarity"),
            "domain": card.get("domain"),
            "energyCost": card.get("energyCost"),
            "powerCost": card.get("powerCost"),
            "might": card.get("might"),
            "effect": card.get("description"),
            "flavorText": card.get("flavorText"),
            "images": {
                "small": card.get("images", {}).get("small"),
                "large": card.get("images", {}).get("large"),
            },
            "set": {
                "id": card.get("set", {}).get("id"),
                "name": card.get("set", {}).get("name"),
                "releaseDate": card.get("set", {}).get("releaseDate"),
            },
            "variants": [],
        }

        for v in card.get("variants", []):
            formatted["variants"].append({
                "tcgplayerId": v.get("tcgplayerId"),
                "juSTname": v.get("juSTname"),
                "condition": v.get("condition"),
                "printing": v.get("printing"),
                "language": v.get("language"),
                "lowPrice": v.get("lowPrice"),
                "midPrice": v.get("midPrice"),
                "highPrice": v.get("highPrice"),
                "marketPrice": v.get("marketPrice")
            })

        # garante estrutura consistente
        if not formatted["variants"]:
            formatted["variants"] = []

        data.append(formatted)
    return data

def op_cole(query, page, limit):
    cursor = (
        onepiece_collection.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = []
    for card in cursor:
        formatted = {
            "id": card.get("id"),
            "code": card.get("code"),
            "name": card.get("name"),
            "type": card.get("type"),
            "rarity": card.get("rarity"),
            "color": card.get("color"),
            "family": card.get("family"),
            "attribute": card.get("attribute", {}).get("name"),
            "attribute_img": card.get("attribute", {}).get("image"),
            "cost": card.get("cost"),
            "power": card.get("power"),
            "counter": card.get("counter"),
            "ability": card.get("ability"),
            "trigger": card.get("trigger"),
            "effect": card.get("ability"),  # pra manter compatibilidade de campo
            "images": {
                "small": card.get("images", {}).get("small"),
                "large": card.get("images", {}).get("large")
            },
            "set": {
                "id": card.get("set", {}).get("groupId"),
                "set_code": card.get("set", {}).get("set_code"),
                "name": card.get("set", {}).get("name"),
                "beauty_name": card.get("set", {}).get("beauty_name"),
                "product_type": card.get("set", {}).get("product_type"),
                "release_date": card.get("set", {}).get("release_date")
            },
            "variants": []
        }

        for v in card.get("variants", []):
            formatted["variants"].append({
                "tcgplayerId": v.get("tcgplayerId"),
                "juSTname": v.get("juSTname"),
                "condition": v.get("condition"),
                "printing": v.get("printing"),
                "language": v.get("language"),
                "price": v.get("price"),
                "avgPrice": v.get("avgPrice"),
                "lowPrice": v.get("lowPrice"),
                "midPrice": v.get("midPrice"),
                "highPrice": v.get("highPrice"),
                "marketPrice": v.get("marketPrice")
            })

        data.append(formatted)
    return data
