// API Configuration - Update this URL after deploying to Google Cloud Run
const API_BASE_URL = 'https://word-vector-api-phpg7cac6a-uc.a.run.app';

const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const header = document.querySelector('.status');
const loadingBanner = document.getElementById('loading-banner');
const loadingMessage = document.getElementById('loading-message');
const loadingProgress = document.getElementById('loading-progress');
const loadingBar = document.getElementById('loading-bar');

const simA = document.getElementById('simA');
const simB = document.getElementById('simB');
const runSim = document.getElementById('runSim');
const simResult = document.getElementById('simResult');

const neiWord = document.getElementById('neiWord');
const neiTopn = document.getElementById('neiTopn');
const runNei = document.getElementById('runNei');
const neiResult = document.getElementById('neiResult');

const anaPos = document.getElementById('anaPos');
const anaNeg = document.getElementById('anaNeg');
const anaTopn = document.getElementById('anaTopn');
const runAna = document.getElementById('runAna');
const anaResult = document.getElementById('anaResult');

let loadingCheckInterval = null;

function getAPI(){
  return API_BASE_URL;
}

function setStatus(state, text){
  header.classList.remove('status-ready','status-initializing','status-error');
  header.classList.add(`status-${state}`);
  statusText.textContent = text;
}

function showLoadingBanner(message, progress){
  if(loadingBanner){
    loadingBanner.style.display = 'block';
    if(loadingMessage) loadingMessage.textContent = message;
    if(loadingBar) loadingBar.style.width = `${progress}%`;
    
    if(loadingProgress && progress < 100){
      loadingProgress.textContent = `${progress}% complete`;
    } else if(loadingProgress && progress >= 100){
      loadingProgress.textContent = 'Finalizing...';
    }
  }
}

function hideLoadingBanner(){
  if(loadingBanner) loadingBanner.style.display = 'none';
}

async function checkLoadingStatus(){
  const base = getAPI();
  if(!base || base === 'YOUR_CLOUD_RUN_URL_HERE') return;
  
  try{
    const r = await fetch(`${base}/loading-status`);
    const status = await r.json();
    
    if(status.model_loaded){
      hideLoadingBanner();
      setStatus('ready', `Ready (${status.vocabulary_size.toLocaleString()} words)`);
      if(loadingCheckInterval){
        clearInterval(loadingCheckInterval);
        loadingCheckInterval = null;
      }
    } else {
      showLoadingBanner(status.loading_status || 'Loading model...', status.loading_progress || 0);
      setStatus('initializing', 'Model loading...');
    }
  }catch(e){
    console.log('Error checking loading status:', e);
  }
}

async function checkHealth(){
  const base = getAPI();
  if(!base || base === 'YOUR_CLOUD_RUN_URL_HERE'){
    setStatus('error','API URL not configured');
    return;
  }
  try{
    const r = await fetch(`${base}/health`);
    const j = await r.json();
    
    if(j.status === 'ready'){
      hideLoadingBanner();
      setStatus('ready', `Ready (${j.vocabulary_size.toLocaleString()} words)`);
      if(loadingCheckInterval){
        clearInterval(loadingCheckInterval);
        loadingCheckInterval = null;
      }
    } else {
      setStatus('initializing', 'Model loading...');
      // Start polling loading status
      if(!loadingCheckInterval){
        loadingCheckInterval = setInterval(checkLoadingStatus, 2000);
        checkLoadingStatus(); // Check immediately
      }
    }
  }catch(e){
    setStatus('error', 'API unreachable - Check connection');
    showLoadingBanner('Error: Cannot connect to API. Please refresh the page.', 0);
  }
}

async function fetchJSON(path, params = {}){
  const base = getAPI();
  if(!base) throw new Error('API not configured');
  
  const url = new URL(`${base}${path}`);
  Object.keys(params).forEach(key => {
    if(params[key] !== null && params[key] !== undefined){
      url.searchParams.append(key, params[key]);
    }
  });
  
  const r = await fetch(url);
  const json = await r.json();
  
  if(!r.ok){
    throw new Error(json.detail || 'API request failed');
  }
  return json;
}

function withLoading(btn, fn){
  return async ()=>{
    btn.disabled = true; btn.textContent = 'Running…';
    try{ await fn(); }
    finally{ btn.disabled = false; btn.textContent = btn.dataset.label || btn.textContent; }
  };
}

runSim.dataset.label = 'Compare';
runNei.dataset.label = 'Find';
runAna.dataset.label = 'Solve';

runSim.addEventListener('click', withLoading(runSim, async ()=>{
  simResult.textContent = '';
  try{
    const a = simA.value.trim().toLowerCase();
    const b = simB.value.trim().toLowerCase();
    if(!a || !b) throw new Error('Enter both words');
    const res = await fetchJSON('/similarity', { word1: a, word2: b });
    simResult.textContent = `Similarity: ${Number(res.similarity).toFixed(4)}\n\n"${res.word1}" and "${res.word2}" are ${(res.similarity * 100).toFixed(1)}% similar`;
  }catch(e){ 
    simResult.textContent = `Error: ${e.message}`; 
    if(e.message.includes('not found')){
      simResult.textContent += '\n\nTip: Try common words like "happy", "sad", "king", "queen"';
    }
  }
}));

