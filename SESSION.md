# Résumé de session — Bot Portefeuille Omar (2026-06-16)

## Contexte

Repo : `wesh622/poo` — bot Telegram (`main.py`) qui suit un portefeuille
d'actions Euronext Paris/Xetra (PEA + CTO), récupère les prix via Boursorama
(scraping) avec fallback yfinance, et persiste tout son état (positions,
transactions, thèses, promesses, contrôle d'accès) directement dans ce
dépôt GitHub via l'API Contents (pas de base de données externe).

**Hébergement** : le code et les données vivent sur GitHub ; le bot tourne
en exécution continue sur **Railway** (process `worker: python main.py`
déclaré dans `Procfile`, format Heroku-style mais lu directement par
Railway — pas de config Railway dédiée nécessaire).

Vision du propriétaire : faire de ce bot un véritable **gestionnaire
d'actions** qui explique sa stratégie, s'entraîne sur les résultats réels
(et pas seulement sur sa conviction de départ), et donne des conseils
(renforcer / tenir / alléger / sortir). Canal de communication : Telegram.

## Travaux réalisés dans cette session

### 1. Réconciliation initiale puis sync réelle BourseDirect
Le portefeuille de démonstration (5 positions, ~1265€) a été remplacé par
le **vrai portefeuille BourseDirect de l'utilisateur** (13 positions,
cash 384.69€), exporté en CSV/Excel et synchronisé dans `portfolio.json` :
EXENS.PA, EXA.PA, GTT.PA, IDL.PA, MEDCL.PA (conviction forte, thèses
détaillées) + ALV.DE, PAEEM.PA, CS.PA, AI.PA, MC.PA, RUI.PA, SAN.PA, SU.PA
(diversification/rendement).

### 2. Bug de prix aberrant (EXAIL.PA à 8273.15€) et mauvais ticker
Diagnostiqué comme un scraping Boursorama qui touchait le mauvais élément
DOM, corrigé par un garde-fou `_price_plausible(price, ref)`. Cause
racine : `EXAIL.PA` n'existe pas, le vrai ticker est `EXA.PA` (ISIN
FR0000062671). Renommé partout (code, données, doc).

### 3. `data/strategie.md`
Documente les critères de sélection (/25), les règles d'achat/
renforcement/sortie, une thèse détaillée par position (13 désormais),
le cash disponible, et un historique versionné des révisions (v1 à v1.3).

### 4. Journal quotidien + suivi des promesses d'entreprise
- `data/journal.md` : alimenté chaque jour ouvré à 17h40 — variation de
  prix vs la veille + jusqu'à 3 actualités récentes par position
  (Boursorama, best-effort).
- `/annonce`, `/promesses`, `/maj_promesse` : enregistrer/lister/valider
  les promesses d'entreprise avec échéance.

### 5. Scores de thèse dynamiques (auto-entraînement)
Les scores /25 sont persistés dans `portfolio.json` (clé `theses`) et
ajustés automatiquement : promesse tenue **+1**, promesse manquée **-2**,
stop atteint en revue hebdo **-3** (une fois par franchissement). Sous
14/25, `/conseil` recommande la sortie même si le prix est correct.

### 6. Rapport hebdomadaire du samedi (`/semaine`)
Nouvelle commande + envoi automatique chaque **samedi 10h00 (Paris)** :
variation sur 7 jours (yfinance), prévision par position (objectif/stop/
score de thèse), conseil achat/vente, échéances de promesses à venir
(14 jours), et priorité de renforcement selon le cash disponible.

