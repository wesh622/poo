# Stratégie Portefeuille Omar

## Critères de sélection (v1 — juin 2026)

| # | Critère | Description | Poids |
|---|---------|-------------|-------|
| 1 | **Sous-cotée** | Prix < valeur intrinsèque estimée (P/E, P/B, DCF) | /5 |
| 2 | **Projets LT concrets** | Roadmap publique, contrats signés, carnet de commandes visible | /5 |
| 3 | **Track record CT** | Objectifs trimestriels tenus sur ≥ 2 ans consécutifs | /5 |
| 4 | **Innovation / moat** | Brevet, techno propriétaire, barrière à l'entrée forte | /5 |
| 5 | **Marché à fort potentiel** | Secteur en croissance structurelle (défense, santé, énergie, logistique) | /5 |

**Règle d'entrée** : score ≥ 18/25  
**Règle de renforcement** : score ≥ 20/25 ET P&L position < +20%  
**Règle de sortie** : score < 14/25 OU objectif atteint OU stop déclenché  

---

## Apprentissage automatique des scores (v1.2 — juin 2026)

Les scores ne sont plus fixes : ils sont stockés dans `portfolio.json` (clé `theses`) et ajustés automatiquement par le bot selon les résultats réels, pas seulement la conviction initiale :

- **Promesse d'entreprise tenue** (`/maj_promesse N tenu`) → score **+1**
- **Promesse d'entreprise manquée** (`/maj_promesse N manque`) → score **-2**
- **Stop atteint lors de la revue hebdo** → score **-3** (une seule fois par franchissement, pas chaque semaine)

Chaque ajustement est logué ici automatiquement (voir section "Revues hebdomadaires") avec la raison et le score avant/après. Si le score d'une position tombe sous 14/25, `/conseil` recommande la sortie même si le prix est encore correct — la thèse elle-même est jugée invalidée par les faits.

Le **journal quotidien** (`data/journal.md`, 17h40 lun-ven) complète ce mécanisme en gardant une trace jour par jour des mouvements de prix et des actualités récentes de chaque position, pour comparer ce qui a été annoncé avec ce qui s'est réellement passé.

Le **rapport hebdomadaire** (`/semaine`, envoyé chaque samedi 10h00) résume la variation 7 jours, les prévisions issues des thèses et les conseils achat/vente pour l'ensemble du portefeuille.

---

## Positions — conviction forte (PEA, suivi actif)

### EXENS.PA — Exosens
- **Thèse** : Leader vision nocturne/imagerie défense. Commandes record, doublement capacité de production en cours, objectifs T1 2026 tenus.
- **Entrée** : 61.75€ × 2 = 123.50€ (cible allocation : 500€)
- **Objectif** : 95€ · **Stop** : 48€
- **Score** : 22/25 — Sous-cotée ✓ · Projets LT ✓ · Track record ✓ · Innovation ✓ · Marché ✓
- **Action suggérée** : Renforcer progressivement jusqu'à 500€

### EXA.PA — Exail Technologies
- **Thèse** : Drones navals + navigation inertielle. CA +40% T1 2026, carnet commandes > 1 Md€, visibilité 3 ans.
- **Entrée** : 84.09€ × 3 = 252.27€ (cible allocation : 400€)
- **Objectif** : 110€ · **Stop** : 58€
- **Score** : 23/25 — Sous-cotée ✓ · Projets LT ✓ · Track record ✓ · Innovation ✓ · Marché ✓
- **Action suggérée** : Renforcer jusqu'à 400€
- **Note** : ticker boursier réel = `EXA.PA` (ISIN FR0000062671), pas `EXAIL.PA` qui n'existe pas

### MEDCL.PA — MedinCell
- **Thèse** : Biotech injectable longue durée, technologie BEPO® brevetée. Dossier EMA accepté, 2 analystes initient à l'achat.
- **Entrée** : 28.01€ × 8 = 224.08€ (cible allocation : 300€)
- **Objectif** : 45€ · **Stop** : 20€
- **Score** : 20/25 — Sous-cotée ✓ · Projets LT ✓ · Track record ~ · Innovation ✓ · Marché ✓
- **Action suggérée** : Tenir, renforcer légèrement si < 25€

### GTT.PA — GTT
- **Thèse** : Licences méthaniers GNL, marges 60%+, 53 commandes 2026, objectif Bank of America 230€.
- **Entrée** : 204.51€ × 2 = 409.02€ (cible allocation : 300€)
- **Objectif** : 240€ · **Stop** : 170€
- **Score** : 21/25 — Sous-cotée ~ · Projets LT ✓ · Track record ✓ · Innovation ✓ · Marché ✓
- **Action suggérée** : Tenir (légèrement surpondéré vs cible)

