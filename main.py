from fastapi import FastAPI, HTTPException, Query
import httpx
import random
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
POKEAPI_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"
POKEAPI_MOVE_URL = "https://pokeapi.co/api/v2/move/"
POKEAPI_ABILITY_URL = "https://pokeapi.co/api/v2/ability/"


async def fetch_evolution_chain(client, url):
    try:
        res = await client.get(url)
        if res.status_code != 200:
            return None
        data = res.json()

        def parse_chain(chain):
            if not chain:
                return None
            return {
                "name": chain['species']['name'],
                "evolves_to": [parse_chain(evo) for evo in chain.get('evolves_to', [])]
            }
        return parse_chain(data.get('chain'))
    except Exception:
        return None


async def get_move_details(client, move_name):
    try:
        resp = await client.get(f"{POKEAPI_MOVE_URL}{move_name}")
        if resp.status_code != 200:
            return {"name": move_name, "effect": "unknown", "power": 40, "type": "normal"}
        move_data = resp.json()
        effect_entries = move_data.get("effect_entries", [])
        effect = next((entry["effect"] for entry in effect_entries if entry["language"]["name"] == "en"),
                      "No effect description available")
        return {
            "name": move_data["name"],
            "type": move_data["type"]["name"],
            "power": move_data.get("power"),
            "accuracy": move_data.get("accuracy"),
            "pp": move_data.get("pp"),
            "effect": effect
        }
    except Exception:
        return {"name": move_name, "effect": "unknown", "power": 40, "type": "normal"}


async def get_ability_details(client, ability_name):
    try:
        resp = await client.get(f"{POKEAPI_ABILITY_URL}{ability_name}")
        if resp.status_code != 200:
            return {"name": ability_name, "description": "unknown"}
        ability_data = resp.json()
        desc_entries = ability_data.get("effect_entries", [])
        description = next((entry["effect"] for entry in desc_entries if entry["language"]["name"] == "en"),
                          "No description available")
        return {"name": ability_data["name"], "description": description}
    except Exception:
        return {"name": ability_name, "description": "unknown"}


async def fetch_full_pokemon_data(name: str, client):
    resp = await client.get(f"{POKEAPI_BASE_URL}{name.lower()}")
    if resp.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Pokémon '{name}' not found.")
    data = resp.json()

    evolution_chain = None
    if species_url := data.get("species", {}).get("url"):
        species_resp = await client.get(species_url)
        if species_resp.status_code == 200:
            species_data = species_resp.json()
            if evo_chain_url := species_data.get('evolution_chain', {}).get('url'):
                evolution_chain = await fetch_evolution_chain(client, evo_chain_url)

    moves = []
    for mv in data.get("moves", [])[:4]:
        mv_detail = await get_move_details(client, mv.get("move", {}).get("name"))
        moves.append(mv_detail)

    abilities = []
    for ab in data.get("abilities", []):
        ab_detail = await get_ability_details(client, ab.get("ability", {}).get("name"))
        abilities.append(ab_detail)

    result = {
        "name": data.get("name"),
        "id": data.get("id"),
        "sprite": data.get("sprites", {}).get("front_default"),
        "types": [t.get("type", {}).get("name") for t in data.get("types", [])],
        "stats": {s.get("stat", {}).get("name"): s.get("base_stat") for s in data.get("stats", [])},
        "abilities": abilities,
        "moves": moves,
        "evolution_chain": evolution_chain
    }
    return result


@app.get("/")
def root():
    return {"message": "Pokémon Data Resource is running. Use /pokemon/{name} & /battle/simulate."}


@app.get("/pokemon/{name}")
async def get_pokemon(name: str):
    async with httpx.AsyncClient() as client:
        return await fetch_full_pokemon_data(name, client)


