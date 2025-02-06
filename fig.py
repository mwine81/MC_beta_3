from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import polars as pl
from config import *
from polars import col as c
import plotly.express as px
import polars.selectors as cs

def create_fig_card(id,title):
    return dbc.Card(
        dbc.CardBody([
            html.H4(title,className="fw-bold text-center", style={'color':MCCPDC_PRIMARY}),
            dcc.Graph(id=id),
            ]
        ),className='rounded-4 shadow-lg border-0 mb-5'
    )

def scatter_fig(data):
    data = (
        data
        .group_by(c.generic_name, c.drug_class)
        .agg(c.total.sum(), (c.total.sum() - c.mc_total.sum()).alias('diff'),c.rx_ct.sum(),c.mc_total.sum())
        .with_columns((c.diff / c.rx_ct).alias('avg_diff'))
        .filter(c.diff > 0)
        .filter(c.avg_diff > 0)
        .sql("""select *,
        case when avg_diff < 10 then 1
        when avg_diff <50 then 1
        when avg_diff <100 then 2
        when avg_diff <500 then 4
        when avg_diff <1000 then 8
        when avg_diff <5000 then 16
        else 32 end as size_normalized
        from self""")
        .collect()
    )


    fig = px.scatter(data, y='total', x='diff', size='size_normalized', color='drug_class', log_x=True, log_y=True,
                     hover_data={
                         'generic_name': True,  # Show generic_name in hover data
                         'avg_diff': ':$,.2f',  # Format avg_diff as .2f (two decimal places)
                         'diff': True,  # Keep other fields unchanged
                         'total': True},
                     custom_data=['avg_diff', 'diff', 'total', 'generic_name', 'drug_class','rx_ct','mc_total'],
                     height=400,
                     color_discrete_map=COLOR_MAPPING
                     )
    template = (
        "<b>Drug Name:</b> %{customdata[3]}<br>"
        "<b>Drug Class:</b> %{customdata[4]}<br>"
        "<b>Rx Count:</b> %{customdata[5]:,.0f}<br>"# Rename 'generic_name'
        "<b>Total Charge:</b> %{customdata[2]:$,.0f}<br>"  # Rename and format 'total'
        "<b>MCCPDC Total Charge:</b> %{customdata[6]:$,.0f}<br>"  # Rename and format 'total'
        "<b>Total Charge Difference:</b> %{customdata[1]:$,.0f}<br>"  # Rename and format 'diff'
        "<b>Average Difference Per Rx:</b> %{customdata[0]:$,.2f}<br>"  # Rename and format 'avg_diff'
        "<extra></extra>"  # Hides the default trace info
    )

    fig.update_layout(
        xaxis=dict(tickformat='$.2s'),
        yaxis=dict(tickformat='$.2s'),
        plot_bgcolor="ghostwhite",  # Set plot background color
        paper_bgcolor="white",  # Set outer paper background color
        xaxis_title="<b>MCCPDC Estimated Savings<b>",
        yaxis_title="<b>Total Charge<b>",
        legend_title = '<b>Drug Class<b>',
        showlegend=False,
        title = None
    )
    fig.update_traces(hovertemplate=template)
    return fig


def bar_total_pct_savings(data):
    data = (
        data
        .group_by(c.drug_class)
        .agg(c.total.sum(), (c.total.sum() - c.mc_total.sum()).alias('diff'), c.rx_ct.sum())
        .with_columns((c.diff / c.rx_ct).alias('avg_diff'))
        .filter(c.diff > 0)
        .with_columns((c.diff / c.diff.sum()).alias('diff_pct'))
        .sort(by='diff_pct', descending=True)
        .collect()
    )
    fig = px.bar(data,
                 y='drug_class',
                 x='diff_pct',
                 color='drug_class',
                 orientation='h',
                 text='diff_pct',
                 hover_data={
                     'drug_class': True,
                     'diff': True,  # Keep other fields unchanged
                     'total': True,
                     'rx_ct': True,
                     'avg_diff': ':$,.2f',  # Format avg_diff as .2f (two decimal places)
                 },
                 custom_data=['avg_diff', 'diff', 'total', 'drug_class', 'rx_ct'],
                 height=400,
                 color_discrete_map=COLOR_MAPPING
                 )
    template = (
        "<b>Drug Class:</b> %{customdata[3]}<br>"
        "<b>Rx Count:</b> %{customdata[4]:,.0f}<br>"  # Rename 'generic_name
        "<b>Total Charge Difference:</b> %{customdata[1]:$,.0f}<br>"  # Rename and format 'diff'
        "<b>Total Charge:</b> %{customdata[2]:$,.0f}<br>"  # Rename and format 'total'
        "<b>Average Difference Per Rx:</b> %{customdata[0]:$,.2f}<br>"  # Rename and format 'avg_diff'
        "<extra></extra>"  # Hides the default trace info
    )
    max_x = data.select(c.diff_pct.max()).item()
    fig.update_traces(
        texttemplate='%{text:.1%}',
        textposition='outside',
        hovertemplate=template
    )
    fig.update_layout(
        showlegend=False,
        xaxis=dict(range=[0, max_x * 1.2]),
        xaxis_showticklabels=False,
        plot_bgcolor="white",  # Set plot background color to white
        paper_bgcolor="white",
        yaxis_ticksuffix='  ',
        xaxis_title="",
        yaxis_title="",
    )
    return fig


def avg_charge_per_rx(data):
    data = (
        data
        .group_by(c.drug_class)
        .agg(c.total.sum(), c.mc_total.sum(), (c.total.sum() - c.mc_total.sum()).alias('diff'), c.rx_ct.sum())
        .with_columns((c.diff / c.rx_ct).alias('avg_diff'))
        .filter(c.diff > 0)
        .with_columns((c.diff / c.diff.sum()).alias('diff_pct'))
        .with_columns((c.total / c.rx_ct).alias('avg_charge'), (c.mc_total / c.rx_ct).alias('mc_avg_charge'))
        .sort(by='diff_pct', descending=True)
        .collect()
    )
    data = data.unpivot(index='drug_class', on=['avg_charge', 'mc_avg_charge']).sort(by=['variable', 'value'])
    fig = px.bar(data,
                 y='variable',
                 x='value',
                 color='drug_class',
                 orientation='h',
                 hover_data={
                     'drug_class': True,
                     'value': True,  # Keep other fields unchanged
                 },
                 custom_data=['drug_class', 'value'],
                 height=400,
                 color_discrete_map=COLOR_MAPPING,
                 text_auto=True
                 )
    template = (
        "<b>Drug Class:</b> %{customdata[0]}<br>"
        "<b>Avgerage Rx Price:</b> %{customdata[1]:$,.2f}<br>"  # Rename 'generic_name
        "<extra></extra>"  # Hides the default trace info
    )
    fig.update_traces(
        hovertemplate=template
    )
    y_tick_mapping = {
        "avg_charge": "Avg Charge   ",
        "mc_avg_charge": "MCCPDC Charge   ",
    }
    fig.update_layout(
        showlegend=False,
        # xaxis_showticklabels=False,
        plot_bgcolor="white",  # Set plot background color to white
        paper_bgcolor="white",
        xaxis_title="<b>Avg Charge Per Rx<b>",
        yaxis_title="",
        xaxis=dict(tickformat='$.2s'),
        yaxis=dict(
            tickvals=list(y_tick_mapping.keys()),  # Original labels (keys of the mapping)
            ticktext=list(y_tick_mapping.values())  # Mapped custom labels (values from the mapping)
        )
    )
    return fig
