from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests, math
from api.utils.cinderfall import fetch_mtg_cards
from api.utils.mango2 import contar_docs, buscar_docs, random_doc, buscar_por_id
from api.utils.gfilters import (
    apply_sorcery_filters,
    apply_onepiece_filters,
    apply_riftbound_filters,
    apply_fab_filters,
    apply_yugioh_filters,
    apply_swu_filters,
    apply_unionarena_filters,
    apply_gundam_filters
)

app = Flask(__name__)
CORS(app)

API_KEY = "94fbfb20cb57a0c1c5e460b84503ae129fe0a8808d6c347a5bb7efa32c7eae56"

GAME_SRC = {
    "apitcg":["digimon","pokemon","dragon-ball-fusion"],
    "mahou":["sorcery","one-piece","riftbound","star-wars","fab","yugioh","magic","gundam","union-arena"]
}

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
    "star-wars": {
        "collection": "star-wars",
        "filter_fn": apply_swu_filters
    },
}

def has_game(game: str) -> bool:
    return any(game in games for games in GAME_SRC.values())

def has_game_mahou(game: str) -> bool:
    return game in GAME_SRC["mahou"]

def paginated_response(data, page, limit, total):
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": math.ceil(total / limit),
        "data": data
    })

def get_mtg_cards():
    try:
        limit = request.args.get("limit", 25)
        page = request.args.get("page", 1)

        filters = {
            "name": request.args.get("name"),
            "set": request.args.get("set"),
            "colors": request.args.get("colors"),
            "rarity": request.args.get("rarity"),
            "layout": request.args.get("layout"),
            "cmc": request.args.get("cmc"),
            "language": request.args.get("language"),
            "id": request.args.get("id"),
        }

        result = fetch_mtg_cards(limit=limit, page=page, **filters)
        return jsonify(result)

    except requests.HTTPError as e:
        return jsonify({"error": "Falha ao consultar Scryfall", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Erro desconhecido", "details": str(e)}), 500

def get_apitcg_cards(game):
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
    if not has_game(game):
        return jsonify({"error": "Jogo não encontrado"}), 404
    if not has_game_mahou(game):
        return get_apitcg_cards(game)
    if game == "magic":
        return get_mtg_cards()
    config = GAME_CONFIG[game]
    collection = config["collection"]
    filter_fn = config["filter_fn"]
    query = filter_fn(request.args)
    try:
        limit = int(request.args.get("limit", 25))
        page = int(request.args.get("page", 1))
    except ValueError:
        return jsonify({"error": "page e limit devem ser números"}), 400
    total = contar_docs(collection, query)
    data = buscar_docs(collection, query, page, limit)
    return paginated_response(data, page, limit, total)

@app.route("/api/<game>/cards/bulk", methods=["POST"])
def get_cards_bulk(game):
    if not has_game_mahou(game):
        return jsonify({"error": "Jogo não habilitado"}), 404
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
    if not has_game(game):
        return jsonify({"error": "Jogo não encontrado"}), 404
    if not has_game_mahou(game):
        return get_apitcg_cards(game)
    if game == "magic":
        return get_mtg_cards()
    config = GAME_CONFIG[game]
    collection = config["collection"]
    card = buscar_por_id(collection, card_id)
    if not card:
        return jsonify({"error": "Card não encontrado"}), 404
    return jsonify({
        "data": card
    })

@app.route("/api/<game>/cards/random")
def get_random_card(game):
    if not has_game_mahou(game):
        return jsonify({"error": "Jogo não habilitado"}), 404
    config = GAME_CONFIG[game]
    collection = config["collection"]
    data = random_doc(collection)
    return jsonify({
        "data": data
    })

@app.after_request
def add_cache_headers(resp):
    resp.headers["Cache-Control"] = "s-maxage=300, stale-while-revalidate=600"
    return resp

if __name__ == "__main__":
    app.run(port=5003, debug=True)
