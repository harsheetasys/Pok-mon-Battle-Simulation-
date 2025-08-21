const API_BASE = 'http://127.0.0.1:8000';

const pokemonList = [
  'pikachu', 'bulbasaur', 'charmander', 'squirtle', 'eevee', 'snorlax',
  'jigglypuff', 'meowth', 'psyduck', 'magikarp', 'gyarados', 'alakazam'
];

let pokemonData = [null, null];
let battleTurns = [];
let isBattleActive = false;

// --- DOM Elements ---
const battleLogDiv = document.getElementById('battle-log');
const autoPlayBtn = document.getElementById('auto-play');
const simulateBtn = document.getElementById('simulate-battle');
const resetBtn = document.getElementById('reset-battle');
const pokemonSelect1 = document.getElementById('pokemon1');
const pokemonSelect2 = document.getElementById('pokemon2');
const battleStage = document.getElementById('battle-stage');

const attackSound = document.getElementById('attack-sound');
const faintSound = document.getElementById('faint-sound');

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function populateDropdowns() {
  pokemonList.forEach(name => {
    [pokemonSelect1, pokemonSelect2].forEach(sel => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = capitalize(name);
        sel.appendChild(option);
    });
  });
  pokemonSelect1.selectedIndex = 0;
  pokemonSelect2.selectedIndex = 1;
}

async function fetchPokemonData(n) {
  const selectedName = document.getElementById(`pokemon${n}`).value;
  const infoDiv = document.getElementById(`pokemon${n}-info`);
  infoDiv.innerHTML = 'Loading...';

  try {
    const res = await fetch(`${API_BASE}/pokemon/${selectedName}`);
    if (!res.ok) throw new Error(`Failed to fetch ${selectedName}`);
    const data = await res.json();
    pokemonData[n - 1] = data;

    infoDiv.innerHTML = `
      <img id="pokeimg${n}" src="${data.sprite}" alt="${data.name}" />
      <div class="stats">
        <h3>${capitalize(data.name)} (ID: ${data.id})</h3>
        <div>
          <strong>HP:</strong> 
          <span id="cur-hp${n}">${data.stats.hp}</span> / 
          <span id="max-hp${n}">${data.stats.hp}</span>
          <div class="hp-bar">
            <div class="hp-fill" id="hpbar${n}" style="width: 100%;"></div>
          </div>
        </div>
        <strong>Types:</strong> ${data.types.join(', ')}<br/>
        <strong>Abilities:</strong> ${data.abilities.map(a => a.name).join(', ')}<br/>
        <strong>Moves (first 4):</strong> ${data.moves.map(m => m.name).join(', ')}<br/>
      </div>
    `;
  } catch (err) {
    infoDiv.textContent = err.message;
  }
}

function updateHPBar(n, currentHP, maxHP) {
  const percent = Math.max(0, 100 * (currentHP / maxHP));
  const hpBarFill = document.getElementById(`hpbar${n}`);
  const curHpText = document.getElementById(`cur-hp${n}`);
  
  if (hpBarFill) {
    hpBarFill.style.width = `${percent}%`;
    hpBarFill.classList.remove('low', 'medium');
    if (percent < 20) hpBarFill.classList.add('low');
    else if (percent < 50) hpBarFill.classList.add('medium');
  }
  if (curHpText) curHpText.textContent = Math.max(0, Math.round(currentHP));
}

async function simulateBattle() {
  if (isBattleActive) return;
  setControls(false);
  battleLogDiv.textContent = 'Simulating battle...';

  const p1Name = pokemonSelect1.value;
  const p2Name = pokemonSelect2.value;

  try {
    const res = await fetch(`${API_BASE}/battle/simulate?pokemon1=${p1Name}&pokemon2=${p2Name}`);
    if (!res.ok) throw new Error('Battle simulation failed.');
    const data = await res.json();
    battleTurns = data.battle_log;
    battleLogDiv.textContent = 'Simulation complete! Click Auto Play to watch.';
    autoPlayBtn.disabled = false;
  } catch (err) {
    battleLogDiv.textContent = err.message;
    resetBtn.disabled = false;
  }
}

