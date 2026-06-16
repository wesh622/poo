# Résumé de session — Bot Portefeuille Omar (2026-06-16)

## Contexte

Repo : `wesh622/poo` — bot Telegram (`main.py`) qui suit un portefeuille
d'actions Euronext Paris (PEA + CTO), récupère les prix via Boursorama
(scraping) avec fallback yfinance, et persiste tout son état (positions,
transactions, thèses, promesses) directement dans ce dépôt GitHub via
l'API Contents (pas de base de données externe).

Vision du propriétaire : faire de ce bot un véritable **gestionnaire
d'actions** qui explique sa stratégie, s'entraîne sur les résultats réels
(et pas seulement sur sa conviction de départ), et donne des conseils
(renforcer / tenir / alléger / sortir) sur un budget de 2000€ réparti
PEA/CTO. Canal de communication : Telegram (pas WhatsApp, confirmé par
l'utilisateur).

## Travaux réalisés dans cette session

### 1. Réconciliation des données du portefeuille
Le portefeuille déployé ne correspondait pas à la réalité (quantités,
PRU et cash erronés, position EXAIL manquante). Corrigé dans
`portfolio.json` et `DEFAULT_PORTFOLIO` :
- EXENS.PA : 2 × 61.20€
- GTT.PA : 2 × 203.20€
- IDL.PA : 1 × 362.50€
- MEDCL.PA : 8 × 28.01€
- EXA.PA : 2 × 74.77€
- Cash : 1.37€

### 2. Bug de prix aberrant (EXAIL.PA à 8273.15€)
Diagnostiqué comme un scraping Boursorama qui touchait le mauvais élément
DOM. Corrigé par un garde-fou `_price_plausible(price, ref)` qui rejette
tout prix hors de 2%–5000% du PRU et bascule sur yfinance, ou affiche
« prix indisponible » plutôt qu'une valeur fausse.

### 3. Cause racine : mauvais ticker
`EXAIL.PA` n'existe pas. Le vrai ticker Euronext Paris pour Exail
Technologies est `EXA.PA` (ISIN FR0000062671). Renommé partout :
`portfolio.json`, `main.py` (positions, codes Boursorama, thèses), et
`data/strategie.md`.

### 4. Création de `data/strategie.md`
Documente les critères de sélection (sous-cotée, projets LT, track
record, innovation, marché porteur — chacun /5, total /25), les règles
d'achat/renforcement/sortie, la thèse détaillée par position, le budget
restant, et un historique des révisions de critères.

### 5. Journal quotidien + suivi des promesses d'entreprise
Répond à la demande : garder une trace jour par jour de pourquoi chaque
action monte ou baisse, et comparer ce qui a été annoncé avec ce qui a
été réellement fait.
- `data/journal.md` : nouveau fichier, alimenté chaque jour ouvré à
  17h40 par `run_daily_journal()` — variation de prix vs la veille +
  jusqu'à 3 actualités récentes par position (scraping Boursorama,
  best-effort, dégrade en « actualité non récupérée » si indisponible).
- `/annonce TICKER texte | YYYY-MM-DD` : enregistre une promesse
  d'entreprise avec échéance.
- `/promesses` : liste les promesses suivies, flague celles dont
  l'échéance est dépassée.
- `/maj_promesse N tenu|manque` : l'utilisateur valide manuellement si
  une promesse a été tenue (vérification automatique non fiable).

### 6. Scores de thèse dynamiques (auto-entraînement)
Les scores /25 de chaque thèse ne sont plus figés dans le code : ils
sont persistés dans `portfolio.json` (clé `theses`) et **ajustés
automatiquement** selon les résultats réels :
- Promesse tenue → score **+1**
- Promesse manquée → score **-2**
- Stop atteint lors de la revue hebdo → score **-3** (une fois par
  franchissement)

Si le score tombe sous 14/25, `/conseil` recommande la sortie même si
le prix est encore correct — la thèse elle-même est jugée invalidée par
les faits, pas seulement le cours. Chaque ajustement est journalisé dans
`data/strategie.md` avec la raison et le score avant/après.

## État actuel des commandes Telegram

| Commande | Rôle |
|---|---|
| `/portfolio`, `/p` | Portefeuille en direct avec P&L |
| `/rapport`, `/r` | Rapport complet immédiat |
| `/conseil`, `/c` | Recommandations renforcer/tenir/alléger/sortir |
| `/strategie`, `/s` | Thèses et scores actuels |
| `/prix TICKER` | Prix d'un titre |
| `/achat TICKER QTY PRIX` | Enregistre un achat |
| `/vente TICKER QTY PRIX` | Enregistre une vente |
| `/annonce TICKER texte \| YYYY-MM-DD` | Logue une promesse d'entreprise |
| `/promesses` | Liste des promesses et leur statut |
| `/maj_promesse N tenu\|manque` | Valide une promesse (ajuste le score) |
| `/help` | Aide |

## Tâches planifiées automatiquement (heure de Paris, lun-ven sauf mention)
- 09h00 / 12h30 / 17h35 : rapports de portefeuille
- 17h40 : journal quotidien (prix + actus)
- Lundi 09h00 : revue hebdomadaire de stratégie (ajuste les scores)
- En continu : alerte Telegram si variation ≥ ±5% sur une position

## Pendant en cours / prochaine étape
L'utilisateur est chez BourseDirect (courtier réel) et veut que le bot
suive son vrai portefeuille. Pas d'API publique BourseDirect disponible ;
méthode retenue : **export CSV/Excel** depuis l'interface BourseDirect,
transmis au bot pour mettre à jour `portfolio.json` (positions réelles,
quantités, PRU).

## Notes techniques
- Persistance : API GitHub Contents (`gh_get`/`gh_put` dans `main.py`),
  pas de base de données.
- Après chaque push de code, un **restart du dyno Heroku** est nécessaire
  pour que le bot prenne en compte les changements.
- Le scraping de news Boursorama (`get_all_news_headlines`) est best-effort
  et peut échouer silencieusement (retourne une liste vide) sans casser
  le journal quotidien.
