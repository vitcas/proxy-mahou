from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient("mongodb+srv://tcguser:A539ouca6IWf671S@cluster0.gb3pk.mongodb.net/?retryWrites=true&w=majority")
db = client["tcg"]
fab_collection = db["fab_cards"]
yugi_collection = db["yugioh_cards"]

fab_schema = {
    "unique_id": {"type": "string", "target": "id"},
    "name": {"type": "string", "target": "name"},
    "color": {"type": "string", "target": "color"},
    "cost": {"type": "string|int", "target": "cost"},
    "pitch": {"type": "string|int", "target": "pitch"},
    "power": {"type": "string|int", "target": "power"},
    "defense": {"type": "string|int", "target": "defense"},
    "health": {"type": "string|int", "target": "hp"},
    "intelligence": {"type": "string|int", "target": "intelligence"},
    "type_text": {"type": "string", "target": "type"},
    "types": {"type": "list[string]", "target": "types"},
    "traits": {"type": "list[string]", "target": "traits"},
    "card_keywords": {"type": "list[string]", "target": "keywords"},
    "functional_text": {"type": "string", "target": "effect"},
    "functional_text_plain": {"type": "string", "target": "effect_plain"},
    "played_horizontally": {"type": "bool", "target": "playedHorizontally"},
    # legalidades e banimentos
    "blitz_legal": {"type": "bool", "target": "legalities.blitz"},
    "cc_legal": {"type": "bool", "target": "legalities.classicConstructed"},
    "commoner_legal": {"type": "bool", "target": "legalities.commoner"},
    "upf_banned": {"type": "bool", "target": "legalities.upfBanned"},
    # printing principal
    "printings": {"type": "list[dict]", "target": "variants"}
}

swu_schema = {
    "Set": {"type": "string", "target": "set.set_code"},
    "Number": {"type": "string", "target": "number"},
    "Name": {"type": "string", "target": "name"},
    "Subtitle": {"type": "string", "target": "subtitle"},
    "Type": {"type": "string", "target": "type"},
    "Aspects": {"type": "list[string]", "target": "aspects"},
    "Traits": {"type": "list[string]", "target": "traits"},
    "Arenas": {"type": "list[string]", "target": "arenas"},
    "Cost": {"type": "string|int", "target": "cost"},
    "Power": {"type": "string|int", "target": "power"},
    "HP": {"type": "string|int", "target": "hp"},
    "FrontText": {"type": "string", "target": "frontText"},
    "EpicAction": {"type": "string", "target": "epicAction"},
    "DoubleSided": {"type": "bool", "target": "doubleSided"},
    "BackArt": {"type": "string", "target": "images.back"},
    "BackText": {"type": "string", "target": "backText"},
    "Rarity": {"type": "string", "target": "rarity"},
    "Unique": {"type": "bool", "target": "unique"},
    "Artist": {"type": "string", "target": "artist"},
    "VariantType": {"type": "string", "target": "variants.type"},
    "MarketPrice": {"type": "float|string", "target": "variants.marketPrice"},
    "LowPrice": {"type": "float|string", "target": "variants.lowPrice"},
    "FrontArt": {"type": "string", "target": "images.front"}
}

mtg_schema = {
    "id": {"type": "string", "target": "id"},
    "name": {"type": "string", "target": "name"},
    "manaCost": {"type": "string", "target": "manaCost"},
    "cmc": {"type": "float", "target": "cmc"},
    "colors": {"type": "list[string]", "target": "colors"},
    "colorIdentity": {"type": "list[string]", "target": "colorIdentity"},
    "type": {"type": "string", "target": "type"},
    "types": {"type": "list[string]", "target": "types"},
    "subtypes": {"type": "list[string]", "target": "subtypes"},
    "rarity": {"type": "string", "target": "rarity"},
    "set": {"type": "string", "target": "set.set_code"},
    "setName": {"type": "string", "target": "set.name"},
    "text": {"type": "string", "target": "effect"},
    "artist": {"type": "string", "target": "artist"},
    "number": {"type": "string", "target": "number"},
    "power": {"type": "string|int", "target": "power"},
    "toughness": {"type": "string|int", "target": "toughness"},
    "layout": {"type": "string", "target": "layout"},
    "multiverseid": {"type": "string|int", "target": "multiverseid"}, 
    "imageUrl": {"type": "string", "target": "images.small"},
    "variations": {"type": "list[string]", "target": "variations"},  # TODO: detalhar como armazenar variantes
    "foreignNames": {"type": "list[dict]", "target": "foreignNames"},  # TODO: decidir se vira variants por idioma
    "printings": {"type": "list[string]", "target": "printings"},  # TODO: decidir se vira array de sets
    "originalText": {"type": "string", "target": "originalText"},
    "originalType": {"type": "string", "target": "originalType"},
    "legalities": {"type": "list[dict]", "target": "legalities"},
}

def forced_layout_flat_fixed(mapa: dict, card: dict) -> dict:
    out = {}
    images, set_obj, variants = {}, {}, {}
    for campo, info in mapa.items():
        target = info.get("target", "")
        val = card.get(campo)
        if target.startswith("images.") and val is not None:
            key = target.split(".", 1)[1]
            images[key] = val
        elif target.startswith("set.") and val is not None:
            set_obj[target.split(".", 1)[1]] = val
        elif target.startswith("variants.") and val is not None:
            variants[target.split(".", 1)[1]] = val
        elif val is not None:
            out[target] = val
    # --- ajuste: front → small e large ---
    if "front" in images:
        images["small"] = images["front"]
        images["large"] = images["front"]
    if images:
        out["images"] = images
    if set_obj:
        out["set"] = set_obj
    if variants:
        out["variants"] = [variants]
    # gerar id/code -- so precisa no star wars
    if "doubleSided" in out:
        if "set" in out and "set_code" in out["set"] and "number" in out:
            out["id"] = f"{out['set']['set_code']}-{out['number']}"
            out["code"] = out["id"]
    return out