async function autoPlayBattle() {
  if (isBattleActive || battleTurns.length === 0) return;
  setControls(false);
  isBattleActive = true;
  battleLogDiv.textContent = '';
  battleStage.innerHTML = ''; 

  const sprite1 = document.getElementById('pokeimg1');
  const sprite2 = document.getElementById('pokeimg2');

  if (!sprite1 || !sprite2) {
      resetBattle();
      return;
  }

  sprite1.className = 'battle-sprite';
  sprite2.className = 'battle-sprite';
  sprite1.style.transform = 'scaleX(-1)';

  battleStage.appendChild(sprite1);
  battleStage.appendChild(sprite2);
  
  await delay(500);

  for (const turn of battleTurns) {
    battleLogDiv.textContent += turn.text + '\n';
    battleLogDiv.scrollTop = battleLogDiv.scrollHeight;

    if (turn.action === 'attack') {
        await handleAttackAnimation(turn, sprite1, sprite2);
    } else if (turn.action === 'faint') {
        await handleFaintAnimation(turn, sprite1, sprite2);
        break;
    }
    
    await delay(1000);
  }
  
  const winnerLog = battleTurns.find(turn => turn.action === 'end');
  if (winnerLog && winnerLog.text.includes('Winner:')) {
    const winnerName = winnerLog.text.split('Winner: ')[1].trim();
    if (winnerName.toLowerCase() === pokemonData[0]?.name.toLowerCase()) {
        if(sprite1) {
            sprite1.classList.add('animate-victory');
            triggerVictoryConfetti();
        }
    } else if (winnerName.toLowerCase() === pokemonData[1]?.name.toLowerCase()) {
        if(sprite2) {
            sprite2.classList.add('animate-victory');
            triggerVictoryConfetti();
        }
    }
  }
  
  isBattleActive = false;
  resetBtn.disabled = false;
}

async function handleAttackAnimation(turn, sprite1, sprite2) {
    const isP1Attacking = turn.attacker.name === pokemonData[0]?.name;
    const attackerSprite = isP1Attacking ? sprite1 : sprite2;
    const defenderSprite = isP1Attacking ? sprite2 : sprite1;
    const defenderIdx = isP1Attacking ? 2 : 1;

    attackerSprite.classList.add('animate-lunge');
    playSound(attackSound);
    await delay(250);

    defenderSprite.classList.add('animate-hit');
    updateHPBar(defenderIdx, turn.defender.hp_left, pokemonData[defenderIdx - 1].stats.hp);
    await delay(300);

    attackerSprite.classList.remove('animate-lunge');
    defenderSprite.classList.remove('animate-hit');
}

async function handleFaintAnimation(turn, sprite1, sprite2) {
    const faintedIdx = turn.pokemon.name === pokemonData[0]?.name ? 1 : 2;
    const faintedSprite = (faintedIdx === 1) ? sprite1 : sprite2;
    
    if(faintedSprite) faintedSprite.style.opacity = '0';
    playSound(faintSound);
    await delay(800);
}

// --- NEW: Victory Confetti Function ---
function triggerVictoryConfetti() {
    const colors = ['#FFD700', '#FF69B4', '#00BFFF', '#ADFF2F'];
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti-piece';
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = `${Math.random() * 2}s`;
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
        battleStage.appendChild(confetti);
    }
}

function resetBattle() {
  isBattleActive = false;
  battleTurns = [];
  battleLogDiv.textContent = '';
  battleStage.innerHTML = '';
  setControls(true);
  autoPlayBtn.disabled = true;
  
  fetchPokemonData(1);
  fetchPokemonData(2);
}

function setControls(enabled) {
    simulateBtn.disabled = !enabled;
    resetBtn.disabled = !enabled;
    pokemonSelect1.disabled = !enabled;
    pokemonSelect2.disabled = !enabled;
}

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const playSound = (sound) => {
    sound.currentTime = 0;
    sound.play().catch(error => {
        console.error(`Sound playback failed:`, error);
    });
};

// Event Listeners
simulateBtn.onclick = simulateBattle;
autoPlayBtn.onclick = autoPlayBattle;
resetBtn.onclick = resetBattle;
pokemonSelect1.onchange = resetBattle;
pokemonSelect2.onchange = resetBattle;

window.onload = async () => {
    populateDropdowns();
    await fetchPokemonData(1);
    await fetchPokemonData(2);
    setControls(true);
};