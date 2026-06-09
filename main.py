import os
import time
import logging
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

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

PARIS = ZoneInfo('Europe/Paris')

PORTFOLIO = {
    'EXENS.PA': {'name': 'Exosens',      'qty': 2,  'buy': 61.20},
    'GTT.PA':   {'name': 'GTT',           'qty': 2,  'buy': 203.20},
    'IDL.PA':   {'name': 'ID Logistics',  'qty': 1,  'buy': 362.50},
    'MEDCL.PA': {'name': 'MedinCell',     'qty': 4,  'buy': 28.06},
}

BOURSORAMA_CODES = {
    'EXENS.PA': '1rPEXENS',
    'GTT.PA':   '1rPGTT',
    'IDL.PA':   '1rPIDL',
    'MEDCL.PA': '1rPMEDCL',
}

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'fr-FR,fr;q=0.9',
}

_prev_prices: dict[str, float] = {}
_last_report: dict[str, date | None] = {'morning': None, 'midday': None, 'evening': None}


def send_telegram(text: str) -> None:
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    try:
        r = requests.post(
            url,
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': text},
            timeout=10,
        )
        if not r.ok:
            logger.error('Telegram error %s: %s', r.status_code, r.text)
            return
        logger.info('Telegram message sent (%d chars)', len(text))
    except Exception as e:
        logger.error('Telegram send failed: %s', e)


def _parse_price(text: str) -> float | None:
    cleaned = ''.join(c for c in text.replace(',', '.') if c.isdigit() or c == '.')
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def get_price_boursorama(ticker: str) -> float | None:
    code = BOURSORAMA_CODES.get(ticker)
    if not code:
        return None
    url = f'https://www.boursorama.com/cours/{code}/'
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        for sel in [
            'span.c-instrument.c-instrument--last',
            'span[data-ist-last]',
            'span.c-faceplate__price',
            'span.c-instrument--last',
        ]:
            tag = soup.select_one(sel)
            if tag:
                p = _parse_price(tag.get_text(strip=True))
                if p and p > 0:
                    return p
    except Exception as e:
        logger.warning('Boursorama %s: %s', ticker, e)
    return None


def get_price_yfinance(ticker: str) -> float | None:
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


def get_price(ticker: str) -> float | None:
    p = get_price_boursorama(ticker)
    if p:
        logger.info('%s → %.3f€ (Boursorama)', ticker, p)
        return p
    p = get_price_yfinance(ticker)
    if p:
        logger.info('%s → %.3f€ (yfinance)', ticker, p)
        return p
    logger.error('%s: price unavailable', ticker)
    return None


def build_report(label: str) -> str:
    now = datetime.now(PARIS)
    lines = [f'{label}', f'📅 {now.strftime("%d/%m/%Y %H:%M")} (Paris)', '']
    total_inv = total_val = 0.0

    for ticker, pos in PORTFOLIO.items():
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
        else:
            total_val += inv
            lines.append(f'{pos["name"]} ({ticker})\n  ⚠️ Prix indisponible')

    pnl_t = total_val - total_inv
    pct_t = pnl_t / total_inv * 100 if total_inv else 0
    s = '+' if pnl_t >= 0 else ''
    cash = 114.0
    lines.append(
        f'\n━━━━━━━━━━━━━━━━\n'
        f'Investi : {total_inv:.2f}€\n'
        f'Valeur  : {total_val:.2f}€\n'
        f'P&L     : {s}{pnl_t:.2f}€ ({s}{pct_t:.1f}%)\n'
        f'Especes : ~{cash:.0f}€\n'
        f'Total   : ~{total_val + cash:.0f}€'
    )
    return '\n'.join(lines)


def check_alerts() -> None:
    for ticker, pos in PORTFOLIO.items():
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
                logger.info('Alert sent for %s: %+.1f%%', ticker, chg)
        _prev_prices[ticker] = price


_SCHEDULES = [
    ('morning', 9,  0,  '☀️ Rapport du matin'),
    ('midday',  12, 30, '🕛 Rapport de midi'),
    ('evening', 17, 35, '🌙 Rapport de clôture'),
]


def run_scheduled() -> None:
    now = datetime.now(PARIS)
    if now.weekday() >= 5:
        return
    today = now.date()
    for key, h, m, label in _SCHEDULES:
        if now.hour == h and now.minute == m and _last_report[key] != today:
            _last_report[key] = today
            send_telegram(build_report(label))


if __name__ == '__main__':
    logger.info('Bot portefeuille started')
    send_telegram(
        '🤖 Bot Portefeuille Omar demarre\n\n'
        '📊 Rapports automatiques :\n'
        '  ☀️ 09h00 ouverture\n'
        '  🕛 12h30 mi-journee\n'
        '  🌙 17h35 cloture\n'
        '  Lundi-vendredi uniquement\n\n'
        '⚠️ Alerte si variation +-5% (toutes les 15 min)\n\n'
        '📌 En attente achat : EXAIL.PA (~400€)'
    )

    # Seed initial prices for alert tracking
    check_alerts()

    tick = 0
    while True:
        run_scheduled()
        # Every 30 ticks × 30s = 15 minutes
        if tick % 30 == 0 and tick > 0:
            now = datetime.now(PARIS)
            if now.weekday() < 5:
                check_alerts()
        time.sleep(30)
        tick += 1
