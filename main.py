import os
import copy
import time
import json
import base64
import logging
import threading
from datetime import datetime, date, timedelta
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
        'ALV.DE':   {'name': 'Allianz SE',                         'qty': 1, 'buy': 245.22},
        'PAEEM.PA': {'name': 'Amundi PEA Emergent (MSCI Emerging)', 'qty': 3, 'buy': 31.69},
        'CS.PA':    {'name': 'AXA',                                'qty': 2, 'buy': 27.72},
        'EXA.PA':   {'name': 'Exail Technologies',                 'qty': 3, 'buy': 84.09,  'target': 110.0, 'stop': 58.0,  'alloc_target': 400},
        'EXENS.PA': {'name': 'Exosens',                            'qty': 2, 'buy': 61.75,  'target': 95.0,  'stop': 48.0,  'alloc_target': 500},
        'GTT.PA':   {'name': 'GTT',                                'qty': 2, 'buy': 204.51, 'target': 240.0, 'stop': 170.0, 'alloc_target': 300},
        'IDL.PA':   {'name': 'ID Logistics Group',                 'qty': 1, 'buy': 364.94, 'target': 460.0, 'stop': 290.0, 'alloc_target': 250},
        'AI.PA':    {'name': "L'Air Liquide",                      'qty': 1, 'buy': 158.25},
        'MC.PA':    {'name': 'LVMH',                               'qty': 5, 'buy': 662.52},
        'MEDCL.PA': {'name': 'MedinCell',                          'qty': 8, 'buy': 28.01,  'target': 45.0,  'stop': 20.0,  'alloc_target': 300},
        'RUI.PA':   {'name': 'Rubis',                              'qty': 3, 'buy': 21.59},
        'SAN.PA':   {'name': 'Sanofi',                             'qty': 2, 'buy': 86.99},
        'SU.PA':    {'name': 'Schneider Electric',                 'qty': 1, 'buy': 234.52},
    },
    'cash': 384.69,
    'transactions': [],
    'promises': [],
    'theses': {},  # rempli depuis DEFAULT_THESES au premier chargement
    'access': {'superusers': [], 'whitelist': [], 'blacklist': []},
}

_portfolio: dict = {}
_portfolio_lock = threading.Lock()

# ── GitHub helpers ──────────────────────────────────────────────────────────────────────────────────

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

# ── Portfolio persistence ─────────────────────────────────────────────────────────────────────────────

def load_portfolio():
    global _portfolio
    content, _ = gh_get('portfolio.json')
    if content:
        try:
            _portfolio = json.loads(content)
            _portfolio.setdefault('promises', [])
            if not _portfolio.get('theses'):
                _portfolio['theses'] = copy.deepcopy(DEFAULT_THESES)
            access = _portfolio.setdefault('access', {})
            for key in ('superusers', 'whitelist', 'blacklist'):
                access.setdefault(key, [])
            logger.info('Portfolio loaded from GitHub')
            return
        except Exception as e:
            logger.warning('portfolio.json parse error: %s', e)
    _portfolio = copy.deepcopy(DEFAULT_PORTFOLIO)
    _portfolio['theses'] = copy.deepcopy(DEFAULT_THESES)
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

def append_strategy(entry: str):
    if not GITHUB_TOKEN:
        return
    def _do():
        path = 'data/strategie.md'
        content, sha = gh_get(path)
        if not content:
            return
        now = datetime.now(PARIS).strftime('%Y-%m-%d')
        block = f'\n### Revue {now}\n\n{entry}\n'
        marker = '<!-- Les revues automatiques du bot sont ajoutees ici chaque lundi -->'
        if marker in content:
            updated = content.replace(marker, marker + block)
        else:
            updated = content + block
        gh_put(path, updated, f'review: revue hebdo {now}', sha)
    threading.Thread(target=_do, daemon=True).start()

def append_journal(entry: str):
    if not GITHUB_TOKEN:
        return
    def _do():
        path = 'data/journal.md'
        content, sha = gh_get(path)
        now = datetime.now(PARIS).strftime('%Y-%m-%d')
        block = f'\n## {now}\n\n{entry}\n'
        header = '# Journal quotidien Portefeuille Omar\n\nSuivi jour par jour : mouvement de prix, actualite probable, promesses en cours.\n'
        updated = (content or header) + block
        gh_put(path, updated, f'journal: {now}', sha)
    threading.Thread(target=_do, daemon=True).start()

def append_access_log(entry: str):
    if not GITHUB_TOKEN:
        return
    def _do():
        path = 'data/access_log.md'
        content, sha = gh_get(path)
        header = (
            "# Journal d'acces au bot\n\n"
            "Chaque ligne : date/heure (Paris) | identifiant Telegram | requete | statut | reponse.\n"
        )
        updated = (content or header) + entry + '\n'
        gh_put(path, updated, 'log: acces bot', sha)
    threading.Thread(target=_do, daemon=True).start()

