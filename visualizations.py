"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Python implementation of cross exchange market-making (XEMM)                               -- #
# -- script: functions.py: python script with general functions                                          -- #
# -- author: MoyMFO, AndresLaresBarragan, Miriam1999                                                     -- #
# -- license: GPL-3.0 license                                                                            -- #
# -- repository: https://github.com/AndresLaresBarragan/MyST_XEMM                                        -- #                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
class XemmVisualization:

    @staticmethod
    def orderbook_history(data: dict) -> go.Figure:

        def __ob_melt(data: pd.DataFrame ):
            bid = data[['bid_size','bid']]
            bid['bid_flag'] = ['bid']*bid.shape[0]
            bid.rename(columns={'bid_size':'size',
                                    'bid':'price',
                                    'bid_flag':'type'}, inplace=True)

            ask = data[['ask_size','ask']]
            ask['ask_flag'] = ['ask']*ask.shape[0]
            ask.rename(columns={'ask_size':'size',
                                    'ask':'price',
                                    'ask_flag':'type'}, inplace=True)

            ob = bid.append(ask, ignore_index=True).dropna()
            return ob
    
        # Create figure
        fig = go.Figure()

        # Add traces, one for each slider step
        for time in range(0, len(list(data.keys())[0:100])):
            dff = __ob_melt(data[list(data.keys())[time]])
            fig.add_trace(go.Bar(x=dff['price'], y=dff['size'], 
            marker_color= ['red' if (dff['type'][i] == 'ask') else 
            'blue' for i in range(len(dff['type']))], width = 0.4))
        

        
        # Create and add slider
        steps = []
        for i in range(len(fig.data)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)},
                    {"title": "Slider switched to step: " + str(i)}],  # layout attribute
            )
            step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
            steps.append(step)

        sliders = [dict(
            active = 0,
            currentvalue={"prefix": "Frequency: "},
            pad={"t": len(list(data.keys())[0:100])},
            steps=steps
        )]

        fig.update_layout(
            sliders=sliders
        )
        fig.data[0].visible = True
        return fig.show()
    
    @staticmethod
    def plot_mid(xemm: dict, origin: dict, destination: dict, 
                 fiat_hist_dest: list, fiat_hist_origin: list) -> go.Figure:
        """
        Plots the mid-price of the XEMM orderbook against the origin and destination ones.

        Parameters:
        -----------
            xemm: Product orderbook of the XEMM implementation (dict).
            origin: Origin orderbook (dict).
            destination: Destination orderbook (dict).
            fiat_hist_dest: Destination balance per orderbook (list).
            fiat_hist_origin: Origin balance per orderbook (list).

        Returns:
        --------
            Scatter plot.
        """
        def __mid_price(data: dict) -> list:
            ob_ts = list(data.keys())
            mid = [(data[ob_ts[i]]['ask'][0] + data[ob_ts[i]]['bid'][0]) * 0.5 for i in range(0, len(ob_ts))]
            return mid

        origin = __mid_price(origin)
        xemm = __mid_price(xemm)
        destination = __mid_price(destination)[0:len(origin)]
        fig = make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_trace(go.Scatter(name = 'Origin orderbook', y = origin, marker_color = 'blue'), secondary_y=False)
        fig.add_trace(go.Scatter(name = 'XEMM orderbook', y = xemm, marker_color = 'green'), secondary_y=False)
        fig.add_trace(go.Scatter(name = 'Destination orderbook', y = destination, marker_color = 'grey'), secondary_y=False)
        fig.add_trace(go.Scatter(name = 'Destination balance', y = fiat_hist_dest, marker_color = 'firebrick'), secondary_y=True)
        fig.add_trace(go.Scatter(name = 'Origin balance', y = fiat_hist_origin, marker_color = 'navy'), secondary_y=True)
        fig.update_layout(autosize = False, width = 900, height = 800, title_text = f'Mid-price comparison')
        fig.update_xaxes(title_text = 'Number of orderbook')
        fig.update_yaxes(title_text = 'Mid-price', secondary_y=False)
        fig.update_yaxes(title_text = 'Cash Balance', secondary_y=True)
        return fig.show()
        
    @staticmethod
    def cash_balances(fiat_bal_origin: float, fiat_bal_dest: float) -> go.Figure:
        """
        Plots the cash balances.

        Parameters:
        -----------
            fiat_bal_origin: Origin orderbook cash balance (float).
            fiat_bal_dest: Destination orderbook cash balance (float).

        Returns:
        --------
            Bar plot.
        """

        fig = go.Figure(data = [
              go.Bar(name = 'Origin balance', y = [fiat_bal_origin], marker_color = 'pink'), 
              go.Bar(name = 'Destination balance', y = [fiat_bal_dest], marker_color = 'purple')])
        fig.update_layout(autosize = False, width = 900, height = 500, title_text = f'XEMM cash balance comparison')
        fig.update_yaxes(title_text = '$')
        return fig.show()
    
    @staticmethod
    def tokens_balances(token_bal_origin: float, token_bal_dest: float) -> go.Figure:
        """
        Plots the token balances.

        Parameters:
        -----------
            token_bal_origin: Origin orderbook token balance (float).
            token_bal_dest: Destination orderbook token balance (float).

        Returns:
        --------
            Bar plot.
        """

        fig = go.Figure(data = [
              go.Bar(name = 'Origin balance', y = [token_bal_origin], marker_color = 'navy'), 
              go.Bar(name = 'Destination balance', y = [token_bal_dest], marker_color = 'cyan')])
        fig.update_layout(autosize = False, width = 900, height = 500, title_text = f'XEMM token balance comparison')
        fig.update_yaxes(title_text = 'Tokens')
        return fig.show()

    @staticmethod
    def fees_comparison(fees_origin: list, fees_dest: list) -> go.Figure:
        """
        Plots the accumulated fees of the origin and destination orderbooks.

        Parameters:
        -----------
            fees_origin: Origin orderbook accumulated fees (list).
            fees_dest: Destination orderbook accumulated fees (list).

        Returns:
        --------
            Bar plot.
        """

        fig = go.Figure(data = [
              go.Bar(name = 'Origin accumulated fees', y = [-sum(fees_origin)], marker_color = 'brown'), 
              go.Bar(name = 'Destination accumulated fees', y = [-sum(fees_dest)], marker_color = 'orange')])
        fig.update_layout(autosize = False, width = 900, height = 500, title_text = f'Accumulated fees comparison')
        fig.update_yaxes(title_text = '$')
        return fig.show()