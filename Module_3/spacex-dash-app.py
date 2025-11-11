import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# データ読み込み
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Dashアプリ作成
app = dash.Dash(__name__)

# レイアウト
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # タスク1: ランチサイト選択用ドロップダウン
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True
                 ),
    html.Br(),
    # タスク2: 成功割合パイチャート
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    # タスク3: ペイロード質量範囲選択スライダー
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload,
                    max=max_payload,
                    step=1000,
                    marks={int(min_payload): str(int(min_payload)), int(max_payload): str(int(max_payload))},
                    value=[min_payload, max_payload]
                    ),
    # タスク4: ペイロードと成功率の散布図
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# タスク2 パイチャートのコールバック
@app.callback(
    Output('success-pie-chart', component_property='figure'),
    Input('site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    filtered_df = spacex_df
    if selected_site == 'ALL':
        fig = px.pie(spacex_df[spacex_df['class'] == 1], 
                     names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, 
                     names='class',
                     title=f'Success vs. Failure for site {selected_site}',
                     color='class',
                     color_discrete_map={1: 'green', 0: 'red'})
    return fig

# タスク4 散布図のコールバック
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    fig = px.scatter(filtered_df,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     title='Payload vs. Launch Success correlation',
                     labels={'class': 'Launch Success (1=Success, 0=Failure)'}
                    )
    return fig

# アプリ実行
if __name__ == '__main__':
    app.run(port=8051)