# ── Controle d'acces (owner / super-utilisateurs / whitelist / blacklist) ──────────────────────

def is_owner(chat_id: str) -> bool:
    return chat_id == str(TELEGRAM_CHAT_ID)

def _access() -> dict:
    with _portfolio_lock:
        return {
            'superusers': [str(x) for x in _portfolio.get('access', {}).get('superusers', [])],
            'whitelist':  [str(x) for x in _portfolio.get('access', {}).get('whitelist', [])],
            'blacklist':  [str(x) for x in _portfolio.get('access', {}).get('blacklist', [])],
        }

def is_admin(chat_id: str) -> bool:
    return is_owner(chat_id) or chat_id in _access()['superusers']

def is_blacklisted(chat_id: str) -> bool:
    return chat_id in _access()['blacklist']

def is_authorized(chat_id: str) -> bool:
    if is_blacklisted(chat_id):
        return False
    if is_admin(chat_id):
        return True
    return chat_id in _access()['whitelist']

def cmd_manage_access(key: str, args):
    if not args:
        return f'Usage : /{key} add ID | /{key} remove ID | /{key} list'
    action = args[0].lower()
    with _portfolio_lock:
        lst = _portfolio.setdefault('access', {}).setdefault(key, [])
        if action == 'list':
            items = list(lst)
        elif action in ('add', 'remove') and len(args) >= 2:
            value = args[1]
            if action == 'add' and value not in lst:
                lst.append(value)
            elif action == 'remove' and value in lst:
                lst.remove(value)
            items = None
        else:
            return f'Usage : /{key} add ID | /{key} remove ID | /{key} list'
    if items is not None:
        return f'{key} :\n' + ('\n'.join(f'- {x}' for x in items) if items else '(vide)')
    save_portfolio()
    return f'✅ {key} mis a jour ({action} {value})'

def cmd_acces(args):
    n = 10
    if args:
        try:
            n = max(1, min(50, int(args[0])))
        except ValueError:
            pass
    content, _ = gh_get('data/access_log.md')
    entries = [l for l in content.splitlines() if l.startswith('- ')] if content else []
    if not entries:
        return "Aucun acces enregistre pour le moment."
    return '🔐 Derniers acces au bot\n\n' + '\n'.join(entries[-n:])

# ── Telegram ─────────────────────────────────────────────────────────────────────────────────

def send_telegram(text: str, chat_id: str = None):
    target = chat_id or TELEGRAM_CHAT_ID
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    try:
        r = requests.post(url, json={'chat_id': target, 'text': text}, timeout=10)
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

# ── Price fetching ─────────────────────────────────────────────────────────────────────────────────

