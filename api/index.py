# api_swu_single.py

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from math import ceil

app = Flask(__name__)
CORS(app)

# --- Schema SWU ---
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

    # gerar id/code
    if "set" in out and "set_code" in out["set"] and "number" in out:
        out["id"] = f"{out['set']['set_code']}-{out['number']}"
        out["code"] = out["id"]

    return out


# ---------------- ROTAS ----------------
@app.route("/")
def root():
    base = request.host_url.rstrip("/")
    return jsonify([
        {"name": "SWU - Buscar carta única", "url": f"{base}/swu/cards?Set=SOR&Number=010"}
    ])

@app.route("/swu/cards")
def swu_cards():
    Set = request.args.get("Set")
    Number = request.args.get("Number")

    # construir URL dinâmica
    if Set and Number:
        url = f"https://api.swu-db.com/cards/{Set}/{Number}"
    elif Set and not Number:
        url = f"https://api.swu-db.com/cards/{Set}"
    else:
        url = "https://api.swu-db.com/cards"

    try:
        r = requests.get(url, params={"format": "json", "pretty": "true"}, timeout=10)
        r.raise_for_status()
        cards = r.json()
    except requests.HTTPError as e:
        return jsonify({"error": "Falha ao consultar SWU", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Erro desconhecido", "details": str(e)}), 500

    # se retornar um dict único, transformar em lista
    if isinstance(cards, dict):
        cards = [cards]

    page_data = [forced_layout_flat_fixed(swu_schema, c) for c in cards]

    return jsonify({
        "total": len(cards),
        "data": page_data
    })

@app.after_request
def add_cache_headers(resp):
    resp.headers["Cache-Control"] = "s-maxage=300, stale-while-revalidate=600"
    return resp

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(port=5003, debug=True)