### 7. Contrôle d'accès multi-niveaux + journal d'accès
Toutes les requêtes Telegram (autorisées ou refusées) sont loguées dans
`data/access_log.md` (heure, identifiant Telegram, requête, statut,
réponse). Quatre niveaux :
- **Owner** : `TELEGRAM_CHAT_ID` (fixe, variable d'env Railway), tous les
  droits, seul à pouvoir gérer `/superuser`.
- **Super-utilisateur** : liste `access.superusers` dans `portfolio.json`,
  gérée uniquement par le owner (`/superuser add|remove|list ID`). Accès
  complet sauf gestion des super-utilisateurs eux-mêmes.
- **Whitelist** : `access.whitelist`, gérée par owner + super-utilisateurs
  (`/whitelist add|remove|list ID`). Accès aux commandes normales.
- **Blacklist** : `access.blacklist`, priorité absolue sur tout le reste
  (`/blacklist add|remove|list ID`).
- `/acces [N]` (owner + super-utilisateurs) : derniers accès au bot.

Pour ajouter un super-utilisateur (ex. Clyde) : il doit d'abord écrire au
bot une fois (son `chat_id` Telegram est alors capturé dans le log), puis
le owner fait `/superuser add <id>` — impossible de l'autoriser via un
numéro de téléphone seul (l'API Telegram Bot ne permet pas cette
résolution).

### 8. Correction d'une régression
Un commit antérieur de cette session (scores de thèse dynamiques) avait
accidentellement écrasé `DEFAULT_PORTFOLIO` et 6 codes Boursorama avec
des données de démonstration obsolètes. Corrigé : positions réelles et
codes Boursorama restaurés, thèses complètes ajoutées pour les 8
positions qui n'en avaient pas (`/conseil` et `/strategie` couvrent
maintenant les 13 positions réelles, plus seulement les 5 d'origine).

## État actuel des commandes Telegram

| Commande | Accès | Rôle |
|---|---|---|
| `/portfolio`, `/p` | tous (whitelist+) | Portefeuille en direct avec P&L |
| `/rapport`, `/r` | tous (whitelist+) | Rapport complet immédiat |
| `/semaine` | tous (whitelist+) | Rapport hebdomadaire (variation 7j, prévisions, conseils) |
| `/conseil`, `/c` | tous (whitelist+) | Recommandations renforcer/tenir/alléger/sortir |
| `/strategie`, `/s` | tous (whitelist+) | Thèses et scores actuels |
| `/prix TICKER` | tous (whitelist+) | Prix d'un titre |
| `/achat TICKER QTY PRIX` | tous (whitelist+) | Enregistre un achat |
| `/vente TICKER QTY PRIX` | tous (whitelist+) | Enregistre une vente |
| `/annonce TICKER texte \| YYYY-MM-DD` | tous (whitelist+) | Logue une promesse d'entreprise |
| `/promesses` | tous (whitelist+) | Liste des promesses et leur statut |
| `/maj_promesse N tenu\|manque` | tous (whitelist+) | Valide une promesse (ajuste le score) |
| `/acces [N]` | owner + super-utilisateurs | Derniers accès au bot |
| `/whitelist add\|remove\|list ID` | owner + super-utilisateurs | Gère les comptes autorisés |
| `/blacklist add\|remove\|list ID` | owner + super-utilisateurs | Gère les comptes bloqués |
| `/superuser add\|remove\|list ID` | owner uniquement | Gère les super-utilisateurs |
| `/help` | tous | Aide (étendue si admin) |

## Tâches planifiées automatiquement (heure de Paris)
- 09h00 / 12h30 / 17h35 (lun-ven) : rapports de portefeuille
- 17h40 (lun-ven) : journal quotidien (prix + actus)
- Lundi 09h00 : revue hebdomadaire de stratégie (ajuste les scores)
- **Samedi 10h00 : rapport hebdomadaire** (`/semaine`)
- En continu : alerte Telegram si variation ≥ ±5% sur une position

## Notes techniques
- Persistance : API GitHub Contents (`gh_get`/`gh_put` dans `main.py`),
  pas de base de données.
- Hébergement d'exécution : **Railway** (pas Heroku, malgré le `Procfile`
  hérité du format Heroku). Après chaque push de code, un redéploiement
  Railway est nécessaire pour que le bot prenne en compte les changements.
- Variables d'environnement requises sur Railway : `TELEGRAM_TOKEN`,
  `TELEGRAM_CHAT_ID`, `GITHUB_TOKEN` (scope `repo`), `GITHUB_REPO`
  (optionnel, défaut `wesh622/poo`), `TZ=Europe/Paris`. Un `GITHUB_TOKEN`
  manquant ou invalide fait retomber silencieusement le bot sur
  `DEFAULT_PORTFOLIO` (portefeuille de démonstration) au lieu du vrai
  portefeuille — déjà rencontré et corrigé dans cette session.
- Le scraping de news Boursorama (`get_all_news_headlines`) est best-effort
  et peut échouer silencieusement (retourne une liste vide) sans casser
  le journal quotidien.
- **Sécurité** : ne jamais committer ni afficher un token/secret (GitHub,
  Telegram) dans un fichier du dépôt ou dans le chat — uniquement via les
  variables d'environnement Railway.
