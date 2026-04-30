#!/usr/bin/env python3
"""
Simple Calculator Web App using Flask
"""

from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Calculator</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:       #0e0e0f;
      --surface:  #1a1a1d;
      --card:     #222226;
      --border:   #2e2e33;
      --accent:   #f0c040;
      --accent2:  #e05a2b;
      --text:     #f2f2f0;
      --muted:    #6b6b72;
      --btn-num:  #27272b;
      --btn-op:   #2e2018;
      --btn-eq:   #f0c040;
      --radius:   18px;
    }

    body {
      min-height: 100vh;
      background: var(--bg);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'DM Mono', monospace;
      overflow: hidden;
    }

    /* Ambient glow background */
    body::before {
      content: '';
      position: fixed;
      width: 500px; height: 500px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(240,192,64,0.08) 0%, transparent 70%);
      top: 50%; left: 50%;
      transform: translate(-50%, -60%);
      pointer-events: none;
    }

    .calc-wrap {
      position: relative;
      animation: floatIn 0.6s cubic-bezier(0.34,1.56,0.64,1) both;
    }

    @keyframes floatIn {
      from { opacity: 0; transform: translateY(40px) scale(0.92); }
      to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    .label {
      font-family: 'Syne', sans-serif;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 12px;
      padding-left: 2px;
    }

    .calculator {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      width: 320px;
      box-shadow:
        0 0 0 1px rgba(255,255,255,0.03),
        0 40px 80px rgba(0,0,0,0.6),
        0 0 60px rgba(240,192,64,0.04);
    }

    /* Display */
    .display {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 20px;
      min-height: 100px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
    }

    .display-history {
      font-size: 12px;
      color: var(--muted);
      min-height: 18px;
      text-align: right;
      letter-spacing: 0.05em;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .display-current {
      font-size: 40px;
      font-weight: 300;
      color: var(--text);
      text-align: right;
      letter-spacing: -0.02em;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      transition: font-size 0.1s;
    }

    .display-current.long { font-size: 28px; }
    .display-current.vlong { font-size: 20px; }

    /* Button grid */
    .grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }

    button {
      all: unset;
      cursor: pointer;
      border-radius: 12px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'DM Mono', monospace;
      font-size: 18px;
      font-weight: 400;
      transition:
        background 0.12s,
        transform 0.08s,
        box-shadow 0.12s;
      position: relative;
      overflow: hidden;
      user-select: none;
    }

    button:active { transform: scale(0.93); }

    /* Ripple effect */
    button::after {
      content: '';
      position: absolute;
      width: 100%; height: 100%;
      top: 0; left: 0;
      background: rgba(255,255,255,0.07);
      opacity: 0;
      transition: opacity 0.15s;
    }
    button:active::after { opacity: 1; }

    /* Number buttons */
    .btn-num {
      background: var(--btn-num);
      color: var(--text);
      border: 1px solid rgba(255,255,255,0.04);
    }
    .btn-num:hover {
      background: #303035;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }

    /* Operator buttons */
    .btn-op {
      background: var(--btn-op);
      color: var(--accent);
      font-size: 20px;
      border: 1px solid rgba(240,192,64,0.12);
    }
    .btn-op:hover {
      background: #3a2a14;
      box-shadow: 0 4px 16px rgba(240,192,64,0.1);
    }

    /* Clear / special */
    .btn-clear {
      background: #2a1a1a;
      color: #f08080;
      border: 1px solid rgba(240,128,128,0.12);
    }
    .btn-clear:hover {
      background: #351f1f;
      box-shadow: 0 4px 16px rgba(240,80,80,0.12);
    }

    /* Sign / percent */
    .btn-fn {
      background: #1e1e28;
      color: #a0a0c0;
      border: 1px solid rgba(160,160,192,0.1);
    }
    .btn-fn:hover { background: #252530; }

    /* Equals */
    .btn-eq {
      background: var(--btn-eq);
      color: #1a1200;
      font-size: 24px;
      font-weight: 500;
      border: none;
      box-shadow: 0 4px 20px rgba(240,192,64,0.25);
    }
    .btn-eq:hover {
      background: #f5cc50;
      box-shadow: 0 6px 28px rgba(240,192,64,0.4);
    }

    /* Wide zero button */
    .span2 { grid-column: span 2; justify-content: flex-start; padding-left: 24px; }

    /* Error state */
    .display-current.error { color: #f08080; font-size: 22px; }

    /* Result flash animation */
    @keyframes resultFlash {
      0%   { color: var(--accent); }
      100% { color: var(--text); }
    }
    .display-current.flash { animation: resultFlash 0.4s ease-out forwards; }
  </style>
</head>
<body>
  <div class="calc-wrap">
    <div class="label">calculator v1</div>
    <div class="calculator">
      <div class="display">
        <div class="display-history" id="history"></div>
        <div class="display-current" id="current">0</div>
      </div>
      <div class="grid">
        <button class="btn-clear" onclick="clearAll()">AC</button>
        <button class="btn-fn"    onclick="toggleSign()">+/−</button>
        <button class="btn-fn"    onclick="percent()">%</button>
        <button class="btn-op"    onclick="setOp('/')">÷</button>

        <button class="btn-num" onclick="digit('7')">7</button>
        <button class="btn-num" onclick="digit('8')">8</button>
        <button class="btn-num" onclick="digit('9')">9</button>
        <button class="btn-op"  onclick="setOp('*')">×</button>

        <button class="btn-num" onclick="digit('4')">4</button>
        <button class="btn-num" onclick="digit('5')">5</button>
        <button class="btn-num" onclick="digit('6')">6</button>
        <button class="btn-op"  onclick="setOp('-')">−</button>

        <button class="btn-num" onclick="digit('1')">1</button>
        <button class="btn-num" onclick="digit('2')">2</button>
        <button class="btn-num" onclick="digit('3')">3</button>
        <button class="btn-op"  onclick="setOp('+')">+</button>

        <button class="btn-num span2" onclick="digit('0')">0</button>
        <button class="btn-num" onclick="dot()">.</button>
        <button class="btn-eq"  onclick="calculate()">=</button>
      </div>
    </div>
  </div>

  <script>
    let current   = '0';
    let previous  = '';
    let operator  = null;
    let justCalc  = false;

    const currentEl = document.getElementById('current');
    const historyEl = document.getElementById('history');

    function updateDisplay(val, flash = false) {
      currentEl.className = 'display-current';
      if (flash) currentEl.classList.add('flash');

      // Adjust font size for long numbers
      if (val.length > 12) currentEl.classList.add('vlong');
      else if (val.length > 8) currentEl.classList.add('long');

      currentEl.textContent = val;
    }

    function digit(d) {
      if (justCalc) { current = d; justCalc = false; }
      else if (current === '0' && d !== '.') current = d;
      else if (current.length < 15) current += d;
      updateDisplay(current);
    }

    function dot() {
      if (justCalc) { current = '0.'; justCalc = false; }
      else if (!current.includes('.')) current += '.';
      updateDisplay(current);
    }

    function setOp(op) {
      const opSymbols = { '+': '+', '-': '−', '*': '×', '/': '÷' };
      if (operator && !justCalc) calculate(true);
      previous = current;
      operator = op;
      justCalc = true;
      historyEl.textContent = previous + ' ' + opSymbols[op];
    }

    async function calculate(chained = false) {
      if (!operator || !previous) return;
      const opSymbols = { '+': '+', '-': '−', '*': '×', '/': '÷' };
      const expr = `${previous}${operator}${current}`;
      historyEl.textContent = `${previous} ${opSymbols[operator]} ${current} =`;

      try {
        const res = await fetch('/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ expression: expr })
        });
        const data = await res.json();

        if (data.error) {
          currentEl.className = 'display-current error';
          currentEl.textContent = data.error;
          current = '0'; operator = null; previous = '';
          return;
        }

        current = String(data.result);
        if (!chained) { operator = null; previous = ''; }
        justCalc = true;
        updateDisplay(current, !chained);
      } catch (e) {
        currentEl.className = 'display-current error';
        currentEl.textContent = 'Error';
      }
    }

    function clearAll() {
      current = '0'; previous = ''; operator = null; justCalc = false;
      historyEl.textContent = '';
      updateDisplay('0');
    }

    function toggleSign() {
      if (current !== '0') {
        current = current.startsWith('-') ? current.slice(1) : '-' + current;
        updateDisplay(current);
      }
    }

    function percent() {
      current = String(parseFloat(current) / 100);
      updateDisplay(current);
    }

    // Keyboard support
    document.addEventListener('keydown', e => {
      if (e.key >= '0' && e.key <= '9') digit(e.key);
      else if (e.key === '.') dot();
      else if (e.key === '+') setOp('+');
      else if (e.key === '-') setOp('-');
      else if (e.key === '*') setOp('*');
      else if (e.key === '/') { e.preventDefault(); setOp('/'); }
      else if (e.key === 'Enter' || e.key === '=') calculate();
      else if (e.key === 'Escape') clearAll();
      else if (e.key === 'Backspace') {
        if (current.length > 1) current = current.slice(0, -1);
        else current = '0';
        updateDisplay(current);
      }
    });
  </script>
</body>
</html>'''


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json(force=True)
    expression = data.get("expression", "")

    try:
        # Safe evaluation — only allow numbers and basic operators
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return jsonify({"error": "Invalid input"})

        result = eval(expression)  # safe: only digits/operators allowed above

        # Handle division by zero and infinity
        if result == float('inf') or result == float('-inf'):
            return jsonify({"error": "Can't ÷ by 0"})

        # Return clean integer if possible, else float
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        # Limit decimal places
        if isinstance(result, float):
            result = round(result, 10)
            result = float(f"{result:.10g}")

        return jsonify({"result": result})

    except ZeroDivisionError:
        return jsonify({"error": "Can't ÷ by 0"})
    except Exception:
        return jsonify({"error": "Error"})


if __name__ == "__main__":
    print("=" * 40)
    print("  Calculator App")
    print("  Open http://localhost:5001")
    print("=" * 40)
    app.run(debug=True, port=5001)
