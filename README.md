# Partie 2 : Kialo et extraction de relations

Contrôle continu 2 du cours *Argumentation Theory and Applications* (Bruno Yun), M2 IA, Université Claude Bernard Lyon 1.

Cette partie traite :
1. la collecte et l'exploration de 250 débats Kialo
2. la classification de relations Pro/Con entre un argument et son parent, ainsi qu'une expérience de découverte de relations, avec comparaison à la littérature.

## Structure

```
Code/
  01_Scrapping.ipynb       collecte des 250 débats (API Kialo + export texte via Selenium)
  02_EDA.ipynb             parsing des exports, exploration, figures
  03_Preprocessing.ipynb   nettoyage, renvois, langue, paires (parent, enfant), découpage
  04_Models.ipynb          modèles de classification Pro/Con (majoritaire, TF-IDF, DistilBERT)
  05_Decouverte.ipynb      découverte de relations (négatifs aléatoires, TF-IDF)
rawData/kialo/
  kialo-url-ids.csv        identifiants et thèmes des 250 débats
  debates/*.txt            exports bruts Kialo
cleanData/
  parsed/                  arguments_parsed.csv, echecs_parsing.csv
  train.csv val.csv test.csv   paires (parent, enfant) découpées par débat
  suivi.csv                nombre de lignes après chaque étape de préparation
resultats_models/
  metrics.json             scores (validation et test)
  pred_val.csv pred_test.csv   prédictions de DistilBERT
figures/                   figures du rapport (PDF)
```

Les notebooks utilisent des chemins relatifs (`../`) : lancez-les depuis le dossier `Code/`.

## Installation

Python 3.12 ou plus récent est nécessaire.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

La première exécution télécharge depuis Hugging Face le tokenizer `roberta-base` (notebook 02) et le modèle `distilbert-base-uncased` (notebook 04) : une connexion internet est requise.

## Exécution

Les données brutes et nettoyées sont fournies dans l'archive. On peut donc **commencer au notebook 02** (ou 03) sans refaire la collecte. Ordre d'exécution : 01, 02, 03, 04, 05.

| Notebook | Rôle | Durée indicative |
|---|---|---|
| 01 | Collecte | environ 8 min (250 téléchargements) |
| 02 | Parsing et exploration | quelques minutes |
| 03 | Préparation des paires | quelques minutes (détection de langue) |
| 04 | Modèles | environ 30 min d'entraînement DistilBERT sur CPU, puis inférence validation et test |
| 05 | Découverte | environ 2 min |

Pour le notebook 04, exécutez les cellules dans l'ordre. Ne relancez pas la cellule d'entraînement inutilement. Les checkpoints ne sont pas inclus dans l'archive (poids du modèle trop volumineux) ; ils sont recréés dans `resultats_models/checkpoints` à l'entraînement.

### Collecte (notebook 01) : identifiants Kialo

L'export texte de Kialo exige un compte. Le notebook demande l'identifiant et le mot de passe à l'exécution (saisie masquée) : **aucun identifiant n'est stocké dans le code**. Chrome doit être installé ; Selenium récupère le pilote automatiquement.

## Reproductibilité

- Graine 42 pour l'échantillonnage, le découpage et l'entraînement (`set_seed`), graine 0 pour `langdetect`.
- Découpage 70/15/15 **par débat**, pour qu'aucun débat ne soit à cheval entre entraînement, validation et test.
- Les choix d'hyperparamètres sont faits sur la validation, le test sert à l'évaluation finale.
- Entraînement sur CPU, 20 000 paires, une époque, une seule graine : les scores de DistilBERT peuvent varier légèrement d'une machine à l'autre.

## Résultats (classification Pro/Con)

| Modèle | F1 macro (val) | F1 macro (test) | Exactitude (test) |
|---|---|---|---|
| Majoritaire (toujours Pro) | 0,324 | 0,312 | 0,454 |
| TF-IDF + régression logistique (unigrammes) | 0,633 | 0,648 | 0,653 |
| DistilBERT (20 000 paires, 1 époque) | 0,675 | **0,686** | **0,692** |

Découverte de relations (TF-IDF, négatifs tirés au hasard dans le même débat) : F1 macro de 0,497 en validation et 0,496 en test, soit le niveau du hasard. Cette expérience n'applique pas le retrait des doublons du notebook 04, d'où des tailles de découpage légèrement différentes.

## Limites

Calcul limité (CPU, une époque, 20 000 paires sur 63 608), une seule graine, parent immédiat seul comme contexte. Détails dans le rapport.

## Sources

- Outil de collecte inspiré de ADC : <https://github.com/4mbroise/ADC> (`tool/kialo.ipynb`).
- Modèles : `distilbert-base-uncased` (Hugging Face), tokenizer `roberta-base` (analyse des longueurs).
- Bibliothèques : voir `requirements.txt`.