### IDL.PA — ID Logistics Group (CTO)
- **Thèse** : Logistique contractuelle, CA +14% T1 2026, croissance vérifiable chaque trimestre depuis 5 ans.
- **Entrée** : 364.94€ × 1 = 364.94€ (cible allocation : 250€)
- **Objectif** : 460€ · **Stop** : 290€
- **Score** : 20/25 — Sous-cotée ✓ · Projets LT ✓ · Track record ✓ · Innovation ~ · Marché ✓
- **Action suggérée** : Tenir (surpondéré, ne pas renforcer)

---

## Positions — diversification / rendement (synchronisées depuis BourseDirect)

Ces 8 positions viennent de l'export réel BourseDirect (13 positions au total, v1.3). Elles ne sont pas des paris de conviction comme les 5 ci-dessus : ce sont des valeurs établies (blue chips, ETF) détenues pour la diversification, le dividende ou la stabilité. Les scores reflètent cette nature — qualité correcte à bonne, mais pas une décote ou un catalyseur de croissance fort.

### AI.PA — L'Air Liquide
- **Thèse** : Leader mondial des gaz industriels, cash-flows récurrents, exposition hydrogène/transition énergétique.
- **Entrée** : 158.25€ × 1 (cible allocation : 200€) · **Objectif** : 190€ · **Stop** : 130€ · **Score** : 19/25

### MC.PA — LVMH
- **Thèse** : Leader du luxe, marques diversifiées, résilience historique. Position déjà large, pas de renforcement visé.
- **Entrée** : 662.52€ × 5 (cible allocation : 3 300€) · **Objectif** : 795€ · **Stop** : 530€ · **Score** : 18/25

### SAN.PA — Sanofi
- **Thèse** : Pharma diversifiée, pipeline vaccins/immunologie, profil défensif, croissance modérée.
- **Entrée** : 86.99€ × 2 (cible allocation : 200€) · **Objectif** : 104€ · **Stop** : 70€ · **Score** : 18/25

### SU.PA — Schneider Electric
- **Thèse** : Leader électrification/efficacité énergétique, exposition data centers et IA, exécution solide.
- **Entrée** : 234.52€ × 1 (cible allocation : 250€) · **Objectif** : 281€ · **Stop** : 188€ · **Score** : 20/25

### ALV.DE — Allianz SE
- **Thèse** : Assureur européen leader, dividende stable. Position rendement/diversification, pas une conviction de croissance.
- **Entrée** : 245.22€ × 1 (cible allocation : 300€) · **Objectif** : 294€ · **Stop** : 196€ · **Score** : 17/25

### CS.PA — AXA
- **Thèse** : Assureur diversifié, valorisation décotée vs pairs, dividende solide, profil value.
- **Entrée** : 27.72€ × 2 (cible allocation : 100€) · **Objectif** : 34€ · **Stop** : 21€ · **Score** : 16/25

### RUI.PA — Rubis
- **Thèse** : Distribution/stockage d'énergie, dividende élevé, diversification géographique, profil value/rendement cyclique.
- **Entrée** : 21.59€ × 3 (cible allocation : 100€) · **Objectif** : 27€ · **Stop** : 16€ · **Score** : 17/25

### PAEEM.PA — Amundi PEA Emergent (MSCI Emerging)
- **Thèse** : ETF de diversification marchés émergents, exposition macro plutôt que stock-picking — pas de catalyseur entreprise individuel à suivre.
- **Entrée** : 31.69€ × 3 (cible allocation : 150€) · **Objectif** : 40€ · **Stop** : 24€ · **Score** : 16/25

---

## Cash disponible
- **Cash** : ~384.69€ (au 16/06/2026)
- **Priorité de déploiement** : déterminée dynamiquement par `/conseil` selon score thèse ≥ 18/25 et écart à la cible d'allocation

---

## Historique des révisions de critères

| Date | Version | Modification | Raison |
|------|---------|--------------|--------|
| 2026-06-09 | v1 | Critères initiaux | Création portefeuille |
| 2026-06-16 | v1.1 | Correction ticker EXAIL.PA → EXA.PA | EXAIL.PA n'existe pas, causait des prix faux/indisponibles |
| 2026-06-16 | v1.2 | Journal quotidien + suivi promesses + scores dynamiques | Le bot doit s'entraîner sur les résultats réels (annonces vs réalisé) plutôt que garder des scores figés |
| 2026-06-16 | v1.3 | Sync réelle BourseDirect (13 positions), thèses + codes Boursorama pour les 8 nouvelles positions, rapport hebdomadaire `/semaine` (samedi 10h) | Le portefeuille réel remplace le portefeuille de démonstration ; `/conseil` et `/strategie` doivent couvrir toutes les positions, pas seulement les 5 d'origine |

---

## Revues hebdomadaires

<!-- Les revues automatiques du bot sont ajoutees ici chaque lundi -->
