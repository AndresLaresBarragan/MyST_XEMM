
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: THE LICENSE TYPE AS STATED IN THE REPOSITORY                                               -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class XemmVisualization:

    @staticmethod
    def orderbook_history(data: dict):

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
        