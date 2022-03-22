import plotly.graph_objs as go
from plotly.offline import plot
import os
from one_hour_candle_db import OneHourCandleDB
from rsi_divergence_finder import *
from timeframe import TimeFrame
import talib

real_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(real_path)


def plot_rsi_divergence(candles_df, divergences, pair, file_name):
    plot_file_name = os.path.join(os.getcwd(), '{}.html'.format(file_name))
    all_traces = list()

    all_traces.append(go.Scatter(
        x=candles_df['T'].tolist(),
        y=candles_df['C'].values.tolist(),
        mode='lines',
        name='Price'
    ))

    all_traces.append(go.Scatter(
        x=candles_df['T'].tolist(),
        y=candles_df['rsi'].values.tolist(),
        mode='lines',
        name='RSI',
        xaxis='x2',
        yaxis='y2'
    ))

    for divergence in divergences:
        dtm_list = [divergence['start_dtm'], divergence['end_dtm']]
        rsi_list = [divergence['rsi_start'], divergence['rsi_end']]
        price_list = [divergence['price_start'], divergence['price_end']]

        color = 'rgb(0,0,255)' if 'bullish' in divergence['type'] else 'rgb(255,0,0)'

        all_traces.append(go.Scatter(
            x=dtm_list,
            y=rsi_list,
            mode='lines',
            xaxis='x2',
            yaxis='y2',
            line=dict(
                color=color,
                width=2)
        ))

        all_traces.append(go.Scatter(
            x=dtm_list,
            y=price_list,
            mode='lines',
            line=dict(
                color=color,
                width=2)
        ))

    layout = go.Layout(
        title='{} - RSI divergences'.format(pair),
        yaxis=dict(
            domain=[0.52, 1]
        ),
        yaxis2=dict(
            domain=[0, 0.5],
            anchor='x2'
        )
    )

    fig = dict(data=all_traces, layout=layout)
    plot(fig, filename=plot_file_name)


if __name__ == '__main__':
    db_manager = OneHourCandleDB()

    pair = "BTCUSD"
    time_frame = TimeFrame.ONE_DAY

    candles_df = db_manager.get_all_candles_between('Binance_{}'.format(pair),
                                                    datetime(2018, 1, 1),
                                                    datetime(2022, 3, 22),
                                                    aggregate=int(time_frame.value[0] / 60.0))

    candles_df[RSI_COLUMN] = talib.RSI(candles_df[BASE_COLUMN] * 100000, timeperiod=14)
    candles_df.dropna(inplace=True)

    div_df = get_all_rsi_divergences(candles_df, time_frame)

    if len(div_df) > 0:
        plot_rsi_divergence(candles_df,
                            div_df,
                            pair,
                            "{0}_{1}".format(pair, time_frame.value[1]))
    else:
        logging.info('No divergence found')
