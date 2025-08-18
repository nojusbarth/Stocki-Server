from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

from model.Stock import Stock


class MainFrame:

    def __init__(self, stockManager):

        self.app = Dash(__name__)
        self.stockManager = stockManager
        self.currentStock = stockManager.getStock("AAPL")

        self.app.layout = self.initLayout()



        
        @self.app.callback(
            Output("stock-title", "children"),
            Input("search-dropdown", "value")
        )
        def update_title(selected_stock):
            if not selected_stock:
                return "----"
            return self.stockManager.getStock(selected_stock).getName()


        # Callback: aktualisiert den Graph, wenn eine Aktie ausgewaehlt wird oder Kategorie geaendert wird, oder Tage geaendert werden
        @self.app.callback(
            Output("main-plot", "figure"),
            Input("search-dropdown", "value"),  # ausgewaehlte Aktie
            Input("data-column-selector", "value"),  # aktuelle Kategorie
            Input("days-selector", "value"),  # Anzahl der Tage fuer die Anzeige
        )
        def update_plot_on_search(selected_stock, category, days):
            if not selected_stock or not category:
                return {}

            self.currentStock = self.stockManager.getStock(selected_stock)


            return self.createPlot(self.currentStock.getData(), selected_stock, category, days)



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
                                html.Span(self.currentStock.getName(), id="stock-title")
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
                            className="data-dropdown-container",
                            children=[
                                dcc.Dropdown(
                                    id="data-column-selector",
                                    options=[
                                        {"label": col, "value": col}
                                        for col in self.currentStock.getData().columns
                                    ],
                                    value="Close",
                                    clearable=False,
                                )
                            ],
                        ),
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


    def createPlot(self, data, stockName, category, days):
        x = data.index.tolist()
        y = data[category]
        
        fig = px.line(
            x=x,
            y=y,
            labels={"x": "Zeit", "y": category},
            title=f"{category} von {stockName} ueber Zeit",
        )
        

        # Globale Grenzen (nicht ueberschreitbar)
        x_min, x_max = x[0], x[-1]
        y_min, y_max = y.min(), y.max()

        # Initialer Zoom basierend auf 'days'
        if days is not None and days != "all":
            x_start = x[-days] if len(x) >= days else x_min
        else:
            x_start = x_min

        fig.update_layout(
            dragmode='pan',

            xaxis=dict(
                range=[x_start, x_max],    # aktueller sichtbarer Bereich
                minallowed=x_min,          # links nicht weiter verschieben
                maxallowed=x_max,          # rechts nicht weiter verschieben
            ),
            yaxis=dict(
                range=[y_min, y_max],
                minallowed=y_min,
                maxallowed=y_max
            )
        )

        return fig



    def run(self):
        self.app.run(debug=True)