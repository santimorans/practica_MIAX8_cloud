from matplotlib.pyplot import title
import pandas as pd
import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
from PIL import Image

datos_calls = pd.read_csv('datos_calls.csv')
datos_puts = pd.read_csv('datos_puts.csv')

vencimientos_calls = datos_calls["date"].unique()
vencimientos_puts = datos_puts["date"].unique()

app = dash.Dash(__name__,)

app.title = "App Cloud"

pil_image = Image.open("imagenes/bmelogo.png")

app.layout = html.Div([html.Div(className = "row", children = [html.Img(style = {"margin-left" : "50px", "display": "inline-block"}, src=pil_image), html.H1(style={'textAlign': 'center', "font-size": "50px", "display" : "inline-block", "margin-left" : "300px", "font-family": "Georgia"}, children = "MIAX-8 Tecnologías Cloud")]),
    html.H3(children = "Aplicación Dash", style={'textAlign': 'center','color': "#00008b", "font-family": "Georgia", "marginBottom": "75px"}),
    dcc.Markdown(style = {"font-size": "20px", "marginBottom": "50px", "margin-left" : "50px"}, children = "Selecciona el vencimiento para el tipo de opción correspondiente para ver el skew de volatilidad:"),
    html.Div(className = "row", children = [(dcc.RadioItems(id="tipo_opcion", 
    options=[{"label": "Call", "value": "Call"}, 
    {"label": "Put", "value": "Put"}], inline = True, style = {"marginBottom": "25px"})), 
    dcc.Dropdown(id="vencimiento_opcion")], style = {"font-size": "20px", 'textAlign': 'center', "font-family": "Georgia", "marginBottom": "50px", "margin-left" : "50px", "margin-right" : "50px"}),
    html.Div(dcc.Graph(id= "data-graph"), style = {'width': '100%', 'textAlign': 'center', "font-size": "20px", "font-family": "Georgia", "marginBottom": "50px", "margin-right" : "50px"})])
    

@app.callback(
    Output("vencimiento_opcion", "options"),
    Input("tipo_opcion", "value")
)

def update_options(tipo_opcion):
    if tipo_opcion == "Call":
        list_options = [
            {"label": vencimiento, "value": vencimiento}
            for vencimiento in vencimientos_calls
        ]
    else:
        list_options = [
            {"label": vencimiento, "value": vencimiento}
            for vencimiento in vencimientos_puts
        ]
    return list_options

@app.callback(
    Output("vencimiento_opcion", "value"),
    Input("vencimiento_opcion", "options")
)

def select_first(options):
    return options[0]["value"]

@app.callback(
    Output("data-graph", "figure"),
    State("tipo_opcion", "value"),
    Input("vencimiento_opcion", "value")
)

def update_graph(tipo_opcion, vencimiento_opcion):
    if tipo_opcion == "Call":
        shortlist = datos_calls[datos_calls["date"]==vencimiento_opcion]
        fig = px.line(shortlist, x="strike", y = "volatility", title="Volatility Skew")
    else:
        shortlist_p = datos_puts[datos_puts["date"]==vencimiento_opcion]
        fig = px.line(shortlist_p, x="strike", y = "volatility", title="Volatility Skew")
    return fig.update_layout(title= "Volatility Skew", xaxis_title="Strike Opción", yaxis_title="Volatilidad Implícita", font=dict(family="Georgia",size=14,color="Dark Blue"))

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False, port = 8080)