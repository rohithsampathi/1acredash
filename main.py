import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import plotly.graph_objs as go

# Load the data
ads_data = pd.read_excel("1acrebgr.xlsx", sheet_name='ADs')
telangana_data = pd.read_excel("1acrebgr.xlsx", sheet_name='Telangana')
ap_data = pd.read_excel("1acrebgr.xlsx", sheet_name='AP')

# Initialize the app with suppressed callback exceptions
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Theme settings
theme = {
    'bg': '#f5f5f5', 'card_bg': '#fff', 'text': '#333', 'border': '#ddd',
    'header': '#6200ea', 'accent': '#6200ea', 'positive': '#00c853', 'negative': '#d50000'
}

# Generate controls
def generate_controls(include_state=True):
    controls = []
    if include_state:
        controls.append(dcc.Dropdown(id='state-dropdown', options=[
            {'label': 'Andhra Pradesh', 'value': 'AP'}, {'label': 'Telangana', 'value': 'Telangana'}],
            value='AP', clearable=False, style={'width': '50%', 'margin': '0 auto'}))
    controls.append(dcc.DatePickerRange(id='date-range-picker', min_date_allowed=ads_data['Date'].min(),
                                        max_date_allowed=ads_data['Date'].max(), start_date=ads_data['Date'].min(),
                                        end_date=ads_data['Date'].max(), display_format='YYYY-MM-DD',
                                        style={'padding': '10px', 'backgroundColor': theme['card_bg'],
                                               'color': theme['text'], 'border': f"1px solid {theme['border']}",
                                               'borderRadius': '5px'}))
    return html.Div(controls, style={'textAlign': 'center', 'marginBottom': '30px'})

# Generate summary cards
def generate_summary_cards(state, start_date, end_date):
    data = ap_data if state == 'AP' else telangana_data
    filtered = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
    if filtered.empty:
        return [html.Div("No data available for the selected date range.", style={'color': theme['negative'], 'padding': '20px'})]

    start, end = filtered.iloc[0], filtered.iloc[-1]
    return [create_card(channel, end[channel], start[channel]) for channel in ['LinkedIn', 'Twitter', 'Instagram', 'Facebook']]

# Create individual summary card
def create_card(channel, value, start_value):
    change = ((value - start_value) / start_value) * 100 if start_value != 0 else 0
    color = theme['positive'] if change > 0 else theme['negative']
    return html.Div([
        html.H4(channel, style={'marginBottom': '10px', 'color': theme['header']}),
        html.H2(f"{value}", style={'marginBottom': '0px', 'color': theme['text']}),
        html.P(f"{change:.2f}%", style={'marginTop': '5px', 'color': color, 'fontSize': '14px'})
    ], id={'type': 'channel-card', 'index': channel}, n_clicks=0, style={
        'backgroundColor': theme['card_bg'], 'padding': '20px', 'borderRadius': '10px',
        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'width': '200px', 'textAlign': 'center',
        'border': f"1px solid {theme['border']}", 'cursor': 'pointer'})

# Generate line chart
def generate_line_chart(data, campaigns, metrics, title):
    traces = [
        go.Scatter(x=data['Date'], y=data[metric], mode='lines+markers', marker=dict(symbol='diamond', size=6),
                   name=f"{campaign} - {metric}", line=dict(width=2))
        for campaign in campaigns for metric in metrics if not data.empty]
    return {'data': traces, 'layout': go.Layout(title=title, xaxis={'title': 'Date'}, yaxis={'title': 'Metric Value'},
                                                paper_bgcolor=theme['bg'], plot_bgcolor=theme['bg'], hovermode='closest')}

# Generate tab content
def generate_tabs_content(tab):
    if tab == 'followers-tab':
        return html.Div([generate_controls(include_state=True), html.Div(id='summary-cards', style={
            'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '15px'}),
            html.H2("Social Channel Follower Trends", style={'marginTop': '40px', 'textAlign': 'center', 'color': theme['header']}),
            dcc.Graph(id='follower-line-chart')])
    elif tab == 'campaign-tab':
        return html.Div([generate_controls(include_state=False),
            html.H2("Paid Campaign Performance", style={'marginTop': '40px', 'textAlign': 'center', 'color': theme['header']}),
            dcc.Dropdown(id='campaign-dropdown', options=[{'label': name, 'value': name} for name in ads_data['Campaign name'].unique()],
                         multi=True, style={'width': '80%', 'margin': '0 auto', 'padding': '10px'}),
            dcc.Dropdown(id='metric-dropdown', options=[{'label': metric, 'value': metric} for metric in [
                'Sales', 'Checkouts', 'Clicks', 'Leads', 'Reach', 'Impressions', 'Cost per results', 'Amount spent (INR)']],
                         multi=True, style={'width': '80%', 'margin': '0 auto', 'padding': '10px'}),
            dcc.Graph(id='line-chart')])

# App layout
app.layout = html.Div(style={'backgroundColor': theme['bg'], 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1("Strategy Genesis Panel", style={'textAlign': 'center', 'padding': '20px', 'color': theme['header'], 'marginBottom': '30px'}),
    dcc.Tabs(id="tabs", value='followers-tab', children=[
        dcc.Tab(label='Followers', value='followers-tab', style={'padding': '10px'}, selected_style={'padding': '10px', 'backgroundColor': theme['accent'], 'color': theme['card_bg']}),
        dcc.Tab(label='Paid Campaign Analysis', value='campaign-tab', style={'padding': '10px'}, selected_style={'padding': '10px', 'backgroundColor': theme['accent'], 'color': theme['card_bg']}),
    ], style={'marginBottom': '20px'}),
    html.Div(id='tabs-content')
])

# Callbacks
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    return generate_tabs_content(tab)

@app.callback(Output('summary-cards', 'children'), [Input('state-dropdown', 'value'), Input('date-range-picker', 'start_date'), Input('date-range-picker', 'end_date')])
def update_summary_cards(state, start_date, end_date):
    return generate_summary_cards(state, start_date, end_date)

@app.callback(Output('line-chart', 'figure'), [Input('campaign-dropdown', 'value'), Input('metric-dropdown', 'value'), Input('date-range-picker', 'start_date'), Input('date-range-picker', 'end_date')])
def update_line_chart(campaigns, metrics, start_date, end_date):
    data = ads_data[(ads_data['Campaign name'].isin(campaigns or [])) & (ads_data['Date'] >= start_date) & (ads_data['Date'] <= end_date)]
    return generate_line_chart(data, campaigns or [], metrics or [], "Paid Campaign Performance")

@app.callback(Output('follower-line-chart', 'figure'), [Input({'type': 'channel-card', 'index': ALL}, 'n_clicks')], 
              [State('state-dropdown', 'value'), State('date-range-picker', 'start_date'), State('date-range-picker', 'end_date')])
def update_follower_line_chart(n_clicks_list, state, start_date, end_date):
    triggered = [i for i, n in enumerate(n_clicks_list) if n > 0]
    if not triggered:
        return {}
    channels = ['LinkedIn', 'Twitter', 'Instagram', 'Facebook']
    data = (ap_data if state == 'AP' else telangana_data)[(ap_data['Date'] >= start_date) & (ap_data['Date'] <= end_date)]
    return generate_line_chart(data, [channels[i] for i in triggered], ['Number of Followers'], "Follower Trends Over Time")

if __name__ == '__main__':
    app.run_server(debug=True)