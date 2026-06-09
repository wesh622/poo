import os
import time
import json
import base64
import logging
import threading
from datetime import datetime, date
from zoneinfo import ZoneInfo

import requests
import yfinance as yf
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
GITHUB_TOKEN     = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO      = os.environ.get('GITHUB_REPO', 'wesh622/poo')

PARIS = ZoneInfo('Europe/Paris')

DEFAULT_PORTFOLIO = {
    'positions': {
        'EXENS.PA': {'name': 'Exosens',      'qty': 2, 'buy': 61.20},
        'GTT.PA':   {'name': 'GTT',           'qty': 2, 'buy': 203.20},
        'IDL.PA':   {'name': 'ID Logistics',  'qty': 1, 'buy': 362.50},
        'MEDCL.PA': {'name': 'MedinCell',     'qty': 4, 'buy': 28.06},
    },
    'cash': 114.0,
    'transactions': [],
}

_portfolio: dict = {}
_portfolio_lock = threading.Lock()

# ── GitHub helpers ────────────────────────────────────────────────────────────

def _gh_headers():
    return {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

def gh_get(path):
    if not GITHUB_TOKEN:
        return None, None
    try:
        r = requests.get(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}',
            headers=_gh_headers(), timeout=10,
        )
        if r.ok:
            d = r.json()
            return base64.b64decode(d['content']).decode('utf-8'), d['sha']
    except Exception as e:
        logger.warning('gh_get %s: %s', path, e)
    return None, None

def gh_put(path, content, message, sha=None):
    if not GITHUB_TOKEN:
        return False
    try:
        payload = {
            'message': message,
            'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            'branch': 'main',
        }
        if sha:
            payload['sha'] = sha
        r = requests.put(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}',
            headers=_gh_headers(), json=payload, timeout=15,
        )
        return r.ok
    except Exception as e:
        logger.warning('gh_put %s: %s', path, e)
        return False

# ── Portfolio persistence ─────────────────────────────────────────────────────

def load_portfolio():
    global _portfolio
    content, _ = gh_get('portfolio.json')
    if content:
        try:
            _portfolio = json.loads(content)
            logger.info('Portfolio loaded from GitHub')
            return
        except Exception as e:
            logger.warning('portfolio.json parse error: %s', e)
    import copy
    _portfolio = copy.deepcopy(DEFAULT_PORTFOLIO)
    logger.info('Using default portfolio')

def save_portfolio():
    if not GITHUB_TOKEN:
        return
    with _portfolio_lock:
        content = json.dumps(_portfolio, ensure_ascii=False, indent=2)
    _, sha = gh_get('portfolio.json')
    if gh_put('portfolio.json', content, 'chore: update portfolio', sha):
        logger.info('Portfolio saved to GitHub')
    else:
        logger.error('Failed to save portfolio')

def append_history(entry: str):
    if not GITHUB_TOKEN:
        return
    def _do():
        path = 'data/historique.md'
        content, sha = gh_get(path)
        now = datetime.now(PARIS).strftime('%Y-%m-%d %H:%M')
        block = f'\n## {now}\n\n{entry}\n'
        updated = (content or '# Historique Portefeuille Omar\n') + block
        gh_put(path, updated, f'log: {now}', sha)
    threading.Thread(target=_do, daemon=True).start()

# ── Telegram ──────────────────────────────────────────────────────────────────

def send_telegram(text: str):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    try:
        r = requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': text}, timeout=10)
        if not r.ok:
            logger.error('Telegram %s: %s', r.status_code, r.text)
        else:
            logger.info('Telegram sent (%d chars)', len(text))
    except Exception as e:
        logger.error('Telegram send failed: %s', e)

def get_updates(offset=0):
    try:
        r = requests.get(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates',
            params={'offset': offset, 'timeout': 30, 'allowed_updates': ['message']},
            timeout=35,
        )
        if r.ok:
            return r.json().get('result', [])
    except Exception as e:
        logger.warning('getUpdates: %s', e)
    return []

