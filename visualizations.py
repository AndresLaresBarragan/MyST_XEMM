
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
    def orderbook_history():
        s = 365 * 15
        df = pd.DataFrame({"date": pd.date_range("1-jan-2008", periods=s),
                        "positive": np.random.uniform(0, 20, s),
                        "negative": np.random.uniform(0, -5, s),})

        fig = go.Figure([
            go.Bar(x=df["date"], y=df["positive"], name="positive", marker_color="green"),
            go.Bar(x=df["date"], y=df["negative"], name="negative", base=0, marker_color="red"),
            ]).update_layout(
            barmode="stack",
            xaxis={
                "range": [df.iloc[-200]["date"], df["date"].max()],
                "rangeslider": {"visible": True},
            },
            margin={"l": 0, "r": 0, "t": 0, "r": 0},
        )
        return fig.show()
        