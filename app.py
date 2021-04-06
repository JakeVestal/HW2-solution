# Fetches and displays a basic candlestick app.

import dash
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from hw2_utils import *
from datetime import date, timedelta
from math import ceil
from model import *
from backtest import *

# 4) Create a Dash app
app = dash.Dash(__name__)

# 5) Create the page layout
app.layout = html.Div([
    ##### Intermediate Variables (hidden in divs as JSON) ######################
    ############################################################################
    # Hidden div inside the app that stores IVV historical data
    html.Div(id='ivv-hist', style={'display': 'none'}),
    # Hidden div inside the app that stores bonds historical data
    html.Div(id='bonds-hist', style={'display': 'none'}),
    # Hidden div inside the app that stores model features output
    html.Div(id='features', style={'display': 'none'}),
    # Hidden div inside the app that stores historical model response
    html.Div(id='response', style={'display': 'none'}),
    # Hidden div inside the app that stores the blotter backtest
    html.Div(id='blotter', style={'display': 'none'}),
    # Hidden div inside the app that stores the ledger backtest
    html.Div(id='ledger', style={'display': 'none'}),
    ############################################################################
    ############################################################################

    ##### Parameters ###########################################################
    ############################################################################
    # Date range for update historical data
    dcc.DatePickerRange(
        id='hist-data-range',
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date.today(),
        initial_visible_month=date.today(),
        start_date=date(2021, 3, 16),
        end_date=date.today()
    ),
    # Identifier for what asset to fetch from Bloomberg (IVV US Equity)
    dcc.Input(id='bbg-identifier-1', type = "text", value = "IVV US Equity"),
    # Little 'n': how long for strategy to be profitable? (days)
    dcc.Input(id='lil-n', type = "number", value = 3),
    # Big 'N': How long to train model? (days)
    dcc.Input(id='big-N', type="number", value=5),
    # Alpha: the profitability threshold
    dcc.Input(id="alpha", type="number", value=0.02),
    # lot-size: how many shares to trade?
    dcc.Input(id="lot-size", type="number", value=100),
    ############################################################################
    ############################################################################
    # Display the current selected date range
    html.Div(id='date-range-output'),
    dcc.Graph(id='bonds-3d-graph', style={'display': 'none'}),
    dcc.Graph(id='candlestick', style={'display': 'none'}),
    html.Div(id='proposed-trade'),
    ############################################################################
    ############################################################################

    ##### Buttons ##############################################################
    ############################################################################
    html.Button("RUN BACKTEST", id='run-backtest', n_clicks=0),
    html.Button("PLACE TRADE", id='place-trade', n_clicks=0)
    ############################################################################
    ############################################################################
])
@app.callback(
#### Update Historical Bloomberg Data
    [dash.dependencies.Output('ivv-hist', 'children'),
    dash.dependencies.Output('date-range-output', 'children'),
    dash.dependencies.Output('candlestick', 'figure'),
    dash.dependencies.Output('candlestick', 'style')],
    dash.dependencies.Input("run-backtest", 'n_clicks'),
    [dash.dependencies.State("bbg-identifier-1", "value"),
    dash.dependencies.State('hist-data-range', 'start_date'),
    dash.dependencies.State('hist-data-range', 'end_date')],
    prevent_initial_call = True
)
def update_bbg_data(nclicks, bbg_id_1, start_date, end_date):

    historical_data = req_historical_data(bbg_id_1, start_date, end_date)

    date_output_msg = 'Backtesting from : '

    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        date_output_msg = date_output_msg + 'Start Date: ' + start_date_string

    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        date_output_msg = date_output_msg + 'End Date: ' + end_date_string
    if len(date_output_msg) == len('You have selected: '):
        date_output_msg = 'Select a date to see it displayed here'

    print(historical_data)

    fig = go.Figure(
        data=[go.Candlestick(x=historical_data['Date'],
                                         open=historical_data['Open'],
                                         high=historical_data['High'],
                                         low=historical_data['Low'],
                                         close=historical_data['Close'])]
    )

    return historical_data.to_json(), date_output_msg, fig, {'display': 'block'}


@app.callback(
    [dash.dependencies.Output('bonds-hist', 'children'),
    dash.dependencies.Output('bonds-3d-graph', 'figure'),
    dash.dependencies.Output('bonds-3d-graph', 'style')],
    dash.dependencies.Input("run-backtest", 'n_clicks'),
    [dash.dependencies.State('hist-data-range', 'start_date'),
     dash.dependencies.State('hist-data-range', 'end_date'),
     dash.dependencies.State('big-N', 'value')],
    prevent_initial_call=True
)
def update_bonds_hist(n_clicks, startDate, endDate, N):

    # Need to query enough days to run the backtest on every date in the
    # range start_date to end_date
    startDate = pd.to_datetime(startDate).date() - timedelta(days=ceil(N * 365 / 252))
    startDate = startDate.strftime("%Y-%m-%d")

    data_years = list(
        range(pd.to_datetime(startDate).date().year,
                           pd.to_datetime(endDate).date().year + 1, 1)
    )


    bonds_data = fetch_usdt_rates(data_years[0])

    if len(data_years) > 1:
        for year in data_years[1:]:
            bonds_data = pd.concat([bonds_data, fetch_usdt_rates(year)],
                                    axis = 0, ignore_index=True)

    # How to filter a dataframe for rows that you want
    bonds_data = bonds_data[bonds_data.Date >= pd.to_datetime(startDate)]
    bonds_data = bonds_data[bonds_data.Date <= pd.to_datetime(endDate)]

    fig = go.Figure(
        data=[
            go.Surface(
                z=bonds_data,
                y=bonds_data.Date,
                x=[
                    to_years(cmt_colname) for cmt_colname in list(
                        filter(lambda x: ' ' in x, bonds_data.columns.values)
                    )
                ]
            )
        ]
    )

    fig.update_layout(
        scene=dict(
            xaxis_title='Maturity (years)',
            yaxis_title='Date',
            zaxis_title='APR (%)',
            zaxis=dict(ticksuffix='%')
        ),
        autosize=False,
        width=1500,
        height=500,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    return bonds_data.to_json(), fig, {'display': 'block'}


@app.callback(
    dash.dependencies.Output('features', 'children'),
    dash.dependencies.Input('bonds-hist', 'children'),
    prevent_initial_call = True
)
def calculate_features(bonds):
    return calc_features(bonds)

@app.callback(
    dash.dependencies.Output('response', 'children'),
    [dash.dependencies.Input('ivv-hist', 'children'),
    dash.dependencies.Input('alpha', 'value'),
    dash.dependencies.Input('lil-n', 'value')],
    prevent_initial_call = True
)
def calculate_response(ivv_hist, alpha, n):
    return calc_response(ivv_hist, alpha, n)

@app.callback(
    dash.dependencies.Output('blotter', 'children'),
    [dash.dependencies.Input('features', 'children'),
     dash.dependencies.Input('response', 'children'),
     dash.dependencies.Input('ivv-hist', 'children'),
     dash.dependencies.Input('lil-n', 'value'),
     dash.dependencies.Input('big-N', 'value'),
     dash.dependencies.Input('alpha', 'value'),
     dash.dependencies.Input('lot-size', 'value'),
     dash.dependencies.State('hist-data-range', 'start_date'),
     dash.dependencies.State('hist-data-range', 'end_date')],
    prevent_initial_call = True
)
def calculate_backtest(features, response, ivv_data, n, N, alpha, lot_size,
                       start_date, end_date):
    return backtest(features, response, ivv_data, n, N, alpha, lot_size,
                    start_date, end_date)

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