# ── Price fetching ────────────────────────────────────────────────────────────

BOURSORAMA_CODES = {
    'EXENS.PA': '1rPEXENS',
    'GTT.PA':   '1rPGTT',
    'IDL.PA':   '1rPIDL',
    'MEDCL.PA': '1rPMEDCL',
    'EXAIL.PA': '1rPEXAIL',
}

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9',
}

def _parse_price(text: str):
    cleaned = ''.join(c for c in text.replace(',', '.') if c.isdigit() or c == '.')
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None

def get_price_boursorama(ticker: str):
    code = BOURSORAMA_CODES.get(ticker)
    if not code:
        return None
    try:
        r = requests.get(f'https://www.boursorama.com/cours/{code}/', headers=_HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        for sel in ['span.c-instrument.c-instrument--last', 'span[data-ist-last]',
                    'span.c-faceplate__price', 'span.c-instrument--last']:
            tag = soup.select_one(sel)
            if tag:
                p = _parse_price(tag.get_text(strip=True))
                if p and p > 0:
                    return p
    except Exception as e:
        logger.warning('Boursorama %s: %s', ticker, e)
    return None

def get_price_yfinance(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        try:
            p = stock.fast_info.last_price
            if p and p > 0:
                return float(p)
        except Exception:
            pass
        for period, interval in [('1d', '5m'), ('2d', '1d')]:
            hist = stock.history(period=period, interval=interval)
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
    except Exception as e:
        logger.warning('yfinance %s: %s', ticker, e)
    return None

def get_price(ticker: str):
    p = get_price_boursorama(ticker)
    if p:
        logger.info('%s -> %.3f EUR (Boursorama)', ticker, p)
        return p
    p = get_price_yfinance(ticker)
    if p:
        logger.info('%s -> %.3f EUR (yfinance)', ticker, p)
        return p
    logger.error('%s: unavailable', ticker)
    return None

# ── Report builder ────────────────────────────────────────────────────────────

def build_report(label: str) -> str:
    now = datetime.now(PARIS)
    lines = [label, f'📅 {now.strftime("%d/%m/%Y %H:%M")} (Paris)', '']
    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
        cash = _portfolio.get('cash', 0.0)

    total_inv = total_val = 0.0
    md_lines = [f'**{label}** — {now.strftime("%Y-%m-%d %H:%M")}', '']

    for ticker, pos in positions.items():
        price = get_price(ticker)
        inv = pos['qty'] * pos['buy']
        total_inv += inv
        if price:
            val = pos['qty'] * price
            pnl = val - inv
            pct = pnl / inv * 100
            s = '+' if pnl >= 0 else ''
            total_val += val
            lines.append(
                f'{pos["name"]} ({ticker})\n'
                f'  {pos["qty"]} x {price:.2f}€ = {val:.2f}€  '
                f'({s}{pnl:.2f}€ / {s}{pct:.1f}%)'
            )
            md_lines.append(f'- {pos["name"]} ({ticker}): {price:.2f}€  {s}{pnl:.2f}€ ({s}{pct:.1f}%)')
        else:
            total_val += inv
            lines.append(f'{pos["name"]} ({ticker})\n  ⚠️ Prix indisponible')
            md_lines.append(f'- {pos["name"]} ({ticker}): indisponible')

    pnl_t = total_val - total_inv
    pct_t = pnl_t / total_inv * 100 if total_inv else 0
    s = '+' if pnl_t >= 0 else ''
    lines.append(
        f'\n━━━━━━━━━━━━━━━━\n'
        f'Investi : {total_inv:.2f}€\n'
        f'Valeur  : {total_val:.2f}€\n'
        f'P&L     : {s}{pnl_t:.2f}€ ({s}{pct_t:.1f}%)\n'
        f'Especes : ~{cash:.0f}€\n'
        f'Total   : ~{total_val + cash:.0f}€'
    )
    md_lines += ['', f'**Total** : {total_val:.2f}€  P&L {s}{pnl_t:.2f}€ ({s}{pct_t:.1f}%)']

    append_history('\n'.join(md_lines))
    return '\n'.join(lines)

# ── Alerts ────────────────────────────────────────────────────────────────────

_prev_prices: dict[str, float] = {}

def check_alerts():
    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
    for ticker, pos in positions.items():
        price = get_price(ticker)
        if not price:
            continue
        prev = _prev_prices.get(ticker)
        if prev:
            chg = (price - prev) / prev * 100
            if abs(chg) >= 5:
                s = '+' if chg >= 0 else ''
                send_telegram(
                    f'⚠️ ALERTE {pos["name"]} ({ticker})\n'
                    f'Variation : {s}{chg:.1f}%\n'
                    f'Prix actuel : {price:.2f}€  |  Precedent : {prev:.2f}€'
                )
                logger.info('Alert %s %+.1f%%', ticker, chg)
        _prev_prices[ticker] = price

# ── Command handlers ──────────────────────────────────────────────────────────

HELP_TEXT = (
    '🤖 Commandes disponibles :\n\n'
    '/portfolio ou /p\n'
    '  Portefeuille avec P&L en temps reel\n\n'
    '/rapport ou /r\n'
    '  Rapport complet immediat\n\n'
    '/prix TICKER\n'
    '  Ex : /prix GTT.PA\n\n'
    '/achat TICKER QTY PRIX\n'
    '  Ex : /achat EXAIL.PA 3 132.50\n\n'
    '/vente TICKER QTY PRIX\n'
    '  Ex : /vente GTT.PA 1 205.00\n\n'
    '/help\n'
    '  Affiche ce message'
)

def cmd_prix(args):
    if not args:
        return 'Usage : /prix TICKER   ex : /prix GTT.PA'
    ticker = args[0].upper()
    if '.' not in ticker:
        ticker += '.PA'
    price = get_price(ticker)
    if price:
        return f'💹 {ticker} : {price:.2f}€'
    return f'Prix indisponible pour {ticker}'

def cmd_achat(args):
    if len(args) < 3:
        return 'Usage : /achat TICKER QTY PRIX   ex : /achat EXAIL.PA 3 132.50'
    ticker = args[0].upper()
    if '.' not in ticker:
        ticker += '.PA'
    try:
        qty   = int(args[1])
        price = float(args[2].replace(',', '.'))
    except ValueError:
        return 'Format invalide.   ex : /achat EXAIL.PA 3 132.50'

    with _portfolio_lock:
        positions = _portfolio['positions']
        if ticker in positions:
            old = positions[ticker]
            total_qty = old['qty'] + qty
            avg = (old['qty'] * old['buy'] + qty * price) / total_qty
            positions[ticker]['qty'] = total_qty
            positions[ticker]['buy'] = round(avg, 4)
            detail = f'PRU ajuste : {avg:.2f}€'
        else:
            positions[ticker] = {'name': ticker.replace('.PA', ''), 'qty': qty, 'buy': price}
            detail = 'Nouvelle position'
        _portfolio['transactions'].append({
            'date': datetime.now(PARIS).isoformat(),
            'type': 'achat', 'ticker': ticker, 'qty': qty, 'price': price,
        })

    save_portfolio()
    append_history(f'**ACHAT** {ticker} x{qty} @ {price:.2f}€ — {detail}')
    return f'✅ Achat enregistre\n{ticker} x{qty} @ {price:.2f}€\n{detail}'

def cmd_vente(args):
    if len(args) < 3:
        return 'Usage : /vente TICKER QTY PRIX   ex : /vente GTT.PA 1 205.00'
    ticker = args[0].upper()
    if '.' not in ticker:
        ticker += '.PA'
    try:
        qty   = int(args[1])
        price = float(args[2].replace(',', '.'))
    except ValueError:
        return 'Format invalide.   ex : /vente GTT.PA 1 205.00'

    with _portfolio_lock:
        positions = _portfolio['positions']
        if ticker not in positions:
            return f'{ticker} non trouve dans le portefeuille'
        pos = positions[ticker]
        pnl = (price - pos['buy']) * qty
        s   = '+' if pnl >= 0 else ''
        if qty >= pos['qty']:
            del positions[ticker]
            detail = f'Position cloturee. P&L : {s}{pnl:.2f}€'
        else:
            positions[ticker]['qty'] -= qty
            detail = f'Position reduite ({positions[ticker]["qty"]} restantes). P&L : {s}{pnl:.2f}€'
        _portfolio['cash']         = _portfolio.get('cash', 0.0) + price * qty
        _portfolio['transactions'].append({
            'date': datetime.now(PARIS).isoformat(),
            'type': 'vente', 'ticker': ticker, 'qty': qty, 'price': price, 'pnl': round(pnl, 2),
        })

    save_portfolio()
    append_history(f'**VENTE** {ticker} x{qty} @ {price:.2f}€ — {detail}')
    return f'✅ Vente enregistree\n{ticker} x{qty} @ {price:.2f}€\n{detail}'

def handle_command(text: str):
    parts = text.strip().split()
    cmd  = parts[0].lower().split('@')[0]
    args = parts[1:]
    if cmd == '/help':
        return HELP_TEXT
    if cmd in ('/portfolio', '/p'):
        return build_report('📊 Portefeuille (live)')
    if cmd in ('/rapport', '/r'):
        return build_report(f'📋 Rapport {datetime.now(PARIS).strftime("%H:%M")}')
    if cmd == '/prix':
        return cmd_prix(args)
    if cmd == '/achat':
        return cmd_achat(args)
    if cmd == '/vente':
        return cmd_vente(args)
    if cmd == '/start':
        return '🤖 Bot Portefeuille Omar\nTape /help pour voir les commandes.'
    return None

# ── Telegram polling thread ───────────────────────────────────────────────────

def poll_loop():
    offset = 0
    while True:
        try:
            updates = get_updates(offset)
            for upd in updates:
                offset = upd['update_id'] + 1
                msg     = upd.get('message', {})
                chat_id = str(msg.get('chat', {}).get('id', ''))
                text    = msg.get('text', '')
                if chat_id != str(TELEGRAM_CHAT_ID):
                    continue
                if text.startswith('/'):
                    reply = handle_command(text)
                    if reply:
                        send_telegram(reply)
        except Exception as e:
            logger.error('poll_loop: %s', e)
            time.sleep(5)

# ── Scheduled tasks ───────────────────────────────────────────────────────────

_last_report: dict[str, date | None] = {'morning': None, 'midday': None, 'evening': None}
_SCHEDULES = [
    ('morning', 9,  0,  '☀️ Rapport du matin'),
    ('midday',  12, 30, '🕛 Rapport de midi'),
    ('evening', 17, 35, '🌙 Rapport de cloture'),
]

def run_scheduled():
    now   = datetime.now(PARIS)
    if now.weekday() >= 5:
        return
    today = now.date()
    for key, h, m, label in _SCHEDULES:
        if now.hour == h and now.minute == m and _last_report[key] != today:
            _last_report[key] = today
            send_telegram(build_report(label))

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    load_portfolio()
    logger.info('Bot portefeuille started')
    send_telegram(
        '🤖 Bot Portefeuille Omar demarre\n\n'
        'Rapports : ☀️ 09h00 / 🕛 12h30 / 🌙 17h35 (lun-ven)\n'
        'Alerte si variation +-5%\n\n'
        'Tape /help pour les commandes'
    )

    threading.Thread(target=poll_loop, daemon=True).start()
    check_alerts()

    tick = 0
    while True:
        run_scheduled()
        if tick % 30 == 0 and tick > 0:
            if datetime.now(PARIS).weekday() < 5:
                check_alerts()
        time.sleep(30)
        tick += 1
