from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from config import *
from calc import *
from fig import *
import polars as pl
from polars import col as c
from datetime import date


app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.BOOTSTRAP,dbc.icons.FONT_AWESOME],assets_folder='assets')
server = app.server

def kpi_card(name,value,text_color):
    return dbc.Col(
    dbc.Card(
    dbc.CardBody([
        html.H3(value,className="fw-bold text-center",style={'color':text_color}),
        html.P(name,className="text-muted text-center"),
        ]
    ),className='rounded-4 shadow-lg border-0 mb-5'
    )
    )

navi = html.Div(
        html.Div([
            html.A(
                html.Img(src=app.get_asset_url
                ('img.png'),alt='logo',className='ps-3')
                ,href='index.html',className='navbar-brand'),
            ]
            )
        ,className="navbar", style={'background-color': MCCPDC_SECONDARY}
)

footer = html.Footer(
            html.A(
                html.Img(src=app.get_asset_url
                ('img_1.png'),alt='logo', height='100px')
                ,href='index.html',className='px-4'),
           className='mb-4')

def group_select(name,**kwargs):
    return html.Div([
        dbc.Col(
            html.P(f'{name}',className="mb-0"),style=({'font-size':'12px'}),width=4
        ),
        dbc.Col(
    dcc.Dropdown(**kwargs,style={'font-size':'12px'}),width=8
        )
    ],className='hstack gap-1 mb-1')

date_selector = html.Div([
    dbc.Col(
    html.P('Date Range',className="text-bold mb-0",style={'font-size':'12px'}),width=3
    ),
    dbc.Col(
    dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=date(2023, 1, 1),
                max_date_allowed=date(2024, 12, 31),
                end_date=date(2024, 12, 31),
                start_date=date(2023, 1, 1),),width=9
    )],
    className='hstack gap-1 mb-1')


#controls
controls = dbc.Card(
    dbc.CardBody([
        html.H4('Controls',className="text-center"),
        dbc.Row([
            date_selector,
            group_select('Date Sets', options=get_files(), multi=True, id='data-set'),
            group_select('Drug Class', id='drug-class-group', multi=True),

            group_select('Affiliated', options={'All': 'All', True: 'Affiliated', False: 'Non-Affiliated'},
                         value='All', id='affiliated-group', clearable=False),
            group_select('Specialty', options={'All': 'All', True: 'Specialty', False: 'Non-Specialty'}, value='All',
                         id='specialty-group', clearable=False),
            group_select('FTC Generic', options={'All': 'All', True: 'FTC', False: 'Non-FTC'}, id='ftc-group',
                         value='All',
                         clearable=False),
        ]),
    ],className='rounded-4 shadow-lg border-0 mb-5')
    ,className='border-0')


app.layout = html.Div([
    navi,
    dbc.Container([
        dbc.Row(
            dbc.Col(dbc.Row(id='kpi-row',className="mt-4"))
        ),
        dbc.Row([
            html.Div(controls,className='col-4'),
            html.Div(FIG4,className='col-8')
        ],align='center'),
        dbc.Row([
            dbc.Col(FIG5,className='col-5'),
            dbc.Col(FIG6,className='col-7'),
        ]),
    ],
    fluid=True),
    footer
])

ALL_VALUE = 'All'  # Introduced constant for reused string

def filter_data(data_set_list, affiliated_group, specialty_group,ftc_group, date_start=None, date_end=None,
                drug_class_list=None):
    data = load_files(data_set_list)
    if date_start and date_end:
        start, end = [int(x) for x in date_start.split('-')], [int(x) for x in date_end.split('-')]
        data = data.filter(c.dos.is_between(pl.date(start[0], start[1], start[2]), pl.date(end[0], end[1], end[2])))
    if affiliated_group != ALL_VALUE:
        data = data.filter(c.affiliated == affiliated_group)
    if specialty_group != ALL_VALUE:
        data = data.filter(c.is_special == specialty_group)
    if drug_class_list:
        data = data.filter(c.drug_class.is_in(drug_class_list))
    if ftc_group != ALL_VALUE:
        data = data.filter(c.is_ftc == ftc_group)
    return data

@app.callback(
    Output('drug-class-group', 'options'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_control_group_options(data_set_list, affiliated_group, specialty_group,ftc_group,date_start, date_end):
    data = filter_data(data_set_list = data_set_list,affiliated_group= affiliated_group,specialty_group= specialty_group,ftc_group=ftc_group, date_start=date_start, date_end=date_end)
    drug_group_options = data.select(c.drug_class).unique().sort(c.drug_class).collect().to_series().to_list()
    return drug_group_options

@app.callback(
    Output('kpi-row','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),

    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_kpis(data_set_list,affiliated_group,specialty_group,ftc_group, drug_class_list,date_start,date_end):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,date_start=date_start, date_end=date_end)
    data_dict = dict_for_kpis(data)
    KPIS = [
        kpi_card('Total', f'{"${:,.0f}".format(data_dict["total"][0])}',MCCPDC_PRIMARY),
        kpi_card('MCCPDC', f'{"${:,.0f}".format(data_dict.get("mc_total")[0])}',MCCPDC_PRIMARY),
        kpi_card('Rx Ct', f'{"{:,}".format(data_dict.get("rx_ct")[0])}',MCCPDC_PRIMARY),
        kpi_card('Estimated Savings', f'{"${:,.0f}".format(data_dict.get("mc_diff")[0])}', MCCPDC_ACCENT),
        kpi_card('Savings Per Rx', f'{"${:,.2f}".format(data_dict.get("per_rx")[0])}',MCCPDC_ACCENT),
        kpi_card('Savings Percent', f'{"{:,.0%}".format(data_dict.get("diff_pct")[0])}', MCCPDC_ACCENT),
    ]
    return KPIS

@app.callback(
    Output('graph4','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),

    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_graph1(data_set_list,affiliated_group,specialty_group,ftc_group,drug_class_list,date_start,date_end):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=scatter_fig(data))
    return fig

@app.callback(
    Output('graph5','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),

    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_graph1(data_set_list,affiliated_group,specialty_group,ftc_group,drug_class_list,date_start,date_end):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=bar_total_pct_savings(data))
    return fig

@app.callback(
    Output('graph6','children'),
    Input('data-set', 'value'),
    Input('affiliated-group', 'value'),
    Input('specialty-group', 'value'),
    Input('ftc-group', 'value'),
    Input('drug-class-group', 'value'),

    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_graph1(data_set_list,affiliated_group,specialty_group,ftc_group,drug_class_list,date_start,date_end):
    data = filter_data(data_set_list=data_set_list, affiliated_group=affiliated_group, specialty_group=specialty_group,ftc_group=ftc_group,
                       drug_class_list=drug_class_list,date_start=date_start, date_end=date_end)

    fig = dcc.Graph(figure=avg_charge_per_rx(data))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)