def format_yugioh_card(card):
    formatted = {
        "_id": str(card.get("_id")),  # Mongo ID
        "id": str(card.get("id")),    # ID da carta (Yugioh)
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
        "images": {
            "small": None,
            "large": None
        },
        "variants": []
    }

    # imagens
    images = card.get("card_images", [])
    if images and isinstance(images, list):
        img = images[0]  # primeira imagem
        formatted["images"]["small"] = img.get("image_url_small")
        formatted["images"]["large"] = img.get("image_url")

    # variantes baseadas em card_sets
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

    return formatted

def format_fab_card(card):
    formatted = {
        "_id": str(card.get("_id")),
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

    return formatted

@app.route("/")
def root():
    base = request.host_url.rstrip("/")
    return jsonify([
        {"name": "SWU - Buscar carta única ou set", "url": f"{base}/swu/cards?set=sor&number=010"},
        {"name": "SWU - Listar cartas de um set", "url": f"{base}/swu/cards?set=sor"},
        {"name": "FAB - Listar todas as cartas", "url": f"{base}/fab/cards"},
        {"name": "MTG - Listar todas as cartas", "url": f"{base}/mtg/cards"},
        {"name": "YUG - Buscar cartas por nome", "url": f"{base}/yugi/cards?name=blue"},
    ])

@app.route("/swu/cards")
def get_swu_cards():
    # pega parâmetros da query em minúsculo
    Set = request.args.get("set")  # note: 'set' minúsculo
    Number = request.args.get("number")  # 'number' minúsculo

    if not Set:
        return jsonify({"error": "Informe Set"}), 400

    Set = Set.lower()
    if Number:
        Number = Number.lower()
        url = f"https://api.swu-db.com/cards/{Set}/{Number}"
    else:
        url = f"https://api.swu-db.com/cards/{Set}"

    try:
        r = requests.get(url, params={"format": "json", "pretty": "true"}, timeout=10)
        r.raise_for_status()
        resp_json = r.json()
        if isinstance(resp_json, dict) and "data" in resp_json:
            cards = resp_json["data"]
        elif isinstance(resp_json, list):
            cards = resp_json
        else:
            cards = [resp_json]
    except requests.HTTPError as e:
        return jsonify({"error": "Falha ao consultar SWU", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Erro desconhecido", "details": str(e)}), 500

    page_data = [forced_layout_flat_fixed(swu_schema, c) for c in cards]

    return jsonify({
        "total": len(cards),
        "data": page_data
    })

@app.route("/fab/cards")
def get_fab_cards():
    query = {}
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("set_id"):
        query["printings.set_id"] = request.args["set_id"]

    limit = min(int(request.args.get("limit", 25)), 100)
    page = max(int(request.args.get("page", 1)), 1)

    total = fab_collection.count_documents(query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1

    cursor = fab_collection.find(query).skip((page - 1) * limit).limit(limit)
    data = [format_fab_card(doc) for doc in cursor]

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/yugi/cards")
def get_yugi_cards():
    query = {}
    # filtros simples
    if request.args.get("id"):
        query["id"] = int(request.args["id"])
    if request.args.get("konami_id"):
        query["konami_id"] = int(request.args["konami_id"])
    if request.args.get("md_rarity"):
        query["md_rarity"] = request.args["md_rarity"]
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    # filtros dentro de card_sets[]
    if request.args.get("set_code"):
        query["card_sets.set_code"] = request.args["set_code"]
    if request.args.get("rarity"):
        query["card_sets.set_rarity"] = request.args["rarity"]
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    total = yugi_collection.count_documents(query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    # query no Mongo
    cursor = (
        yugi_collection.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = []
    for doc in cursor:
        data.append(format_yugioh_card(doc))
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/mtg/cards")
def get_mtg_cards():
    base_url = "https://api.magicthegathering.io/v1/cards"

    # parâmetros da query (todos suportados pela API)
    params = {}
    allowed_filters = [
        "name", "set", "colors", "colorIdentity", "type", "supertypes",
        "types", "subtypes", "rarity", "layout", "cmc", "loyalty",
        "gameFormat", "legality", "contains", "id", "language", "orderBy", "random"
    ]
    for f in allowed_filters:
        val = request.args.get(f)
        if val:
            params[f] = val

    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1

    params["pageSize"] = limit
    params["page"] = page
    params["contains"] = "imageUrl"

    try:
        r = requests.get(base_url, params=params, timeout=10)
        r.raise_for_status()
        resp_json = r.json()
        cards = resp_json.get("cards", [])
        total = int(r.headers.get("Total-Count", len(cards)))
    except requests.HTTPError as e:
        return jsonify({"error": "Falha ao consultar MTG", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Erro desconhecido", "details": str(e)}), 500

    # aplicar schema
    data = [forced_layout_flat_fixed(mtg_schema, c) for c in cards]
    total_pages = math.ceil(total / limit) if limit > 0 else 1

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.after_request
def add_cache_headers(resp):
    resp.headers["Cache-Control"] = "s-maxage=300, stale-while-revalidate=600"
    return resp

if __name__ == "__main__":
    app.run(port=5003, debug=True)
