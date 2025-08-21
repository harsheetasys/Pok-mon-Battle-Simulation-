# Pokémon Battle Simulation MCP Server

A full-stack web application that provides detailed Pokémon data and simulates turn-based battles between any two Pokémon. Built with a FastAPI backend and an interactive frontend featuring animations and sound effects.

## ✨ Features

- **Comprehensive Pokémon Data**: Fetches and displays detailed information about any Pokémon including stats, types, abilities, and moves
- **Battle Simulation Engine**: Implements authentic Pokémon battle mechanics with type effectiveness, STAB, and damage calculation
- **Animated Battle Interface**: Visual battle sequence with attack animations, HP bars, and victory celebrations
- **Interactive Web UI**: Responsive design with dropdown selectors, battle logs, and control buttons
- **Sound Effects**: Attack and faint sounds for immersive gameplay
- **RESTful API**: Clean endpoints for both Pokémon data and battle simulation

## 🏗️ Project Architecture

```
pokemon-battle-sim/
├── main.py          # FastAPI backend server
├── index.html       # Frontend HTML structure
├── app.js           # Frontend JavaScript logic
├── README.md        # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Modern web browser with JavaScript enabled

### Installation & Setup

1. **Clone or download the project files** to a local directory

2. **Create and activate a virtual environment** (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install Python dependencies**:

```bash
pip install fastapi uvicorn httpx
```

4. **Start the backend server**:

```bash
uvicorn main:app --reload
```

The API server will start at `http://127.0.0.1:8000`

5. **Open the frontend**:
   - Navigate to the project directory
   - Double-click `index.html` to open it in your default browser
   - Or serve it through a local HTTP server

## 🎮 How to Use the Application

### Selecting Pokémon

1. Use the dropdown menus to select two Pokémon from the available options
2. Their information will automatically load and display in the info cards

### Simulating a Battle

1. Click the **"Simulate Battle"** button to run the battle simulation on the server
2. The battle log will show "Simulating battle..." while processing

### Watching the Battle

1. After simulation completes, click the **"Auto Play"** button
2. Watch the animated battle unfold in the battle stage area
3. Follow the action in the battle log text area

### Resetting

1. Click **"Reset"** to clear the current battle and select new Pokémon
2. Changing either Pokémon selection will also reset the battle

## 🔧 API Reference

### Base URL
All endpoints are served from `http://127.0.0.1:8000`

### Endpoints

#### Get Pokémon Data
```
GET /pokemon/{name}
```
Fetches comprehensive data for a specific Pokémon.

**Parameters:**
- `name` (string, required): The name of the Pokémon (e.g., "pikachu")

**Example Response:**
```json
{
  "name": "pikachu",
  "id": 25,
  "sprite": "https://raw.githubusercontent.com/.../25.png",
  "types": ["electric"],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special-attack": 50,
    "special-defense": 50,
    "speed": 90
  },
  "abilities": [
    {
      "name": "static",
      "description": "Has a 30% chance of paralyzing attacking Pokémon on contact."
    }
  ],
  "moves": [
    {
      "name": "thunderbolt",
      "type": "electric",
      "power": 90,
      "accuracy": 100,
      "pp": 15,
      "effect": "Has a 10% chance to paralyze the target."
    }
  ],
  "evolution_chain": {
    "name": "pichu",
    "evolves_to": {
      "name": "pikachu",
      "evolves_to": {
        "name": "raichu",
        "evolves_to": null
      }
    }
  }
}
```

#### Simulate Battle
```
GET /battle/simulate
```
Simulates a battle between two Pokémon and returns a turn-by-turn log.

**Query Parameters:**
- `pokemon1` (string, required): First Pokémon name
- `pokemon2` (string, required): Second Pokémon name

**Example Response:**
```json
{
  "battle_log": [
    {
      "action": "attack",
      "attacker": { "name": "pikachu" },
      "defender": { "name": "bulbasaur", "hp_left": 30 },
      "move": "thunderbolt",
      "damage": 25,
      "text": "Pikachu used Thunderbolt dealing 25 damage!"
    },
    {
      "action": "faint",
      "pokemon": { "name": "bulbasaur" },
      "text": "Bulbasaur fainted!"
    },
    {
      "action": "end",
      "text": "Battle Over. Winner: Pikachu"
    }
  ]
}
```

## 🧠 Battle Mechanics

The simulation implements several key Pokémon battle mechanics:

### Type Effectiveness
The system calculates damage multipliers based on Pokémon types:
- Super effective: 2× damage
- Not very effective: 0.5× damage
- No effect: 0× damage

### STAB (Same-Type Attack Bonus)
Moves matching the Pokémon's type get a 1.5× damage bonus

### Damage Calculation
Damage is calculated using this formula:
```
Damage = (((2 × Level / 5 + 2) × Power × Attack / Defense) / 50 + 2) × TypeMultiplier × STAB × RandomFactor
```

### Turn Order
Pokémon with higher Speed stats attack first

## 🎨 Frontend Features

### Dynamic UI Elements
- Real-time HP bars with color changes (green → yellow → red)
- Animated sprites for attacks and hits
- Victory confetti animation for the winner
- Interactive battle log with auto-scrolling

### Audio Feedback
- Attack sounds during battle sequences
- Faint sound when a Pokémon is defeated

### Responsive Design
- Works on desktop and mobile devices
- Pokémon info cards adapt to different screen sizes

## 🔮 Customization

### Adding More Pokémon
Edit the `pokemonList` array in `app.js` to include additional Pokémon:

```javascript
const pokemonList = [
  'pikachu', 'bulbasaur', 'charmander', 'squirtle', 
  'eevee', 'snorlax', 'jigglypuff', // ... add more here
];
```

### Modifying Battle Rules
Adjust battle parameters in `main.py`:
- Type effectiveness chart in `TYPE_EFFECTIVENESS`
- Damage calculation in `calculate_damage()`
- Move selection logic in `choose_move()`

### Customizing UI
Modify CSS in `index.html` to change:
- Color scheme
- Animation timing
- Layout and spacing

## 🐛 Troubleshooting

### Common Issues

1. **CORS errors**: Ensure the backend server is running on port 8000
2. **Pokémon not loading**: Check your internet connection as data is fetched from PokeAPI
3. **Battles not simulating**: Verify both Pokémon are selected before simulating

### Debug Mode
Start the server with increased logging:
```bash
uvicorn main:app --reload --log-level debug
```

Check browser console (F12) for JavaScript errors.

## 📝 Future Enhancements

Potential improvements for the project:
- [ ] Add more battle mechanics (status effects, critical hits)
- [ ] Implement player-vs-player battles
- [ ] Add more Pokémon and moves
- [ ] Create a mobile app version
- [ ] Add save/load battle functionality
- [ ] Implement AI opponent strategies


## 📄 License

This project is for educational purposes. Pokémon is a trademark of Nintendo/Creatures Inc./GAME FREAK Inc.

## 🙏 Acknowledgments

- [PokeAPI](https://pokeapi.co/) for providing comprehensive Pokémon data
- FastAPI team for the excellent web framework
- Pokémon franchise by Nintendo, Creatures Inc., and GAME FREAK Inc.

---

**Note**: This project is a technical demonstration and is not affiliated with or endorsed by Nintendo, Creatures Inc., or GAME FREAK Inc.
