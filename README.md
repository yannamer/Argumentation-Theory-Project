# Argumentation Theory Project : Contrôle continu 2

Cours *Argumentation Theory and Applications* (INF2347M, Bruno Yun), M2 Informatique parcours IA, Université Claude Bernard Lyon 1. Année 2026-2027.

Ce dépôt réunit le travail d'un groupe de trois étudiants. **Il contient trois parties indépendantes**, une par membre. Chaque partie a son propre dossier, son propre code, ses propres données et son propre README. Il n'y a pas de dépendance entre elles : on peut en exécuter une sans les autres.

## Organisation

| Partie | Sujet | Auteur | Dossier |
|---|---|---|---|
| 1 | Reasoning with ABA : génération et analyse de cadres ABA / ABA+ | Nour Ben Mansour | [`01_Reasoning with ABA/`](01_Reasoning%20with%20ABA/) |
| 2 | Kialo : collecte de débats et extraction de relations (Pro/Con) | Yann Amer | [`02_Relation-based argument mining/`](02_Relation-based%20argument%20mining/) |
| 3 | Visualising acceptability degree spaces for gradual semantics | Antoine Salazar | [`03_Visualising acceptability degree spaces for gradual semantics/`](03_Visualising%20acceptability%20degree%20spaces%20for%20gradual%20semantics/) |

```
.
├── README.md                                                          ce fichier
├── 01_Reasoning with ABA/                                             README, code, tests, interface de la partie 1
├── 02_Relation-based argument mining/                                 README, code, données, résultats de la partie 2
└── 03_Visualising acceptability degree spaces for gradual semantics/  README, notebook de la partie 3
```

## Résumé de chaque partie

**Partie 1 : Reasoning with ABA.** Génération et analyse de cadres ABA (Assumption-Based Argumentation) et ABA+ (préférences entre assumptions) : parsing d’un format texte, validation, transformations (non-circulaire / atomique), calcul des arguments et des attaques (classiques, normales et inverses). Interface Streamlit et API FastAPI ; tests pytest.

**Partie 2 : Kialo.** Collecte des 250 débats les plus actifs de Kialo, parsing et exploration, puis classification de la relation (Pro ou Con) entre un argument et son parent. Meilleur modèle : DistilBERT, F1 macro de 0,686 sur le test, contre 0,648 pour TF-IDF avec régression logistique et 0,312 pour la base majoritaire. Une expérience de découverte de relations (savoir si deux arguments sont liés) reste au niveau du hasard avec TF-IDF.

**Partie 3 : Visualising acceptability degree spaces for gradual semantics.** Implémentation et analyse de la sémantique graduelle h-categorizer pour modéliser l'espace d'acceptabilité d'un cadre d'argumentation. Démonstration, via des simulations Python (enveloppes convexes et heatmaps), que la convergence des scores dépend fondamentalement de la topologie du graphe (densité et structures spécifiques) plutôt que de l'intensité initiale des opinions.

## Utilisation

Chaque partie a ses propres dépendances et ses propres instructions : lisez le README du dossier concerné. Les environnements ne sont pas partagés, créez-en un par partie pour éviter les conflits de versions :

```bash
cd "01_Reasoning with ABA"
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install streamlit fastapi uvicorn pytest
```

```bash
cd Partie2_Kialo
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Livrables

- Rapport PDF commun.
- Archive ZIP avec les notebooks (sorties conservées) et les fichiers de données.
- Rapport de contribution d'une page, signé.

## Répartition du travail

Chaque membre a conçu, écrit et exécuté le code de sa partie. Le détail de la contribution figure dans le rapport de contribution.

## Sources

Le code open source réutilisé est cité dans le README de chaque partie. Pour la partie 2 : <https://github.com/4mbroise/ADC>.
