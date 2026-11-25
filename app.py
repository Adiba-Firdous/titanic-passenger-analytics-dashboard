from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "titanic_cleaned.csv"

def load_data():
    """Load the cleaned passenger CSV and validate the columns used by the app."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}. Put titanic_cleaned.csv inside the data folder."
        )
    df = pd.read_csv(DATA_FILE)
    required = {"PassengerId", "Survived", "Pclass", "Sex"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    df["Survived"] = pd.to_numeric(df["Survived"], errors="coerce")
    df["Pclass"] = pd.to_numeric(df["Pclass"], errors="coerce")
    df["Sex"] = df["Sex"].astype(str).str.strip().str.lower()
    df = df.dropna(subset=["Survived", "Pclass", "Sex"]).copy()
    df["Survived"] = df["Survived"].astype(int)
    df["Pclass"] = df["Pclass"].astype(int)
    df = df[df["Survived"].isin([0, 1]) & df["Pclass"].isin([1, 2, 3])]
    df["Class"] = df["Pclass"].map({1: "1st Class", 2: "2nd Class", 3: "3rd Class"})
    df["Outcome"] = df["Survived"].map({1: "Survived", 0: "Did not survive"})
    return df

df = load_data()
app = Dash(__name__, title="Titanic Passenger Dashboard")
server = app.server

COLORS = {"navy": "#172554", "blue": "#3B82F6", "teal": "#14B8A6",
          "pink": "#F472B6", "muted": "#64748B", "background": "#F4F7FB"}

def metric_card(label, value, detail):
    return html.Div([
        html.Div(label, className="metric-label"),
        html.Div(value, className="metric-value"),
        html.Div(detail, className="metric-detail")
    ], className="metric-card")

app.layout = html.Div(className="page", children=[
    html.Header(className="topbar", children=[
        html.Div([
            html.Div("TITANIC DATA PROJECT", className="eyebrow"),
            html.H1("Passenger Analytics Dashboard"),
            html.P("Explore passenger survival patterns by gender and ticket class.")
        ]),
        html.Div("INTERACTIVE DASHBOARD", className="header-tag")
    ]),
    html.Main([
        html.Section(className="filters panel", children=[
            html.Div([
                html.Label("Gender", htmlFor="gender-filter"),
                dcc.Dropdown(
                    id="gender-filter",
                    options=[{"label": "All genders", "value": "all"},
                             {"label": "Female", "value": "female"},
                             {"label": "Male", "value": "male"}],
                    value="all", clearable=False
                )
            ], className="filter-control"),
            html.Div([
                html.Label("Passenger class", htmlFor="class-filter"),
                dcc.Dropdown(
                    id="class-filter",
                    options=[{"label": "All classes", "value": "all"},
                             {"label": "1st Class", "value": "1"},
                             {"label": "2nd Class", "value": "2"},
                             {"label": "3rd Class", "value": "3"}],
                    value="all", clearable=False
                )
            ], className="filter-control"),
            html.Div("Change either filter to update all metrics and charts.",
                     className="filter-hint")
        ]),
        html.Section(id="metrics", className="metrics-grid"),
        html.Section(className="charts-grid", children=[
            html.Div(className="panel chart-panel", children=[
                html.H3("Survival rate by passenger class"),
                html.P("Percentage of passengers who survived in each class.", className="chart-subtitle"),
                dcc.Graph(id="class-chart", config={"displayModeBar": False}, responsive=True)
            ]),
            html.Div(className="panel chart-panel", children=[
                html.H3("Survival rate by gender"),
                html.P("Compare survival outcomes for female and male passengers.", className="chart-subtitle"),
                dcc.Graph(id="gender-chart", config={"displayModeBar": False}, responsive=True)
            ])
        ]),
        html.Section(className="panel table-panel", children=[
            html.H3("Passenger summary"),
            html.P("Counts for the currently selected filters.", className="chart-subtitle"),
            html.Div(id="summary-table")
        ]),
        html.Footer("Titanic Passenger Analytics • Built with Python, Plotly and Dash",
                    className="footer")
    ])
])

def empty_figure(message):
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                        showarrow=False, font={"color": COLORS["muted"], "size": 14})
    fig.update_layout(template="plotly_white", height=320, margin=dict(l=20, r=20, t=20, b=20))
    return fig

@app.callback(
    Output("metrics", "children"),
    Output("class-chart", "figure"),
    Output("gender-chart", "figure"),
    Output("summary-table", "children"),
    Input("gender-filter", "value"),
    Input("class-filter", "value")
)
def update_dashboard(gender, passenger_class):
    filtered = df.copy()
    if gender != "all":
        filtered = filtered[filtered["Sex"] == gender]
    if passenger_class != "all":
        filtered = filtered[filtered["Pclass"] == int(passenger_class)]

    total = len(filtered)
    survived = int(filtered["Survived"].sum()) if total else 0
    rate = (survived / total * 100) if total else 0
    cards = [
        metric_card("PASSENGERS", f"{total:,}", "Matching current filters"),
        metric_card("SURVIVED", f"{survived:,}", "Passengers who survived"),
        metric_card("SURVIVAL RATE", f"{rate:.1f}%", "Survivors as a share of passengers"),
        metric_card("DID NOT SURVIVE", f"{total-survived:,}", "Passengers who did not survive")
    ]

    if total:
        by_class = (filtered.groupby("Class", as_index=False)
                    .agg(survival_rate=("Survived", "mean"), passengers=("PassengerId", "count")))
        by_class["survival_rate"] *= 100
        class_fig = px.bar(by_class, x="Class", y="survival_rate", text="survival_rate",
                           color="Class", color_discrete_sequence=["#3B82F6", "#14B8A6", "#F59E0B"],
                           hover_data={"passengers": True, "survival_rate": ":.1f"})
        class_fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                cliponaxis=False, marker_line_width=0)
        class_fig.update_layout(showlegend=False, yaxis_title="Survival rate (%)",
                                xaxis_title="", yaxis=dict(range=[0, 110]),
                                template="plotly_white", height=320,
                                margin=dict(l=20, r=20, t=20, b=20),
                                font=dict(family="Arial", color="#334155"))

        by_gender = (filtered.groupby("Sex", as_index=False)
                     .agg(survival_rate=("Survived", "mean"), passengers=("PassengerId", "count")))
        by_gender["Gender"] = by_gender["Sex"].str.title()
        by_gender["survival_rate"] *= 100
        gender_fig = px.bar(by_gender, x="Gender", y="survival_rate", text="survival_rate",
                            color="Gender", color_discrete_map={"Female": "#F472B6", "Male": "#3B82F6"},
                            hover_data={"passengers": True, "survival_rate": ":.1f"})
        gender_fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                 cliponaxis=False, marker_line_width=0)
        gender_fig.update_layout(showlegend=False, yaxis_title="Survival rate (%)",
                                 xaxis_title="", yaxis=dict(range=[0, 110]),
                                 template="plotly_white", height=320,
                                 margin=dict(l=20, r=20, t=20, b=20),
                                 font=dict(family="Arial", color="#334155"))
    else:
        class_fig = empty_figure("No passengers match these filters.")
        gender_fig = empty_figure("No passengers match these filters.")

    summary = (filtered.groupby(["Class", "Sex"], as_index=False)
               .agg(Passengers=("PassengerId", "count"), Survivors=("Survived", "sum")))
    if not summary.empty:
        summary["Survival rate"] = (summary["Survivors"] / summary["Passengers"] * 100).map(lambda x: f"{x:.1f}%")
        table = html.Table([
            html.Thead(html.Tr([html.Th("Class"), html.Th("Gender"),
                                html.Th("Passengers"), html.Th("Survivors"), html.Th("Survival rate")])),
            html.Tbody([
                html.Tr([html.Td(row["Class"]), html.Td(row["Sex"].title()),
                         html.Td(f'{row["Passengers"]:,}'), html.Td(f'{row["Survivors"]:,}'),
                         html.Td(row["Survival rate"])])
                for _, row in summary.iterrows()
            ])
        ], className="data-table")
    else:
        table = html.P("No data available for the selected filters.", className="empty-state")

    return cards, class_fig, gender_fig, table

if __name__ == "__main__":
    app.run(debug=True)
