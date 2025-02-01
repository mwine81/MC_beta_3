from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import polars as pl
from config import *
from polars import col as c
import plotly.express as px
import polars.selectors as cs


#FIG1 PLOT
def fig_drug_group_fig(data,how):
    data = (
        data
        .group_by('drug_class')
        .agg(c.total.sum(),c.mc_total.sum(),c.rx_ct.sum())
        .with_columns((c.total - c.mc_total).alias('diff'))
        .with_columns((c.diff / c.rx_ct).alias('per_rx'))
        .with_columns(c.drug_class.replace(GROUP_DICT))
        .collect()
    )
    fig = px.pie(
        data,
        values=how,
        names="drug_class",
        hole=.7,
    )
    return fig

def create_fig(id):
    return dbc.Card(
        dbc.CardBody([
            html.H4('Title',className="fw-bold text-center"),
            html.Div(id=id),
            ]
        ),className='rounded-4 shadow-lg border-0 mb-5'
    )

FIG1 = create_fig('graph1')

#FIG2 Plot
def top_saving_drugs(data,n_drugs,how):
    #rk = TOP_SAVINGS_DICT.get(rank_by)
    #sort_col = 'per_rx' if rk == 'per_rx' else 'diff'
    data = (
        data
        .group_by(c.generic_name)
        .agg(c.total.sum(), c.mc_total.sum(),c.rx_ct.sum())
        .with_columns((c.total - c.mc_total).alias('diff'))
        .with_columns((c.diff / c.rx_ct).alias('per_rx'))
        .sort(how, descending=True)
        .head(int(n_drugs))
        .sort(by=how)
        .collect()
    )

    fig = px.bar(
        data,
        y="generic_name",
        x=how,
        #title=f"MCCPDC Savings - Top 10 Drugs by Total Savings($)",
        orientation="h",
        barmode="group",
        #text_auto=True,
        text=data[how],
        color_discrete_sequence=[MCCPDC_PRIMARY],
    )
    fig.update_traces(texttemplate="%{text:$,.0f}",)
    fig.update_layout(
        showlegend=False,
        height=50*int(n_drugs),
    )
    fig.update_xaxes(
        # tickformat="$,.0f",
        showticklabels=False,
        title = '',
    )
    fig.update_yaxes(
        title = '',
        ticksuffix='    '
    )
    return fig

#FIG 2 CARD
FIG2 = create_fig('graph2')

#FIG3 Calc
def fig_monthly_spend(data,nadac_fee):

    data = (
        data
        .filter(c.nadac.is_not_null())
        .group_by(pl.date(c.year, c.month, 1).alias('dos'))
        .agg(cs.contains('total', 'rx_ct', 'nadac', 'mc_total').sum())
        .with_columns(((c.rx_ct * int(nadac_fee)) + c.nadac).alias('nadac'))
        .sort(c.dos)
    )
    fig = px.line(data.collect(),
                  x='dos',
                  y=['total', 'mc_total', 'nadac'],
                  line_shape='spline',
                  color_discrete_map={'mc_total':MCCPDC_PRIMARY,'nadac':MCCPDC_SECONDARY,'total':MCCPDC_ACCENT}
                  )
    fig.update_layout(
        plot_bgcolor = 'white',
        legend=dict(
        title='',
        orientation="h",  # Set legend orientation to horizontal
        x=.1,  # Set the x-position of the legend (centered)
        xanchor="center",  # Anchor the legend at the center
        y=1.2,  # Adjust the y-position (above the plot)
    )
                      )
    fig.update_traces(
        line=dict(width=4),
        opacity=0.60,
    )
    fig.update_xaxes(title='')
    fig.update_yaxes(title='Spend($)')

    return fig


FIG3 = create_fig('graph3')



