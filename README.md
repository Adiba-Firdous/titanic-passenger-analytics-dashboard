# Titanic Passenger Analytics Dashboard

An interactive dashboard built with **Python, Plotly, Dash and pandas**. It lets you filter passenger data by gender and passenger class and explore survival rates.

## Features

- Dash app with a responsive layout
- Gender dropdown: All, Female, Male
- Passenger-class dropdown: All, 1st, 2nd, 3rd
- Passenger, survivor, survival-rate and non-survivor KPI cards
- Interactive survival-rate bar charts by class and gender
- Filter-aware passenger summary table

## Project structure

```text
Titanic_Passenger_Analytics_Dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   └── style.css
└── data/
    └── titanic_cleaned.csv
```

## Requirements

- Python 3.9 or newer
- pip

## Run on Windows (PowerShell or Command Prompt)

Open a terminal inside this project folder and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py app.py
```

If `py` is not recognized, install Python from https://www.python.org/downloads/ and select **Add Python to PATH** during installation. Then reopen the terminal and use `python` in place of `py`.

Open the local address printed in the terminal, usually:

`http://127.0.0.1:8050`

Stop the server with `Ctrl + C`.

## Dataset note

The included `data/titanic_cleaned.csv` is a **synthetic demonstration dataset** created so the dashboard can run immediately without downloading a file. It is not the original Titanic passenger manifest and its metrics must not be presented as historical findings.

To use a real cleaned Titanic dataset, replace this CSV with your dataset while keeping these required columns:

- `PassengerId`
- `Survived` (0 = did not survive, 1 = survived)
- `Pclass` (1, 2 or 3)
- `Sex` (`female` or `male`)

Optional columns such as `Age` and `Fare` are retained if present.

## Troubleshooting

- **ModuleNotFoundError**: activate `.venv` and run `py -m pip install -r requirements.txt`.
- **Dataset not found**: check that `titanic_cleaned.csv` is inside the `data` folder.
- **Port already in use**: stop the other Dash app, or change `app.run(debug=True)` to `app.run(debug=True, port=8051)`.

## GitHub

Create a repository on GitHub, then from this folder run:

```powershell
git init
git add .
git commit -m "Add Titanic passenger analytics dashboard"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```
