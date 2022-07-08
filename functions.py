
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: THE LICENSE TYPE AS STATED IN THE REPOSITORY                                               -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import json
import pandas as pd
import numpy as np


class OrderBooksPreparation:

    def __init__(self, ob_krak: dict, ob_bit: dict, bases_points: int) -> None:
        self.ob_krak = ob_krak
        self.ob_bit = ob_bit
        self.bases_points = bases_points

    @property
    def bases_points(self) -> float:
        bp = self.bases_points/10000
        return bp

    @property
    def origin_mid_price(self) -> float:
        df_krak = self.ob_krak[list(self.ob_krak.keys())[0]]
        mid_krak = (df_krak['bid'][0]+df_krak['ask'][0])/2
        return mid_krak

    @property
    def destination_mid_price(self) -> float:
        df_bit = self.ob_bit[list(self.ob_bit.keys())[0]]
        mid_bit = (df_bit['bid'][0]+df_bit['ask'][0])/2
        return mid_bit

    def origin_destination_alignment(self) -> list.pop:
        aux = sum(pd.to_datetime(pd.Series((self.ob_bit.keys()))) 
                  < pd.to_datetime(pd.Series(self.ob_krak.keys()))[0])
        return [self.ob_bit.pop(key) for key in list(self.ob_bit.keys())[:aux]]

    
    def origin_bounds(self) -> dict:
        bounds = {'upper_krak': self.origin_mid_price*(1+self.bases_points),
                  'lower_krak': self.origin_mid_price*(1-self.bases_points)}
        return bounds
    
    def levels_added(self) -> pd.DataFrame:
        df_krak = self.ob_krak[list(self.ob_krak.keys())[0]]
        df_bit = self.ob_bit[list(self.ob_bit.keys())[0]]
        
        bids_krak = df_krak[df_krak['bid']>self.origin_bounds()['lower_krak']][['bid','bid_size']]
        asks_krak = df_krak[df_krak['ask']<self.origin_bounds()['upper_krak']][['ask','ask_size']]
        # destination exchange
        bit_ask = df_bit[['ask','ask_size']]
        bit_bid = df_bit[['bid_size','bid']]

        # origin exchnage
        krak_bid = df_krak[['bid_size','bid']]
        krak_ask = df_krak[['ask','ask_size']]

        bid_levels = levels[['bid_size','bid']]
        bid_levels['bid_flag'] = ['bid']*bid_levels.shape[0]
        bid_levels.rename(columns={'bid_size':'size',
                                'bid':'price',
                                'bid_flag':'type'}, inplace=True)

        ask_levels = levels[['ask_size','ask']]
        ask_levels['ask_flag'] = ['ask']*ask_levels.shape[0]
        ask_levels.rename(columns={'ask_size':'size',
                                'ask':'price',
                                'ask_flag':'type'}, inplace=True)

        levels_added = bid_levels.append(ask_levels, ignore_index=True).dropna()

        levels_added['transaction_time'] = np.random.uniform(1250, size=levels_added.shape[0])
        levels_added.sort_values(by='transaction_time', inplace=True, ignore_index=True)
        return levels_added

    