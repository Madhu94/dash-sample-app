import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html 
from dash.dependencies import Output, Input
import plotly.graph_objects as go

import numpy as np
import pandas as pd


df = pd.read_csv('./co2_emissions.csv')
latest_data = df.loc[df.groupby(["country_code", "country_name"]).date.idxmax()]
latest_data = latest_data.rename({"country_code": "id"}, axis=1)

header = html.H2("CO2 Emissions per Country in metric tons/capita")

columns = []
for column in latest_data.columns:
    col_name = "country_code" if column == "id" else column
    columns.append({"name": col_name, "id": column})

table = dash_table.DataTable(id="emissions-table",
                             columns=columns,
                             data=latest_data.to_dict("records"),
                             style_table={
                                 "overflowY": "scroll",
                                 "maxHeight": 400
                             })

layout = {"margin": dict(r=0, l=100, b=0, t=0)}

figure = go.Figure(data=[
    {    
        "x": df[df["country_code"] == "IND"]["date"].tolist(),
        "y": df[df["country_code"] == "IND"]["value"].tolist(),
        "type": "scatter",
        "mode": "lines+markers"
    }
], layout=layout)

graph = dcc.Graph(id="emissions-timeseries", figure=figure)

text = html.P(id="footer")

app = dash.Dash("co2_emissions")


content = html.Div(children=[table, graph], style={"display": "flex", "justifyContent": "center", "height": "400px"})
app.layout = html.Div(children=[header, content, text])

@app.callback(
    Output("emissions-timeseries", "figure"),
    [Input("emissions-table", "active_cell")]
)
def update_graph(selected_cell):
    if selected_cell:
        code = selected_cell["row_id"]
        new_data = df[df["country_code"] == code]
        new_fig = go.Figure(figure)
        new_fig.data[0].y = new_data["value"].tolist()
        return new_fig
    return figure

@app.callback(
    Output("footer", "children"),
    [Input("emissions-table", "active_cell")]
)
def update_text(selected_cell):
    if selected_cell:
        code = selected_cell["row_id"]
        new_data = df[df["country_code"] == code].iloc[0].country_name
        return "You clicked on {0}".format(new_data)
    return "nothing!"


if __name__ == "__main__":
    app.run_server(debug=True)
    