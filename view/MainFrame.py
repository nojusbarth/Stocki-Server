from dash import Dash, html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

from data.Stock import Stock
from ml import ModelManager
from ml import Predictor


class MainFrame:

    def __init__(self, stockManager, modelManager):

        self.app = Dash(__name__)
        self.stockManager = stockManager
        self.modelManager = modelManager
        self.predictor = Predictor.Predictor(modelManager=modelManager, stockManager=stockManager)
        self.currentStock = None
        self.predictionClose = None

        self.app.layout = self.initLayout()



        
        @self.app.callback(
            Output("stock-title", "children"),
            Input("search-dropdown", "value")
        )
        def update_title(selected_stock):
            if not selected_stock:
                return "----"
            return self.stockManager.getStock(selected_stock).getName()


        # Callback: aktualisiert den Graph, wenn eine Aktie ausgewaehlt wird oder Tage geaendert werden
        @self.app.callback(
            Output("main-plot", "figure"),
            Input("search-dropdown", "value"),  # ausgewaehlte Aktie
            Input("days-selector", "value"),  # Anzahl der Tage fuer die Anzeige
        )
        def update_plot_on_search(selected_stock, days):
            if not selected_stock:
                return {}


            if self.currentStock is None or self.currentStock.getName() is not selected_stock:
                self.currentStock = self.stockManager.getStock(selected_stock)

                _ , self.predictionClose = self.predictor.predict(self.currentStock.getName(),3)



            return self.createPlot(self.currentStock.getData(), selected_stock, days)



    def initLayout(self):

        return html.Div(
            className="frame",
            children=[

                # Titel des Dashboards
                html.H1("Interaktives Dashboard"),
                html.Div(
                    className="search-title",
                    children=[
                        html.Span("Suche nach Aktien:"),
                    ],
                ),

                # Suchfeld fuer die Aktienauswahl
                html.Div(
                    className="search-dropdown-container",
                    children=[
                        dcc.Dropdown(
                            id="search-dropdown",
                            options=[
                                {"label": s, "value": s}
                                for s in self.stockManager.getStockNames()
                            ],
                            placeholder="Suchbegriff eingeben...",
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                ),

                # Plot-Bereich
                html.Div(
                    className="plot-container",
                    children=[
                        html.Div(
                            className="plot-title",
                            children=[
                                html.Span("", id="stock-title")
                            ],
                        ),
                        dcc.Graph(id="main-plot"),
                    ],
                ),

                # Dropdowns fuer die Auswahl der Daten und Tage
                html.Div(
                    className="plot-data-row",
                    children=[
                        html.Div(
                            className="days-dropdown-container",
                            children=[
                                dcc.Dropdown(
                                    id="days-selector",
                                    options=[
                                        {"label": "Letzte 7 Tage", "value": 7},
                                        {"label": "Letzte 30 Tage", "value": 30},
                                        {"label": "Letzte 90 Tage", "value": 90},
                                        {"label": "Letzte 180 Tage", "value": 180},
                                        {"label": "Letzte 365 Tage", "value": 365},
                                        {"label": "Alle Daten", "value": "all"},
                                    ],
                                    value=30,  # Standard: 30 Tage
                                    clearable=False,
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )


    def createPlot(self, data, stockName, days):

    
        x = data.index.tolist()
        y = data["Close"]



    
        fig = go.Figure()
    
        # 1. Historische Werte (schwarz)
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Historisch",
            line=dict(color="black")
        ))
    
        x_pred = pd.date_range(start=x[-1], periods=len(self.predictionClose)+1, freq="D")
        y_pred = np.concatenate([[y.iloc[-1]], self.predictionClose])

        fig.add_trace(go.Scatter(
            x=x_pred,
            y=y_pred,
            mode="lines",
            name="Vorhersage",
            line=dict(color="red", dash="dash")
        ))
    
        # Globale Grenzen

        x_max = x_pred[-1]
        y_min = min(y.min(), y_pred.min())
        y_max = max(y.max(), y_pred.max())

    
        x_min = x[0]
    
        # Initialer Zoom
        if days is not None and days != "all":
            x_start = x[-days] if len(x) >= days else x_min
        else:
            x_start = x_min
    
        fig.update_layout(
            title=f"Close von {stockName} ueber Zeit",
            xaxis=dict(
                range=[x_start, x_max],
                minallowed=x_min,
                maxallowed=x_max
            ),
            yaxis=dict(
                range=[y_min, y_max],
                minallowed=y_min,
                maxallowed=y_max
            ),
            dragmode="pan"
        )
    
        return fig
    



    def run(self):
        self.app.run(debug=True)