BOURSORAMA_CODES = {
    'EXENS.PA': '1rPEXENS',
    'GTT.PA':   '1rPGTT',
    'IDL.PA':   '1rPIDL',
    'MEDCL.PA': '1rPMEDCL',
    'EXA.PA':   '1rPEXA',
    'AI.PA':    '1rPAI',
    'CS.PA':    '1rPCS',
    'MC.PA':    '1rPMC',
    'RUI.PA':   '1rPRUI',
    'SAN.PA':   '1rPSAN',
    'SU.PA':    '1rPSU',
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

def _price_plausible(price: float, ref: float) -> bool:
    if ref <= 0:
        return True
    return (ref * 0.02) <= price <= (ref * 50)

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

def get_price(ticker: str, buy_price: float = 0.0):
    p = get_price_boursorama(ticker)
    if p:
        if _price_plausible(p, buy_price):
            logger.info('%s -> %.3f EUR (Boursorama)', ticker, p)
            return p
        logger.warning('%s: Boursorama %.2f hors plage (ref %.2f), bascule yfinance', ticker, p, buy_price)
    p = get_price_yfinance(ticker)
    if p:
        if _price_plausible(p, buy_price):
            logger.info('%s -> %.3f EUR (yfinance)', ticker, p)
            return p
        logger.warning('%s: yfinance %.2f hors plage (ref %.2f), indispo', ticker, p, buy_price)
        return None
    logger.error('%s: unavailable', ticker)
    return None

def get_week_change(ticker: str):
    try:
        hist = yf.Ticker(ticker).history(period='7d', interval='1d')
        closes = hist['Close'].dropna()
        if len(closes) < 2:
            return None, None, None
        start, end = float(closes.iloc[0]), float(closes.iloc[-1])
        pct = (end - start) / start * 100 if start else None
        return start, end, pct
    except Exception as e:
        logger.warning('week change %s: %s', ticker, e)
        return None, None, None

# ── News fetching (best effort) ──────────────────────────────────────────────────

def get_news_headline(ticker: str):
    code = BOURSORAMA_CODES.get(ticker)
    if not code:
        return None
    try:
        r = requests.get(f'https://www.boursorama.com/cours/{code}/actualites/', headers=_HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        for sel in ['a.c-news-list__link', 'div.c-news-list__item a', 'article a', 'h3 a']:
            tag = soup.select_one(sel)
            if tag:
                text = tag.get_text(strip=True)
                if text and len(text) > 10:
                    return text
    except Exception as e:
        logger.warning('News %s: %s', ticker, e)
    return None

def get_all_news_headlines(ticker: str, limit: int = 5):
    code = BOURSORAMA_CODES.get(ticker)
    if not code:
        return []
    out = []
    try:
        r = requests.get(f'https://www.boursorama.com/cours/{code}/actualites/', headers=_HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        for sel in ['a.c-news-list__link', 'div.c-news-list__item a', 'article a', 'h3 a']:
            for tag in soup.select(sel):
                text = tag.get_text(strip=True)
                if text and len(text) > 10 and text not in out:
                    out.append(text)
                if len(out) >= limit:
                    return out
            if out:
                return out
    except Exception as e:
        logger.warning('News %s: %s', ticker, e)
    return out

# ── Report builder ─────────────────────────────────────────────────────────────────────────────────

def build_report(label: str) -> str:
    now = datetime.now(PARIS)
    lines = [label, f'📅 {now.strftime("%d/%m/%Y %H:%M")} (Paris)', '']
    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
        cash = _portfolio.get('cash', 0.0)

    total_inv = total_val = 0.0
    md_lines = [f'**{label}** — {now.strftime("%Y-%m-%d %H:%M")}', '']

    for ticker, pos in positions.items():
        price = get_price(ticker, pos['buy'])
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
        f'Especes : ~{cash:.2f}€\n'
        f'Total   : ~{total_val + cash:.2f}€'
    )
    md_lines += ['', f'**Total** : {total_val:.2f}€  P&L {s}{pnl_t:.2f}€ ({s}{pct_t:.1f}%)']

    append_history('\n'.join(md_lines))
    return '\n'.join(lines)

# ── Conseil / Strategie ────────────────────────────────────────────────────────────────────────────

# Thèses et scores de depart par ticker (persistes ensuite dans portfolio.json
# sous 'theses' et ajustes automatiquement selon les resultats reels)
DEFAULT_THESES = {
    'EXENS.PA': {
        'score': 22, 'target': 95.0, 'stop': 48.0, 'alloc_target': 500,
        'resume': 'Défense/vision nocturne — commandes record, doublement capacité prod',
    },
    'GTT.PA': {
        'score': 21, 'target': 240.0, 'stop': 170.0, 'alloc_target': 300,
        'resume': 'Licences méthaniers GNL — marges 60%+, 53 commandes 2026',
    },
    'IDL.PA': {
        'score': 20, 'target': 460.0, 'stop': 290.0, 'alloc_target': 250,
        'resume': 'Logistique contractuelle — CA +14% T1 2026, track record 5 ans',
    },
    'MEDCL.PA': {
        'score': 20, 'target': 45.0, 'stop': 20.0, 'alloc_target': 300,
        'resume': "Biotech BEPO® — dossier EMA accepte, 2 analystes a l'achat",
    },
    'EXA.PA': {
        'score': 23, 'target': 110.0, 'stop': 58.0, 'alloc_target': 400,
        'resume': 'Drones navals — CA +40% T1 2026, carnet >1 Md€',
    },
    'ALV.DE': {
        'score': 17, 'target': 294.0, 'stop': 196.0, 'alloc_target': 300,
        'resume': 'Allianz — assureur europeen leader, dividende stable, position rendement/diversification (pas une conviction de croissance)',
    },
    'PAEEM.PA': {
        'score': 16, 'target': 40.0, 'stop': 24.0, 'alloc_target': 150,
        'resume': 'ETF Amundi PEA Emergent — diversification marches emergents, exposition macro plutot que stock-picking',
    },
    'CS.PA': {
        'score': 16, 'target': 34.0, 'stop': 21.0, 'alloc_target': 100,
        'resume': 'AXA — assureur diversifie, valorisation decotee vs pairs, dividende solide, profil value',
    },
    'AI.PA': {
        'score': 19, 'target': 190.0, 'stop': 130.0, 'alloc_target': 200,
        'resume': "L'Air Liquide — leader mondial des gaz industriels, cash-flows recurrents, expose a l'hydrogene/transition energetique",
    },
    'MC.PA': {
        'score': 18, 'target': 795.0, 'stop': 530.0, 'alloc_target': 3300,
        'resume': 'LVMH — leader du luxe, marques diversifiees, resilience historique ; position deja large, pas de renforcement vise',
    },
    'RUI.PA': {
        'score': 17, 'target': 27.0, 'stop': 16.0, 'alloc_target': 100,
        'resume': 'Rubis — distribution/stockage energie, dividende eleve, diversification geographique, profil value/rendement cyclique',
    },
    'SAN.PA': {
        'score': 18, 'target': 104.0, 'stop': 70.0, 'alloc_target': 200,
        'resume': 'Sanofi — pharma diversifiee, pipeline vaccins/immunologie, profil defensif, croissance moderee',
    },
    'SU.PA': {
        'score': 20, 'target': 281.0, 'stop': 188.0, 'alloc_target': 250,
        'resume': 'Schneider Electric — leader electrification/efficacite energetique, expose data centers et IA, execution solide',
    },
}

def _conseil_action(ticker: str, pos: dict, price: float | None, thèse: dict) -> str:
    target = thèse.get('target') or pos.get('target', 0)
    stop   = thèse.get('stop')   or pos.get('stop', 0)
    alloc_t = thèse.get('alloc_target') or pos.get('alloc_target', 0)
    score  = thèse.get('score', 25)

    if not price:
        return '⚠️ Prix indisponible'

    inv = pos['qty'] * pos['buy']
    val = pos['qty'] * price
    pnl_pct = (price - pos['buy']) / pos['buy'] * 100
    s = '+' if pnl_pct >= 0 else ''

    # Score degrade par les resultats reels (promesses manquees, stops passes)
    if score < 14:
        return f'🔴 Score thèse critique ({score}/25) — sortie a envisager malgre le prix'
    # Stop déclenché
    if stop and price <= stop:
        return f'🔴 STOP atteint ({price:.2f}€ ≤ {stop:.2f}€) — envisager la vente'
    # Objectif proche
    if target and price >= target * 0.95:
        return f'🟡 Objectif quasi-atteint ({price:.2f}€ / cible {target:.2f}€) — sécuriser les gains'
    # Sous-pondéré et P&L positif ou légèrement négatif : renforcer
    if alloc_t and inv < alloc_t * 0.85 and pnl_pct > -15 and score >= 18:
        manque = alloc_t - inv
        return f'🟢 Renforcer (+{manque:.0f}€ restants pour atteindre cible {alloc_t}€)'
    # Sur-pondéré
    if alloc_t and inv > alloc_t * 1.2:
        return f'🔵 Tenir — surpondéré vs cible {alloc_t}€, ne pas renforcer'
    return f'🔵 Tenir — P&L {s}{pnl_pct:.1f}%, score {score}/25, dans les bornes'

def _priority_reinforcement(positions: dict, theses: dict, cash: float):
    prio = sorted(
        [(t, theses[t]['alloc_target'] - pos['qty'] * pos['buy'])
         for t, pos in positions.items() if t in theses and
         theses[t]['alloc_target'] - pos['qty'] * pos['buy'] > 50 and
         theses[t].get('score', 0) >= 18],
        key=lambda x: -theses.get(x[0], {}).get('score', 0)
    )
    if prio and cash > 50:
        return prio[0]
    return None

def build_conseil() -> str:
    now = datetime.now(PARIS)
    lines = [f'🧠 Conseils au {now.strftime("%d/%m/%Y %H:%M")}', '']
    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
        cash = _portfolio.get('cash', 0.0)
        theses = dict(_portfolio.get('theses', {}))

    total_inv = 0.0
    for ticker, pos in positions.items():
        price = get_price(ticker, pos['buy'])
        conseil = _conseil_action(ticker, pos, price, theses.get(ticker, {}))
        prix_str = f'{price:.2f}€' if price else 'N/A'
        pru = pos['buy']
        lines.append(f'{pos["name"]} ({ticker}) — {prix_str} (PRU {pru:.2f}€)')
        lines.append(f'  {conseil}')
        total_inv += pos['qty'] * pos['buy']
        lines.append('')

    lines.append(f'💰 Cash disponible : {cash:.2f}€')
    top = _priority_reinforcement(positions, theses, cash)
    if top:
        lines.append(f'🔖 Priorité : {top[0]} (+{top[1]:.0f}€ pour atteindre cible)')
    return '\n'.join(lines)

def build_strategie_summary() -> str:
    lines = ['📊 Stratégie & Thèses', '']
    lines.append('Critères : sous-cotée · projets LT · track record · innovation · marché fort')
    lines.append('Seuil achat : 18/25 · Seuil renforcement : 20/25 · Seuil sortie : <14/25\n')
    with _portfolio_lock:
        theses = dict(_portfolio.get('theses', {}))
    for ticker, t in theses.items():
        lines.append(f'{ticker}  score {t["score"]}/25')
        lines.append(f'  {t["resume"]}')
        lines.append(f'  Objectif {t["target"]}€ · Stop {t["stop"]}€ · Cible alloc {t["alloc_target"]}€')
        lines.append('')
    return '\n'.join(lines)

def adjust_thesis(ticker: str, delta: int, reason: str):
    with _portfolio_lock:
        theses = _portfolio.setdefault('theses', {})
        if ticker not in theses:
            return
        old = theses[ticker]['score']
        new = max(0, min(25, old + delta))
        theses[ticker]['score'] = new
    save_portfolio()
    append_strategy(f'Score {ticker} ajusté {delta:+d} ({reason}) — {old}/25 → {new}/25')

# ── Promesses (annonces des entreprises) ────────────────────────────────────────────

def cmd_annonce(raw: str):
    if '|' not in raw:
        return "Usage : /annonce TICKER texte de l'annonce | YYYY-MM-DD"
    left, deadline = raw.rsplit('|', 1)
    deadline = deadline.strip()
    parts = left.strip().split(maxsplit=1)
    if len(parts) < 2:
        return "Usage : /annonce TICKER texte de l'annonce | YYYY-MM-DD"
    ticker, text = parts[0].upper(), parts[1].strip()
    if '.' not in ticker:
        ticker += '.PA'
    try:
        datetime.strptime(deadline, '%Y-%m-%d')
    except ValueError:
        return 'Date invalide, format attendu YYYY-MM-DD'

    with _portfolio_lock:
        _portfolio.setdefault('promises', []).append({
            'ticker': ticker, 'text': text, 'deadline': deadline,
            'date_added': datetime.now(PARIS).date().isoformat(),
            'status': 'en attente',
        })
    save_portfolio()
    return f'📌 Promesse enregistree pour {ticker}\n"{text}"\nEcheance : {deadline}'

def cmd_promesses():
    with _portfolio_lock:
        promises = list(_portfolio.get('promises', []))
    if not promises:
        return "Aucune promesse suivie. Ajoute avec /annonce TICKER texte | YYYY-MM-DD"
    today = datetime.now(PARIS).date().isoformat()
    lines = ['📌 Promesses suivies', '']
    for i, p in enumerate(promises, start=1):
        if p['status'] == 'en attente' and p['deadline'] <= today:
            flag = '⚠️ ECHEANCE ATTEINTE — a verifier'
        else:
            flag = p['status']
        lines.append(f'{i}. {p["ticker"]} — {p["text"]}')
        lines.append(f'   Echeance {p["deadline"]} · {flag}')
        lines.append('')
    return '\n'.join(lines)

def cmd_maj_promesse(args):
    if len(args) < 2:
        return 'Usage : /maj_promesse N tenu|manque   (N = numero affiche par /promesses)'
    try:
        idx = int(args[0]) - 1
    except ValueError:
        return 'N doit etre un nombre'
    statut = args[1].lower()
    if statut not in ('tenu', 'manque'):
        return 'Statut doit etre "tenu" ou "manque"'
    with _portfolio_lock:
        promises = _portfolio.get('promises', [])
        if not (0 <= idx < len(promises)):
            return 'Numero invalide'
        promises[idx]['status'] = statut
        p = promises[idx]
    append_strategy(f'Promesse {p["ticker"]} ("{p["text"]}") marquee **{statut}** (echeance {p["deadline"]})')
    delta = 1 if statut == 'tenu' else -2
    reason = f'promesse {"tenue" if statut == "tenu" else "manquee"} : "{p["text"]}"'
    adjust_thesis(p['ticker'], delta, reason)
    return f'✅ Promesse #{idx + 1} marquee "{statut}" — score {p["ticker"]} ajuste {delta:+d}'

# ── Daily journal ─────────────────────────────────────────────────────────────────────────────────

_daily_close: dict[str, float] = {}
_last_journal: date | None = None

def run_daily_journal():
    global _last_journal
    now = datetime.now(PARIS)
    if now.weekday() >= 5:
        return
    if now.hour != 17 or now.minute != 40:
        return
    today = now.date()
    if _last_journal == today:
        return
    _last_journal = today

    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
        promises = list(_portfolio.get('promises', []))

    lines = []
    for ticker, pos in positions.items():
        price = get_price(ticker, pos['buy'])
        if not price:
            lines.append(f'**{pos["name"]} ({ticker})** : prix indisponible')
            continue
        prev = _daily_close.get(ticker)
        if prev:
            chg = (price - prev) / prev * 100
            s = '+' if chg >= 0 else ''
            mvt = f'{s}{chg:.1f}% vs hier ({prev:.2f}€ → {price:.2f}€)'
        else:
            mvt = f'{price:.2f}€ (premiere mesure du jour)'
        headlines = get_all_news_headlines(ticker, limit=3)
        actu = '; '.join(headlines) if headlines else 'actualite non recuperee'
        lines.append(f'**{pos["name"]} ({ticker})** : {mvt}\n  Actualites recentes : {actu}')
        _daily_close[ticker] = price

    today_iso = today.isoformat()
    overdue = [p for p in promises if p.get('status') == 'en attente' and p.get('deadline', '9999-12-31') <= today_iso]
    if overdue:
        lines.append('\n⚠️ Promesses a verifier (echeance atteinte) :')
        for p in overdue:
            lines.append(f'- {p["ticker"]} : {p["text"]} (echeance {p["deadline"]})')

    entry = '\n\n'.join(lines)
    append_journal(entry)
    logger.info('Daily journal written')

# ── Weekly review ───────────────────────────────────────────────────────────────────────────

_last_weekly: date | None = None

def run_weekly_review():
    global _last_weekly
    now = datetime.now(PARIS)
    if now.weekday() != 0 or now.hour != 9 or now.minute != 0:
        return
    today = now.date()
    if _last_weekly == today:
        return
    _last_weekly = today

    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
        theses = dict(_portfolio.get('theses', {}))

    lines = []
    total_inv = total_val = 0.0
    alerts = []
    to_penalize = []
    for ticker, pos in positions.items():
        price = get_price(ticker, pos['buy'])
        inv = pos['qty'] * pos['buy']
        total_inv += inv
        if price:
            val = pos['qty'] * price
            total_val += val
            pnl_pct = (price - pos['buy']) / pos['buy'] * 100
            s = '+' if pnl_pct >= 0 else ''
            lines.append(f'- {pos["name"]} ({ticker}): {price:.2f}€  {s}{pnl_pct:.1f}%')
            t = theses.get(ticker, {})
            if t.get('stop') and price <= t['stop']:
                alerts.append(f'STOP {ticker} ({price:.2f}€ ≤ {t["stop"]:.2f}€)')
                if not t.get('stop_flagged'):
                    to_penalize.append(ticker)
            elif t.get('target') and price >= t['target'] * 0.95:
                alerts.append(f'OBJECTIF proche {ticker} ({price:.2f}€ / {t["target"]:.2f}€)')
                if t.get('stop_flagged'):
                    with _portfolio_lock:
                        _portfolio['theses'][ticker]['stop_flagged'] = False
            else:
                if t.get('stop_flagged'):
                    with _portfolio_lock:
                        _portfolio['theses'][ticker]['stop_flagged'] = False
        else:
            total_val += inv
            lines.append(f'- {pos["name"]} ({ticker}): indisponible')

    for ticker in to_penalize:
        with _portfolio_lock:
            _portfolio['theses'][ticker]['stop_flagged'] = True
        adjust_thesis(ticker, -3, 'stop atteint lors de la revue hebdo')

    pnl_t = total_val - total_inv
    s = '+' if pnl_t >= 0 else ''
    summary = '\n'.join(lines)
    summary += f'\n\nTotal investi : {total_inv:.2f}€ | Valeur : {total_val:.2f}€ | P&L {s}{pnl_t:.2f}€'
    if alerts:
        summary += '\n\n⚠️ Alertes stratégie : ' + ', '.join(alerts)

    append_strategy(summary)
    msg = f'📆 Revue hebdo {now.strftime("%d/%m/%Y")}\n\n' + summary
    if alerts:
        msg += '\n\n' + build_conseil()
    send_telegram(msg)
    logger.info('Weekly review done')

# ── Weekly report (samedi) ──────────────────────────────────────────────────────────────────

def build_weekly_report() -> str:
    now = datetime.now(PARIS)
    week_start = (now - timedelta(days=6)).strftime('%d/%m')
    week_end = now.strftime('%d/%m/%Y')
    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
        cash = _portfolio.get('cash', 0.0)
        theses = dict(_portfolio.get('theses', {}))
        promises = list(_portfolio.get('promises', []))

    lines = [f'📅 Rapport hebdomadaire — semaine du {week_start} au {week_end}', '']
    for ticker, pos in positions.items():
        price = get_price(ticker, pos['buy'])
        start, end, pct = get_week_change(ticker)
        t = theses.get(ticker, {})
        lines.append(f'{pos["name"]} ({ticker})')
        if pct is not None:
            s = '+' if pct >= 0 else ''
            lines.append(f'  Semaine : {s}{pct:.1f}% ({start:.2f}€ → {end:.2f}€)')
        else:
            lines.append('  Semaine : variation indisponible')
        if t:
            lines.append(f'  Prévision : objectif {t["target"]:.2f}€ · stop {t["stop"]:.2f}€ · score thèse {t.get("score", "-")}/25')
        lines.append(f'  Conseil : {_conseil_action(ticker, pos, price, t)}')
        lines.append('')

    today_iso = now.date().isoformat()
    horizon = (now.date() + timedelta(days=14)).isoformat()
    soon = [p for p in promises if p.get('status') == 'en attente' and p.get('deadline', '9999-12-31') <= horizon]
    if soon:
        lines.append('📌 Échéances à venir (14 jours) :')
        for p in soon:
            flag = ' — ÉCHÉANCE DÉPASSÉE' if p['deadline'] <= today_iso else ''
            lines.append(f'- {p["ticker"]} : {p["text"]} ({p["deadline"]}){flag}')
        lines.append('')

    lines.append(f'💰 Cash disponible : {cash:.2f}€')
    top = _priority_reinforcement(positions, theses, cash)
    if top:
        lines.append(f'🔖 Priorité renforcement : {top[0]} (+{top[1]:.0f}€ pour atteindre cible)')
    return '\n'.join(lines)

_last_weekly_report: date | None = None

def run_weekly_saturday_report():
    global _last_weekly_report
    now = datetime.now(PARIS)
    if now.weekday() != 5 or now.hour != 10 or now.minute != 0:
        return
    today = now.date()
    if _last_weekly_report == today:
        return
    _last_weekly_report = today
    send_telegram(build_weekly_report())
    logger.info('Weekly Saturday report sent')

# ── Alerts ──────────────────────────────────────────────────────────────────────────────────

_prev_prices: dict[str, float] = {}

def check_alerts():
    with _portfolio_lock:
        positions = dict(_portfolio['positions'])
    for ticker, pos in positions.items():
        price = get_price(ticker, pos['buy'])
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

# ── Command handlers ────────────────────────────────────────────────────────────────────────────

HELP_TEXT = (
    '🤖 Commandes disponibles :\n\n'
    '/portfolio ou /p\n'
    '  Portefeuille avec P&L en temps reel\n\n'
    '/conseil ou /c\n'
    '  Recommandations : renforcer / tenir / alléger\n\n'
    '/strategie ou /s\n'
    '  Thèses et scores de chaque position\n\n'
    '/rapport ou /r\n'
    '  Rapport complet immediat\n\n'
    '/semaine\n'
    '  Rapport hebdomadaire (variation 7j, previsions, conseils) — auto envoye le samedi 10h\n\n'
    '/prix TICKER\n'
    '  Ex : /prix GTT.PA\n\n'
    '/achat TICKER QTY PRIX\n'
    '  Ex : /achat EXA.PA 3 132.50\n\n'
    '/vente TICKER QTY PRIX\n'
    '  Ex : /vente GTT.PA 1 205.00\n\n'
    "/annonce TICKER texte | YYYY-MM-DD\n"
    "  Logue une promesse d'entreprise avec echeance\n"
    "  Ex : /annonce EXA.PA Livraison 50 drones | 2026-09-30\n\n"
    '/promesses\n'
    '  Liste les promesses suivies et leur statut\n\n'
    '/maj_promesse N tenu|manque\n'
    '  Valide si une promesse a ete tenue (ajuste le score de la these)\n\n'
    '/help\n'
    '  Affiche ce message'
)

ADMIN_HELP_TEXT = (
    '\n\n🔐 Commandes super-utilisateur :\n\n'
    '/acces [N]\n'
    '  Affiche les N derniers acces au bot (defaut 10), refuses compris\n\n'
    '/whitelist add|remove|list ID\n'
    '  Gere les comptes Telegram autorises a utiliser le bot\n\n'
    '/blacklist add|remove|list ID\n'
    '  Gere les comptes Telegram explicitement bloques\n\n'
    '/superuser add|remove|list ID  (owner uniquement)\n'
    '  Gere les super-utilisateurs (acces complet)'
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
        return 'Usage : /achat TICKER QTY PRIX   ex : /achat EXA.PA 3 132.50'
    ticker = args[0].upper()
    if '.' not in ticker:
        ticker += '.PA'
    try:
        qty   = int(args[1])
        price = float(args[2].replace(',', '.'))
    except ValueError:
        return 'Format invalide.   ex : /achat EXA.PA 3 132.50'

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

def handle_command(text: str, chat_id: str):
    raw   = text.strip()
    parts = raw.split()
    cmd   = parts[0].lower().split('@')[0]
    args  = parts[1:]
    rest  = raw[len(parts[0]):].strip() if len(parts) > 1 else ''

    if cmd == '/help':
        return HELP_TEXT + (ADMIN_HELP_TEXT if is_admin(chat_id) else '')
    if cmd in ('/portfolio', '/p'):
        return build_report('📊 Portefeuille (live)')
    if cmd in ('/rapport', '/r'):
        return build_report(f'📋 Rapport {datetime.now(PARIS).strftime("%H:%M")}')
    if cmd in ('/conseil', '/c'):
        return build_conseil()
    if cmd in ('/strategie', '/s'):
        return build_strategie_summary()
    if cmd == '/semaine':
        return build_weekly_report()
    if cmd == '/prix':
        return cmd_prix(args)
    if cmd == '/achat':
        return cmd_achat(args)
    if cmd == '/vente':
        return cmd_vente(args)
    if cmd == '/annonce':
        return cmd_annonce(rest)
    if cmd == '/promesses':
        return cmd_promesses()
    if cmd == '/maj_promesse':
        return cmd_maj_promesse(args)
    if cmd == '/acces':
        if not is_admin(chat_id):
            return '⛔ Reserve au owner et aux super-utilisateurs.'
        return cmd_acces(args)
    if cmd == '/whitelist':
        if not is_admin(chat_id):
            return '⛔ Reserve au owner et aux super-utilisateurs.'
        return cmd_manage_access('whitelist', args)
    if cmd == '/blacklist':
        if not is_admin(chat_id):
            return '⛔ Reserve au owner et aux super-utilisateurs.'
        return cmd_manage_access('blacklist', args)
    if cmd == '/superuser':
        if not is_owner(chat_id):
            return '⛔ Reserve au owner.'
        return cmd_manage_access('superusers', args)
    if cmd == '/start':
        return '🤖 Bot Portefeuille Omar\nTape /help pour voir les commandes.'
    return None

# ── Telegram polling thread ───────────────────────────────────────────────────────────────────

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
                if not text:
                    continue
                frm     = msg.get('from', {})
                uid     = frm.get('id', '')
                label   = f"@{frm['username']}" if frm.get('username') else (frm.get('first_name') or 'inconnu')
                now_str = datetime.now(PARIS).strftime('%Y-%m-%d %H:%M:%S')

                if not is_authorized(chat_id):
                    append_access_log(
                        f'- {now_str} | chat_id={chat_id} user={label} (id {uid}) | '
                        f'requete: "{text[:200]}" | statut: REFUSE (non autorise)'
                    )
                    continue

                if text.startswith('/'):
                    reply = handle_command(text, chat_id)
                    reply_log = (reply[:200] + '…') if reply and len(reply) > 200 else (reply or '(pas de reponse)')
                    append_access_log(
                        f'- {now_str} | chat_id={chat_id} user={label} (id {uid}) | '
                        f'requete: "{text[:200]}" | statut: autorise | reponse: "{reply_log}"'
                    )
                    if reply:
                        send_telegram(reply, chat_id)
                else:
                    append_access_log(
                        f'- {now_str} | chat_id={chat_id} user={label} (id {uid}) | '
                        f'requete: "{text[:200]}" | statut: ignore (pas une commande)'
                    )
        except Exception as e:
            logger.error('poll_loop: %s', e)
            time.sleep(5)

# ── Scheduled tasks ────────────────────────────────────────────────────────────────────────────

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

# ── Entry point ─────────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    load_portfolio()
    logger.info('Bot portefeuille started')
    send_telegram(
        '🤖 Bot Portefeuille Omar demarre\n\n'
        'Rapports : ☀️ 09h00 / 🕛 12h30 / 🌙 17h35 (lun-ven)\n'
        'Journal quotidien : 📓 17h40 (lun-ven)\n'
        'Revue strategie : 📆 lundi 09h00 (ajuste les scores selon les stops/promesses)\n'
        'Rapport hebdomadaire : 🗞️ samedi 10h00 (variation 7j, previsions, conseils)\n'
        'Alerte si variation +-5%\n\n'
        'Tape /help pour les commandes'
    )

    threading.Thread(target=poll_loop, daemon=True).start()
    check_alerts()

    tick = 0
    while True:
        run_scheduled()
        run_daily_journal()
        run_weekly_review()
        run_weekly_saturday_report()
        if tick % 30 == 0 and tick > 0:
            if datetime.now(PARIS).weekday() < 5:
                check_alerts()
        time.sleep(30)
        tick += 1
