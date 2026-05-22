const messages = document.getElementById('messages');
const input = document.getElementById('userInput');
const submitBtn = document.getElementById('submitBtn');

console.log("CHAT JS LOADED");
let busy = false;

// ==============================
// HELPERS
// ==============================

function grow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 130) + 'px';
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function scroll() {
  messages.scrollTop = messages.scrollHeight;
}

function make(tag, cls) {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  return el;
}

function h(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function esc(s) {
  return String(s)
    .replace(/`/g, '\\`')
    .replace(/\$/g, '\\$');
}

// ==============================
// SEND MESSAGE
// ==============================

async function sendMessage() {

  const text = input.value.trim();

  if (!text || busy) return;

  busy = true;

  submitBtn.disabled = true;

  input.value = '';

  appendUser(text);

  const thinking = appendThinking();

  try {

    const res = await fetch('http://127.0.0.1:8000/chat/query', {

      method: 'POST',

      headers: {
        'Content-Type': 'application/json'
      },

      body: JSON.stringify({
        query: text
      })

    });

    const json = await res.json();

    console.log("Backend Response:", json);

    thinking.remove();

    if (json.error) {

      appendError(json.error);

    } else {

      renderBot(json);

    }

  } catch (err) {

    console.error(err);

    thinking.remove();

    appendError(
      'Could not reach backend.'
    );

  } finally {

    busy = false;

    submitBtn.disabled = false;

  }
}

// ==============================
// USER MESSAGE
// ==============================

function appendUser(text) {

  const row = make('div', 'msg-row user');

  row.innerHTML =
    `<div class="avatar">You</div>
     <div class="bubble">${h(text)}</div>`;

  messages.appendChild(row);

  scroll();
}

// ==============================
// THINKING
// ==============================

function appendThinking() {

  const row = make('div', 'thinking-row');

  row.innerHTML =
    `<div class="avatar">DB</div>
     <div class="thinking-bubble">
       Thinking...
     </div>`;

  messages.appendChild(row);

  scroll();

  return row;
}

// ==============================
// ERROR
// ==============================

function appendError(msg) {

  const row = make('div', 'msg-row bot');

  row.innerHTML =
    `<div class="avatar">!</div>
     <div class="error-bubble">${h(msg)}</div>`;

  messages.appendChild(row);

  scroll();
}

// ==============================
// RENDER BOT
// ==============================

function renderBot(data) {

  console.log(data);

  const resultData = data.response || [];

  const sql = data.sql || null;

  let answer = "";

  if (Array.isArray(resultData)) {

    answer = resultData.map(row =>

      Object.entries(row)
        .map(([k, v]) => `${k}: ${v}`)
        .join('\n')

    ).join('\n\n');

  } else {

    answer = JSON.stringify(
      resultData,
      null,
      2
    );

  }

  const row = make('div', 'msg-row bot');

  row.innerHTML =
    `<div class="avatar">DB</div>`;

  const card = make('div', 'bot-card');

  const ans = make('div', 'card-answer');

  ans.innerHTML =
    `<pre>${h(answer)}</pre>`;

  card.appendChild(ans);

  if (sql) {

    const block = make('div', 'card-sql');

    block.innerHTML =
      `<div class="sql-topbar">
         <span>Generated SQL</span>
       </div>

       <pre>${h(sql)}</pre>`;

    card.appendChild(block);
  }

  row.appendChild(card);

  messages.appendChild(row);

  scroll();
}