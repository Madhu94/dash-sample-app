import dash # dash core / dev server
import dash_core_components as dcc # Plotly react components - Graph, Sliders, other widgets
import dash_html_components as html # HTML elements (div, span, p, ..)
import dash_table # Interactive table component
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Output, Input # For use in callbacks for interactivity

df = pd.read_csv("./co2_emissions.csv")
# Pick the latest measurement for each country
latest_data_indices = df.groupby(["country_code", "country_name"]).date.idxmax()
latest_data = df.loc[latest_data_indices]

# This is for identifying which row was clicked
latest_data = latest_data.rename({"country_code": "id"}, axis=1)


table = dash_table.DataTable(data=latest_data.to_dict("records"), 
                             columns=[{"name": col, "id": col} for col in latest_data.columns],
                             style_table={
                                "overflow": "scroll",
                                "maxHeight": 300
                             },
                             id="table")

india_data = df[df["country_code"] == "IND"]

# Create a plotly figure
fig = go.Figure(data=[{
    "x": india_data["date"].tolist(),
    "y": india_data["date"].tolist(),
    "type": "scatter",
    "mode": "lines+markers"
}])
# Graph is a dash wrapper over plotly figures
graph = dcc.Graph(id="graph", figure=fig)

# Adding some plain html components
header = html.H2("CO2 Emissions")

# We will update this footer based on clicked cell in the table
footer = html.P("You clicked nothing", id="text")

# initialize a dash app with a name
app = dash.Dash("co2_emissions")

# layout - a top level dash component that
# describes what the entire application looks like
app.layout = html.Div(children=[header, table, graph, footer])

# Callbacks for interactivity - these must be added after
# setting app.layout
@app.callback(
    # text is id of component we want to update, and we want to
    # set its children attribute in the callback
    Output("text", "children"),
     # If any of these inputs change, the callback will be invoked,
     # table is id of input component and we are waiting for its "active_cell"
     # attribute to change
    [Input("table", "active_cell")]
)
def update_text(active_cell):
    if active_cell:
        country_name = latest_data[latest_data["id"] == active_cell["row_id"]].iloc[0].country_name
        return "You clicked on {0}".format(country_name)
    return "You clicked on nothing"


@app.callback(
    Output("graph", "figure"),
    [Input("table", "active_cell")]
)
def update_graph(active_cell):
    if active_cell:
        data = df[df["country_code"] == active_cell["row_id"]]
        new_fig = go.Figure(fig)
        new_fig.data[0]["x"] = data["date"].tolist()
        new_fig.data[0]["y"] = data["value"].tolist()
        return new_fig
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
    