from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests, math
from api.utils.mango2 import contar_docs, buscar_docs, random_doc, buscar_por_id
from api.utils.gfilters import (
    apply_sorcery_filters,
    apply_onepiece_filters,
    apply_riftbound_filters,
    apply_fab_filters,
    apply_yugioh_filters,
    apply_swu_filters,
)

app = Flask(__name__)
CORS(app)

API_KEY = "94fbfb20cb57a0c1c5e460b84503ae129fe0a8808d6c347a5bb7efa32c7eae56"

GAME_CONFIG = {
    "sorcery": {
        "collection": "sorcery",
        "filter_fn": apply_sorcery_filters
    },
    "one-piece": {
        "collection": "one-piece",
        "filter_fn": apply_onepiece_filters
    },
    "riftbound": {
        "collection": "riftbound",
        "filter_fn": apply_riftbound_filters
    },
    "fab": {
        "collection": "fab",
        "filter_fn": apply_fab_filters
    },
    "yugioh": {
        "collection": "yugioh",
        "filter_fn": apply_yugioh_filters
    },
    "swu": {
        "collection": "star-wars",
        "filter_fn": apply_swu_filters
    },
}

def paginated_response(data, page, limit, total):
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": math.ceil(total / limit),
        "data": data
    })

def random_response(collection: str):
    data = random_doc(collection)
    return jsonify({
        "page": 1,
        "limit": 1,
        "total": 1,
        "totalPages": 1,
        "data": data
    })

def get_cards_ext(game):
    url = f"https://apitcg.com/api/{game}/cards"
    params = {k: v for k, v in request.args.items() if k != "game"}
    try:
        r = requests.get(url, headers={"x-api-key": API_KEY}, params=params, timeout=10)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    try:
        r.raise_for_status()
        return jsonify(r.json())
    except Exception:
        return jsonify({"error": r.text[:500]}), 502

@app.route("/")
def root():
    return render_template("home.html")

@app.route("/api/<game>/cards")
def get_cards(game):
    if game not in GAME_CONFIG:
        aux = get_cards_ext(game)
        return aux
    config = GAME_CONFIG[game]
    collection = config["collection"]
    filter_fn = config["filter_fn"]
    query = filter_fn(request.args)
    try:
        limit = int(request.args.get("limit", 20))
        page = int(request.args.get("page", 1))
    except ValueError:
        return jsonify({"error": "page e limit devem ser números"}), 400
    skip = (page - 1) * limit
    total = contar_docs(collection, query)
    data = buscar_docs(collection, query, page, limit)
    return paginated_response(data, page, limit, total)

@app.route("/api/<game>/cards/bulk", methods=["POST"])
def get_cards_bulk(game):
    if game not in GAME_CONFIG:
        return jsonify({"error": "Jogo não encontrado"}), 404

    # corpo deve conter: { "ids": ["x", "y", "z"] }
    body = request.get_json(silent=True)
    if not body or "ids" not in body or not isinstance(body["ids"], list):
        return jsonify({"error": "Envie um JSON com uma lista 'ids'"}), 400

    config = GAME_CONFIG[game]
    collection = config["collection"]

    result = []
    for cid in body["ids"]:
        card = buscar_por_id(collection, cid)
        if card:
            result.append(card)

    return jsonify({
        "count": len(result),
        "data": result
    })

@app.route("/api/<game>/cards/<card_id>")
def get_card_by_id(game, card_id):
    if game not in GAME_CONFIG:
        return jsonify({"error": "Jogo não encontrado"}), 404
    config = GAME_CONFIG[game]
    collection = config["collection"]
    card = buscar_por_id(collection, card_id)
    if not card:
        return jsonify({"error": "Card não encontrado"}), 404
    return jsonify(card)

@app.route("/api/<game>/cards/random")
def get_random_card(game):
    if game not in GAME_CONFIG:
        return jsonify({"error": "Jogo não encontrado"}), 404
    config = GAME_CONFIG[game]
    collection = config["collection"]
    return random_response(collection)

@app.route("/api/mtg/cards")
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
