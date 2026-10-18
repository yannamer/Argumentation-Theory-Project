# ABA Generator

Projet de génération et d’analyse de cadres **ABA** (Assumption-Based Argumentation), avec une variante **ABA+** (préférences entre assumptions).

L’idée est simple : on décrit un cadre en texte (littéraux, assumptions, contraires, règles, éventuellement des préférences), on le valide, on peut le transformer (non-circulaire / atomique), puis on calcule les arguments et les attaques.

---

## Structure du dépôt

```
part-aba/
├── backend/          # cœur logique
│   ├── aba_framework.py   # classes Rule, Argument, ABAFramework
│   ├── parser.py          # lecture du format texte
│   ├── validation.py      # contrôles de cohérence
│   ├── transformations.py # cycles + forme atomique
│   ├── reasoning.py       # arguments + attaques classiques
│   ├── preferences.py     # préférences + attaques normales / inverses
│   ├── api.py             # API FastAPI
│   └── exemples/          # fichiers .aba d’exemple
├── frontend/
│   └── streamlit_app.py   # interface web
├── tests/                 # pytest
└── notebooks/
    └── aba_framework_generator.ipynb
```

---

## Installation

Depuis la racine du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install streamlit fastapi uvicorn pytest
```

(Si le venv existe déjà, active-le juste et tu es bon.)

---

## Lancer l’interface Streamlit

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py
```

Dans l’appli tu peux :

1. Coller un cadre ABA (ou cliquer sur **Charger l’exemple**)
2. Optionnellement cocher **Convertir en non-circulaire** et/ou **Convertir en atomique**
3. **Valider** → vérifie la syntaxe / la cohérence
4. **Analyser** → affiche arguments, préférences, attaques classiques, attaques normales et inverses (ABA+)

---

## Lancer l’API (optionnel)

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --reload
```

Endpoints utiles :

| Méthode | Route | Rôle |
|--------|--------|------|
| GET | `/api/health` | ping |
| GET | `/api/example` | exemple du cours + analyse |
| POST | `/api/parse` | parse un texte `{ "text": "..." }` |
| POST | `/api/validate` | valide un cadre JSON |
| POST | `/api/analyze-text` | parse + analyse (query: `to_non_circular`, `to_atomic`) |
| POST | `/api/analyze` | même chose à partir d’un JSON |

Doc interactive : `http://127.0.0.1:8000/docs`

---

## Format d’un fichier `.aba`

Exemple (`backend/exemples/assignment_exemple.aba`) :

```text
## Literals
L: [a,b,c,q,p,r,s,t]

## Assumptions
A: [a,b,c]

## Contraries
C(a): r
C(b): s
C(c): t

## Rules
[r1]: p <- q,a
[r2]: q <- 
[r3]: r <- b,c
[r4]: t <- p,c
[r5]: s <- t

## Preferences
PREF: a > b
```

Notes :

- Les lignes vides et celles qui commencent par `#` sont ignorées.
- Un fait = règle sans prémisses (`q <-`).
- Les contraires peuvent aussi s’écrire `contrary(a) = r`.
- Les préférences ne portent que sur des **assumptions** (`a > b` veut dire « a est préféré à b »).

---

## Pipeline du projet (dans l’ordre)

### 1. Modèle (`aba_framework.py`)

Un cadre ABA, c’est :

- **L** : ensemble de littéraux  
- **A** ⊆ L : assumptions  
- **contraires** : pour chaque assumption α, un littéral `contrary(α)`  
- **règles** : `conclusion <- premisse1, premisse2, ...`  
- **préférences** (ABA+) : relations entre assumptions  

On a aussi `Rule`, `Argument`, et des méthodes du style `isFlat()`, `summary()`, `to_dict()`.

### 2. Parsing (`parser.py`)

`parse_framework(texte)` lit le format ci-dessus et construit un `ABAFramework`.  
Si une section manque ou qu’une ligne est bizarre → erreurs collectées puis `ValidationError`.

### 3. Validation (`validation.py`)

Contrôles typiques :

- chaque assumption est dans L  
- chaque assumption a un contraire, et ce contraire est dans L  
- pas de contraire défini hors assumptions  
- conclusions / prémisses des règles ∈ L  
- préférences uniquement entre assumptions  

### 4. Transformations (`transformations.py`)

- **Détection de cycles** dans les dépendances (hors assumptions)  
- **`to_non_circular()`** : produit un cadre équivalent sans cycles (littéraux « levelés » du type `p#1`)  
- **`make_atomic()`** : pousse vers une forme atomique (le corps des règles ne contient plus que des assumptions / littéraux traités comme atomiques). Souvent on passe d’abord en non-circulaire, et le cadre doit être *flat*.

Un cadre est **flat** si aucune assumption n’est conclusion d’une règle.

### 5. Raisonnement (`reasoning.py`)

- **`create_arguments`** : construit les arguments `claim ← {assumptions}`  
- **`attacks_classic`** : X attaque Y si la claim de X est le contraire d’une assumption de Y  

### 6. Préférences / ABA+ (`preferences.py`)

Quand X « voudrait » attaquer Y sur α :

- si une assumption de X est **moins préférée** que α → **attaque inverse** (Y attaque X)  
- sinon → **attaque normale** (X attaque Y)  

---

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Ou seulement deux fichiers :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_framework.py tests/test_transformations.py -v
```

Fichiers :

- `test_framework.py` — littéraux, assumptions, contraires, résumé  
- `test_parser.py` — lecture du format texte  
- `test_transformations.py` — cycles / atomique  
- `test_preferences.py` — préférences et attaques ABA+  

---

## Notebook

`notebooks/aba_framework_generator.ipynb` sert à prototypper / illustrer le même flux (création de cadre, transformations, arguments) hors Streamlit.

---

## Petit rappel théorique

En ABA, on argumente à partir d’**assumptions**. Un argument dit : « en acceptant tel ensemble d’assumptions, je dérive telle conclusion via les règles ».  
On attaque un argument en dérivant le **contraire** d’une de ses assumptions.  
Avec ABA+, les préférences peuvent **inverser** le sens de certaines attaques.

C’est exactement ce que le projet calcule et affiche.
