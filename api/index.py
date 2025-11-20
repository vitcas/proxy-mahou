from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import math
from api.utils.mango2 import contar_docs, buscar_docs, random_doc

app = Flask(__name__)
CORS(app)

@app.route("/")
def root():
    return render_template("home.html")

# dados do mongo
@app.route("/sorcery/cards")
def get_sorcery_cards():
    query = {}
    # filtros
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("type"):
        query["type"] = {"$regex": request.args["type"], "$options": "i"}
    if request.args.get("element"):
        query["elements"] = {"$regex": request.args["element"], "$options": "i"}
    if request.args.get("rarity"):
        query["rarity"] = request.args["rarity"]
    if request.args.get("set"):
        query["set.name"] = {"$regex": request.args["set"], "$options": "i"} 
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    total = contar_docs("sorcery", query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    data = buscar_docs("sorcery",query, page, limit)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/sorcery/cards/random")
def get_sorcery_random():
    data = random_doc("sorcery")
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

@app.route("/one-piece/cards")
def get_onepiece_cards():
    query = {}
    # filtros
    if request.args.get("id"):
        query["id"] = {"$regex": request.args["id"], "$options": "i"}
    if request.args.get("code"):
        query["code"] = {"$regex": request.args["code"], "$options": "i"}
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("rarity"):
        query["rarity"] = request.args["rarity"]
    if request.args.get("type"):
        query["type"] = {"$regex": request.args["type"], "$options": "i"}
    if request.args.get("color"):
        query["color"] = request.args["color"]
    if request.args.get("cost"):
        query["cost"] = request.args["cost"]
    if request.args.get("power"):
        query["power"] = request.args["power"]
    if request.args.get("family"):
        query["family"] = {"$regex": request.args["family"], "$options": "i"}
    if request.args.get("set"):
        query["set.set_code"] = request.args["set"] 
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    total = contar_docs("one-piece", query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    data = buscar_docs("one-piece",query, page, limit)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/one-piece/cards/random")
def get_onepiece_random():
    data = random_doc("one-piece")
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

@app.route("/riftbound/cards")
def get_riftbound_cards():
    query = {}
    # filtros
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("rarity"):
        query["rarity"] = request.args["rarity"]
    if request.args.get("might"):
        query["might"] = request.args["might"]
    if request.args.get("energyCost"):
        query["energyCost"] = request.args["energyCost"]
    if request.args.get("powerCost"):
        query["powerCost"] = request.args["powerCost"]
    if request.args.get("cardType"):
        query["cardType"] = {"$regex": request.args["cardType"], "$options": "i"}
    if request.args.get("domain"):
        query["domain"] = {"$regex": request.args["domain"], "$options": "i"}
    if request.args.get("set"):
        query["set.name"] = {"$regex": request.args["set"], "$options": "i"}   
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    total = contar_docs("riftbound", query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    data = buscar_docs("riftbound",query, page, limit)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/riftbound/cards/random")
def get_riftbound_random():
    data = random_doc("riftbound")
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

@app.route("/fab/cards")
def get_fab_cards():
    query = {}
    # filtros
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("set"):
        query["printings.set_id"] = request.args["set"]
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    total = contar_docs("fab", query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    data = buscar_docs("fab",query, page, limit)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/fab/cards/random")
def get_fab_random():
    data = random_doc("fab")
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

@app.route("/yugioh/cards")
def get_yugi_cards():
    # filtros parametros
    query = {}
    if request.args.get("id"):
        query["id"] = int(request.args["id"])
    if request.args.get("konami_id"):
        query["konami_id"] = int(request.args["konami_id"])
    if request.args.get("effect"):
        query["desc"] = {"$regex": request.args["effect"], "$options": "i"}
    if request.args.get("name"):
        query["name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("attribute"):
        query["attribute"] = {"$regex": request.args["attribute"], "$options": "i"}
    if request.args.get("type"):
        query["type"] = {"$regex": request.args["type"], "$options": "i"}
    if request.args.get("frameType"):
        query["frameType"] = {"$regex": request.args["frameType"], "$options": "i"}
    # filtros dentro de card_sets[]
    if request.args.get("set"):
        query["card_sets.set_code"] = {"$regex": request.args["set"], "$options": "i"}
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
    total = contar_docs("yugioh", query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    data = buscar_docs("yugioh",query, page, limit)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/yugioh/cards/random")
def get_yugi_random():
    data = random_doc("yugioh")
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

@app.route("/swu/cards")
def get_swu_cards():
    query = {}
    # filtros
    if request.args.get("name"):
        query["Name"] = {"$regex": request.args["name"], "$options": "i"}
    if request.args.get("set"):
        query["Set"] = {"$regex": request.args["set"], "$options": "i"}
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    total = contar_docs("star-wars", query)
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    data = buscar_docs("star-wars",query, page, limit)
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/swu/cards/random")
def get_swu_random():
    data = random_doc("star-wars")
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

# api externa
@app.route("/old-swu/cards")
def get_swu_cards_old():
    #parâmetros
    swuset = request.args.get("set")  
    swunumber = request.args.get("number")
    if not swuset:
        return jsonify({"error": "Informe o set"}), 400
    swuset = swuset.lower()
    if swunumber:
        swunumber = swunumber.lower()
        url = f"https://api.swu-db.com/cards/{swuset}/{swunumber}"
    else:
        url = f"https://api.swu-db.com/cards/{swuset}"
    # paginação
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
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

    page_data = []
    for card in cards:
        images = {
            "front": card.get("FrontArt"),
            "back": card.get("BackArt"),
        }
        if images["front"]:
            images["small"] = images["large"] = images["front"]
        images = {k: v for k, v in images.items() if v is not None}

        set_obj = {"set_code": card.get("Set")}
        variants = {
            "type": card.get("VariantType"),
            "marketPrice": card.get("MarketPrice"),
            "lowPrice": card.get("LowPrice"),
        }
        variants = {k: v for k, v in variants.items() if v is not None}

        out = {
            "number": card.get("Number"),
            "name": card.get("Name"),
            "subtitle": card.get("Subtitle"),
            "type": card.get("Type"),
            "aspects": card.get("Aspects"),
            "traits": card.get("Traits"),
            "arenas": card.get("Arenas"),
            "cost": card.get("Cost"),
            "power": card.get("Power"),
            "hp": card.get("HP"),
            "frontText": card.get("FrontText"),
            "epicAction": card.get("EpicAction"),
            "doubleSided": card.get("DoubleSided"),
            "backText": card.get("BackText"),
            "rarity": card.get("Rarity"),
            "unique": card.get("Unique"),
            "artist": card.get("Artist"),
        }

        if images:
            out["images"] = images
        if set_obj.get("set_code"):
            out["set"] = set_obj
        if variants:
            out["variants"] = [variants]

        if out.get("doubleSided") and out.get("set") and out["set"].get("set_code") and out.get("number"):
            out["id"] = out["code"] = f"{out['set']['set_code']}-{out['number']}"

        page_data.append({k: v for k, v in out.items() if v is not None})

    total = len(cards)
    total_pages = max((total + limit - 1) // limit, 1)

    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": page_data
    })

@app.route("/old-mtg/cards")
def get_mtg_cards_old():
    base_url = "https://api.magicthegathering.io/v1/cards"
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
    data = []
    for c in cards:
        images = {"small": c.get("imageUrl")}
        images = {k: v for k, v in images.items() if v}
        set_obj = {"set_code": c.get("set"), "name": c.get("setName")}
        set_obj = {k: v for k, v in set_obj.items() if v}
        out = {
            "id": c.get("id"),
            "name": c.get("name"),
            "manaCost": c.get("manaCost"),
            "cmc": c.get("cmc"),
            "colors": c.get("colors"),
            "colorIdentity": c.get("colorIdentity"),
            "type": c.get("type"),
            "types": c.get("types"),
            "subtypes": c.get("subtypes"),
            "rarity": c.get("rarity"),
            "effect": c.get("text"),
            "artist": c.get("artist"),
            "number": c.get("number"),
            "power": c.get("power"),
            "toughness": c.get("toughness"),
            "layout": c.get("layout"),
            "multiverseid": c.get("multiverseid"),
            "variations": c.get("variations"),
            "foreignNames": c.get("foreignNames"),
            "printings": c.get("printings"),
            "originalText": c.get("originalText"),
            "originalType": c.get("originalType"),
            "legalities": c.get("legalities"),
        }
        if images:
            out["images"] = images
        if set_obj:
            out["set"] = set_obj
        data.append({k: v for k, v in out.items() if v is not None})
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "data": data
    })

@app.route("/mtg/cards")
def get_mtg_cards():
    # Parâmetros básicos
    try:
        limit = min(int(request.args.get("limit", 25)), 100)
    except ValueError:
        limit = 25
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1

    # Scryfall pagina por ?page=
    # e permite limitar resultados por q= com filtros textuais
    q_parts = []

    # Convertendo filtros antigos para Scryfall (quando possível)
    mapping = {
        "name": "name:",
        "set": "set:",
        "colors": "color:",
        "rarity": "rarity:",
        "layout": "layout:",
        "cmc": "cmc:",
        "language": "lang:",
        "id": "scryfallid:",
    }

    for old_key, prefix in mapping.items():
        val = request.args.get(old_key)
        if val:
            q_parts.append(f'{prefix}"{val}"')

    # Se nada for passado, buscamos tudo
    q = " ".join(q_parts) if q_parts else "*"

    url = "https://api.scryfall.com/cards/search"
    params = {
        "q": q,
        "page": page,
        "unique": "cards",
        "order": "name"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        resp_json = r.json()
        cards = resp_json.get("data", [])
        total = resp_json.get("total_cards", len(cards))
    except requests.HTTPError as e:
        return jsonify({"error": "Falha ao consultar Scryfall", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Erro desconhecido", "details": str(e)}), 500

    data = []

    for c in cards:
        # imagens
        images = c.get("image_uris") or (
            (c.get("card_faces")[0].get("image_uris") if c.get("card_faces") else None)
        )
        if images:
            images = {
                "small": images.get("small"),
                "normal": images.get("normal"),
                "large": images.get("large"),
            }
            images = {k: v for k, v in images.items() if v}

        # set info
        set_obj = {
            "set_code": c.get("set"),
            "name": c.get("set_name"),
        }
        set_obj = {k: v for k, v in set_obj.items() if v}

        # typeline mantido
        typeline = c.get("type_line")

        # multiverseid compatível
        multiverse_id = (c.get("multiverse_ids") or [None])[0]

        out = {
            "id": c.get("id"),
            "name": c.get("name"),
            "manaCost": c.get("mana_cost"),
            "cmc": c.get("cmc"),
            "colors": c.get("colors"),
            "colorIdentity": c.get("color_identity"),
            "typeline": typeline,                     # <<< mantém o campo original
            "rarity": c.get("rarity"),
            "effect": c.get("oracle_text"),
            "artist": c.get("artist"),
            "number": c.get("collector_number"),
            "power": c.get("power"),
            "toughness": c.get("toughness"),
            "layout": c.get("layout"),
            "multiverseid": multiverse_id,
            "printings": c.get("prints_search_uri"),
            "legalities": c.get("legalities"),
        }

        if images:
            out["images"] = images
        if set_obj:
            out["set"] = set_obj

        # remover None
        data.append({k: v for k, v in out.items() if v is not None})

    # Scryfall não dá total exato por página, mas usamos total_cards
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