TYPE_EFFECTIVENESS = {
    'normal': {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
    'fire': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 2, 'bug': 2, 'rock': 0.5, 'dragon': 0.5, 'steel': 2},
    'water': {'fire': 2, 'water': 0.5, 'grass': 0.5, 'ground': 2, 'rock': 2, 'dragon': 0.5},
    'grass': {'fire': 0.5, 'water': 2, 'grass': 0.5, 'poison': 0.5, 'ground': 2, 'flying': 0.5, 'bug': 0.5, 'rock': 2, 'dragon': 0.5, 'steel': 0.5},
    'electric': {'water': 2, 'electric': 0.5, 'grass': 0.5, 'ground': 0, 'flying': 2, 'dragon': 0.5},
    'psychic': {'psychic': 0.5, 'dark': 0, 'steel': 0.5},
    'ice': {'fire': 0.5, 'water': 0.5, 'ice': 0.5, 'steel': 0.5},
    'dragon': {'dragon': 2, 'steel': 0.5, 'fairy': 0},
}


def get_type_multiplier(move_type: str, defender_types: list) -> float:
    mult = 1.0
    if move_type:
        for t in defender_types:
            mult *= TYPE_EFFECTIVENESS.get(move_type, {}).get(t, 1)
    return mult


def calculate_damage(attacker, defender, move):
    LEVEL = 50
    POWER = move.get("power") or 40
    MOVE_TYPE = move.get("type", "normal")
    ATTACK = attacker.get("stats", {}).get("attack", 50)
    DEFENSE = defender.get("stats", {}).get("defense", 50)
    
    SPECIAL_TYPES = ["special-attack", "special-defense"]
    if move.get("type") in ["fire", "water", "grass", "ice", "electric", "psychic", "dragon"]:
        ATTACK = attacker.get("stats", {}).get("special-attack", ATTACK)
        DEFENSE = defender.get("stats", {}).get("special-defense", DEFENSE)

    type_mult = get_type_multiplier(MOVE_TYPE, defender.get("types", []))
    stab = 1.5 if MOVE_TYPE in attacker.get("types", []) else 1.0
    rand = random.uniform(0.85, 1.0)
    
    if DEFENSE == 0: DEFENSE = 1

    base = (((2 * LEVEL / 5 + 2) * POWER * ATTACK / DEFENSE) / 50) + 2
    return max(1, int(base * type_mult * stab * rand))


def choose_move(pokemon):
    moves = [m for m in pokemon.get("moves", []) if m.get("power")]
    return random.choice(moves) if moves else {"name": "tackle", "type": "normal", "power": 40}


@app.get("/battle/simulate")
async def simulate_battle(pokemon1: str = Query(...), pokemon2: str = Query(...)):
    async with httpx.AsyncClient() as client:
        p1 = await fetch_full_pokemon_data(pokemon1, client)
        p2 = await fetch_full_pokemon_data(pokemon2, client)

    p1["current_hp"] = p1.get("stats", {}).get("hp", 100)
    p2["current_hp"] = p2.get("stats", {}).get("hp", 100)

    structured_log = []
    
    first, second = (p1, p2) if p1.get("stats", {}).get("speed", 0) >= p2.get("stats", {}).get("speed", 0) else (p2, p1)
    
    turn_count = 0
    while p1["current_hp"] > 0 and p2["current_hp"] > 0 and turn_count < 100:
        
        for attacker, defender in [(first, second), (second, first)]:
            if attacker["current_hp"] <= 0 or defender["current_hp"] <= 0:
                break

            move = choose_move(attacker)
            dmg = calculate_damage(attacker, defender, move)
            defender["current_hp"] = max(0, defender["current_hp"] - dmg)

            structured_log.append({
                "action": "attack",
                "attacker": { "name": attacker["name"] },
                "defender": { "name": defender["name"], "hp_left": defender["current_hp"] },
                "move": move["name"],
                "damage": dmg,
                "text": f"{attacker['name'].capitalize()} used {move['name'].capitalize()} dealing {dmg} damage!"
            })
            
            if defender["current_hp"] == 0:
                structured_log.append({
                    "action": "faint",
                    "pokemon": { "name": defender["name"] },
                    "text": f"{defender['name'].capitalize()} fainted!"
                })
                break
        
        turn_count += 1

    winner = "Draw"
    if p1["current_hp"] > 0 and p2["current_hp"] == 0:
        winner = p1["name"].capitalize()
    elif p2["current_hp"] > 0 and p1["current_hp"] == 0:
        winner = p2["name"].capitalize()

    structured_log.append({"action": "end", "text": f"Battle Over. Winner: {winner}"})
    
    return {"battle_log": structured_log}