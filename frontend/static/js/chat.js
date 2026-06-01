const messages = document.getElementById('messages');
const input = document.getElementById('userInput');
const submitBtn = document.getElementById('submitBtn');

const storeCodeInput = document.getElementById('storeCodeInput');
const saveStoreCodeBtn = document.getElementById('saveStoreCodeBtn');
const storeCodeStatus = document.getElementById('storeCodeStatus');

console.log("CHAT JS LOADED");

let busy = false;

// ==============================
// SESSION + STORE CODE
// ==============================

let sessionId =
  localStorage.getItem("session_id") ||
  crypto.randomUUID();

localStorage.setItem(
  "session_id",
  sessionId
);

let storeCode =
  localStorage.getItem("store_code") || "";

if (storeCodeInput && storeCode) {
  storeCodeInput.value = storeCode;
}

if (storeCodeStatus && storeCode) {
  storeCodeStatus.innerText = `Using store code: ${storeCode}`;
}


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
  return String(s ?? "")
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function esc(s) {
  return String(s ?? "")
    .replace(/`/g, '\\`')
    .replace(/\$/g, '\\$');
}


// ==============================
// SAVE STORE CODE
// ==============================

if (saveStoreCodeBtn) {

  saveStoreCodeBtn.addEventListener(
    "click",
    function () {

      const value = storeCodeInput.value.trim();

      if (!value) {
        alert("Please enter a valid store code.");
        return;
      }

      localStorage.setItem(
        "store_code",
        value
      );

      storeCode = value;

      if (storeCodeStatus) {
        storeCodeStatus.innerText =
          `Using store code: ${storeCode}`;
      }

      alert("Store code saved successfully.");
    }
  );
}


// ==============================
// SEND MESSAGE
// ==============================

async function sendMessage() {

  const text = input.value.trim();

  if (!text || busy) return;

  // ==============================
  // GET SAVED STORE CODE
  // ==============================
  storeCode =
    localStorage.getItem("store_code") || "";

  if (!storeCode) {

    appendError(
      "Please enter and save your store code first."
    );

    return;
  }

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
        query: text,
        session_id: sessionId,
        store_code: storeCode
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

  let answer = "";

  const response = data.response;

  // ==============================
  // NEW BACKEND RESPONSE FORMAT
  // response: {
  //   answer: "...",
  //   data: [...],
  //   row_count: 1
  // }
  // ==============================
  if (
    response &&
    typeof response === "object" &&
    !Array.isArray(response)
  ) {

    if (response.answer) {

      answer = response.answer;

    } else if (response.data) {

      answer = formatData(response.data);

    } else {

      answer = JSON.stringify(
        response,
        null,
        2
      );
    }

  }

  // ==============================
  // OLD RESPONSE FORMAT
  // response: [...]
  // ==============================
  else if (Array.isArray(response)) {

    answer = formatData(response);

  }

  // ==============================
  // STRING RESPONSE
  // ==============================
  else if (typeof response === "string") {

    answer = response;

  }

  // ==============================
  // FALLBACK
  // ==============================
  else {

    answer = JSON.stringify(
      data,
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

  // IMPORTANT:
  // SQL is intentionally hidden from frontend now.
  // Do not render data.sql or data.generated_sql.

  row.appendChild(card);

  messages.appendChild(row);

  scroll();
}


// ==============================
// FORMAT DATA
// ==============================

function formatData(resultData) {

  if (!resultData) {
    return "No data found.";
  }

  if (Array.isArray(resultData)) {

    if (resultData.length === 0) {
      return "No matching records found.";
    }

    return resultData.map(row =>

      Object.entries(row)
        .map(([k, v]) => `${k}: ${v}`)
        .join('\n')

    ).join('\n\n');

  }

  return JSON.stringify(
    resultData,
    null,
    2
  );
}