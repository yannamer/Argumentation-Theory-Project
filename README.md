# Argumentation Theory Project : Contrôle continu 2

Cours *Argumentation Theory and Applications* (INF2347M, Bruno Yun), M2 Informatique parcours IA, Université Claude Bernard Lyon 1. Année 2026-2027.

Ce dépôt réunit le travail d'un groupe de trois étudiants. **Il contient trois parties indépendantes**, une par membre. Chaque partie a son propre dossier, son propre code, ses propres données et son propre README. Il n'y a pas de dépendance entre elles : on peut en exécuter une sans les autres.

## Organisation

| Partie | Sujet | Auteur | Dossier |
|---|---|---|---|
| 1 | [Sujet de la partie 1] | [Nom] | [`Partie1_.../`](Partie1_.../) |
| 2 | Kialo : collecte de débats et extraction de relations (Pro/Con) | Yann Amer | [`Partie2_Kialo/`](Partie2_Kialo/) |
| 3 | [Sujet de la partie 3] | [Nom] | [`Partie3_.../`](Partie3_.../) |

```
.
├── README.md                 ce fichier
├── Partie1_.../              README, code, données, résultats de la partie 1
├── Partie2_Kialo/            README, code, données, résultats de la partie 2
└── Partie3_.../              README, code, données, résultats de la partie 3
```

## Résumé de chaque partie

**Partie 1 : [titre].** [Une ou deux phrases : jeu de données, méthode, résultat principal.]

**Partie 2 : Kialo.** Collecte des 250 débats les plus actifs de Kialo, parsing et exploration, puis classification de la relation (Pro ou Con) entre un argument et son parent. Meilleur modèle : DistilBERT, F1 macro de 0,686 sur le test, contre 0,648 pour TF-IDF avec régression logistique et 0,312 pour la base majoritaire. Une expérience de découverte de relations (savoir si deux arguments sont liés) reste au niveau du hasard avec TF-IDF.

**Partie 3 : [titre].** [Une ou deux phrases.]

## Utilisation

Chaque partie a ses propres dépendances et ses propres instructions : lisez le README du dossier concerné. Les environnements ne sont pas partagés, créez-en un par partie pour éviter les conflits de versions :

```bash
cd Partie2_Kialo
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Livrables

- Rapport PDF commun (15 pages maximum, trois parties).
- Archive ZIP avec les notebooks (sorties conservées) et les fichiers de données.
- Rapport de contribution d'une page, signé.

## Répartition du travail

Chaque membre a conçu, écrit et exécuté le code de sa partie. Le détail de la contribution figure dans le rapport de contribution.

## Sources

Le code open source réutilisé est cité dans le README de chaque partie. Pour la partie 2 : <https://github.com/4mbroise/ADC>.