runNei.addEventListener('click', withLoading(runNei, async ()=>{
  neiResult.textContent = '';
  try{
    const word = neiWord.value.trim().toLowerCase();
    const topn = Math.max(1, Math.min(50, Number(neiTopn.value||10)));
    if(!word) throw new Error('Enter a word');
    const res = await fetchJSON('/neighbors', { word, topn });
    if(res.neighbors && Array.isArray(res.neighbors)){
      const items = res.neighbors.map(n => `${n.word} (${n.similarity.toFixed(4)})`).join('\n');
      neiResult.textContent = `Similar words to "${res.word}":\n\n${items}`;
    }else{
      neiResult.textContent = JSON.stringify(res,null,2);
    }
  }catch(e){ 
    neiResult.textContent = `Error: ${e.message}`;
    if(e.message.includes('not found')){
      neiResult.textContent += '\n\nTip: Try common words like "ocean", "computer", "happiness"';
    }
  }
}));

// Analogy builder variables
let wordCount = 3;
let wordOperators = { 2: 'minus', 3: 'plus' }; // word1 is always positive (no operator before it)

// Operator button handlers
document.addEventListener('click', (e) => {
  if(e.target.classList.contains('operator-btn')){
    const wordNum = e.target.dataset.word;
    const currentOp = wordOperators[wordNum];
    const newOp = currentOp === 'plus' ? 'minus' : 'plus';
    wordOperators[wordNum] = newOp;
    e.target.classList.remove('plus', 'minus');
    e.target.classList.add(newOp);
    e.target.textContent = newOp === 'plus' ? '+' : '−';
  }
});

// Add word button
document.getElementById('addWord')?.addEventListener('click', () => {
  if(wordCount >= 6) {
    anaResult.textContent = 'Maximum 6 words allowed';
    return;
  }
  wordCount++;
  wordOperators[wordCount] = 'plus';
  
  const equation = document.querySelector('.word-equation');
  const questionMark = equation.querySelector('.question-mark');
  const equals = equation.querySelector('.equals');
  
  // Create operator button
  const opGroup = document.createElement('div');
  opGroup.className = 'operator-group';
  opGroup.innerHTML = `<button class="operator-btn plus" data-word="${wordCount}">+</button>`;
  
  // Create word input
  const wordGroup = document.createElement('div');
  wordGroup.className = 'word-input-group';
  wordGroup.innerHTML = `
    <input type="text" id="word${wordCount}" class="word-input" placeholder="word" />
    <button class="remove-word" data-word="${wordCount}">×</button>
  `;
  
  equation.insertBefore(opGroup, equals);
  equation.insertBefore(wordGroup, equals);
});

// Remove word handler
document.addEventListener('click', (e) => {
  if(e.target.classList.contains('remove-word')){
    if(wordCount <= 3) {
      anaResult.textContent = 'Need at least 3 words for analogy';
      return;
    }
    const wordNum = e.target.dataset.word;
    const input = document.getElementById(`word${wordNum}`);
    const inputGroup = input.parentElement;
    const opGroup = inputGroup.previousElementSibling;
    
    inputGroup.remove();
    opGroup.remove();
    delete wordOperators[wordNum];
    wordCount--;
  }
});

runAna.addEventListener('click', withLoading(runAna, async ()=>{
  anaResult.textContent = '';
  try{
    // Collect all words and their operators
    const words = [];
    const positiveWords = [];
    const negativeWords = [];
    
    for(let i = 1; i <= wordCount; i++){
      const input = document.getElementById(`word${i}`);
      if(!input) continue;
      
      const word = input.value.trim().toLowerCase();
      if(!word) continue;
      
      if(i === 1){
        // First word is always positive
        positiveWords.push(word);
        words.push(word);
      } else if(wordOperators[i] === 'plus'){
        positiveWords.push(word);
        words.push(`+ ${word}`);
      } else {
        negativeWords.push(word);
        words.push(`- ${word}`);
      }
    }
    
    if(positiveWords.length === 0) throw new Error('Need at least one positive word');
    if(positiveWords.length < 2 || negativeWords.length < 1){
      throw new Error('Need at least 2 positive words and 1 negative word. Example: king + woman - man');
    }
    
    const topn = Math.max(1, Math.min(20, Number(anaTopn.value||5)));
    
    // API expects: a (pos), c (pos), b (neg)
    const res = await fetchJSON('/analogy', { 
      a: positiveWords[0], 
      c: positiveWords[1], 
      b: negativeWords[0],
      topn 
    });
    
    if(res.results && Array.isArray(res.results)){
      const equation = words.join(' ');
      const items = res.results.map(r => `${r.word} (${r.similarity.toFixed(4)})`).join('\n');
      anaResult.textContent = `${equation} = ?\n\nTop Results:\n${items}`;
    }else{
      anaResult.textContent = JSON.stringify(res,null,2);
    }
  }catch(e){ 
    anaResult.textContent = `Error: ${e.message}`;
    if(e.message.includes('Need at least')){
      anaResult.textContent += '\n\nTip: Build equations like "king - man + woman" to find "queen"';
    }
  }
}));

// Initial health check on load
checkHealth();

// Check health every 30 seconds to catch any issues
setInterval(checkHealth, 30000);
