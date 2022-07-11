
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

    def __init__(self, ob_krak: dict, ob_bit: dict, bp: int):
        self.ob_krak = ob_krak
        self.ob_bit = ob_bit
        self.bp = bp
        

    @property
    def bases_points(self) -> int:
        bp = (self.bp)/10000
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

    
    def levels_added(self, df_krak: pd.DataFrame) -> pd.DataFrame:
        
        bids_krak = df_krak[df_krak['bid']>self.origin_bounds()['lower_krak']][['bid','bid_size']]
        asks_krak = df_krak[df_krak['ask']<self.origin_bounds()['upper_krak']][['ask','ask_size']]

        levels = pd.concat([bids_krak, asks_krak], axis=1)

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
        np.random.seed(123)
        levels_added['transaction_time'] = np.random.uniform(1250, size=levels_added.shape[0])
        levels_added.sort_values(by='transaction_time', inplace=True, ignore_index=True)
        return levels_added

class XEMM(OrderBooksPreparation):

    def __init__(self, ob_krak: dict, ob_bit: dict, bp: int):
        super().__init__(ob_krak, ob_bit, bp)

    def cross_exchange_market_making(self, df_krak, bit_ask, bit_bid, krak_bid, krak_ask) -> pd.DataFrame:
        levels_added = self.levels_added(df_krak)
        for i in range(levels_added.shape[0]): # loop to add levels unto destination

            to_fill = levels_added.iloc[0,:]
            
            if to_fill['type']=='bid':
                # identify order's fee structure
                fee_type = 'taker' if to_fill['price'] >= bit_ask.iloc[0]['ask'] else 'maker'


                if fee_type=='taker':

                    bit_ask['accum_size'] = bit_ask['ask_size'].cumsum()


                    vol_to_fill=to_fill['size']

                    bit_ask['remaining_vol'] = vol_to_fill - bit_ask['accum_size']
                    to_drop = bit_ask[bit_ask['remaining_vol']>0]

                    bit_ask.drop(to_drop.index, inplace=True)
                    bit_ask.reset_index(drop=True, inplace=True)

                    new_vol = -bit_ask.iloc[0,-1]  # remaing volume on surviving level

                    bit_ask.iloc[0,1] = new_vol
                    bit_ask.drop(['accum_size', 'remaining_vol'], axis=1, inplace=True) 
                    bit_ask.reset_index(drop=True, inplace=True)
                    
                    levels_added.drop(0, inplace=True)
                    levels_added.reset_index(drop=True, inplace=True)
                    
                    # Hedge transaction in orgin exchange (Kraken)
                    
                    krak_bid['accum_size'] = krak_bid['bid_size'].cumsum()
                    krak_bid['remaining_vol'] = vol_to_fill - krak_bid['accum_size']
                    to_drop = krak_bid[krak_bid['remaining_vol']>0]
                    
                    krak_bid.drop(to_drop.index, inplace=True)
                    krak_bid.reset_index(drop=True, inplace=True)
                    
                    new_vol = -krak_bid.iloc[0,-1] # remaing volume on surviving level
                    
                    krak_bid.iloc[0,0] = new_vol
                    krak_bid.drop(['accum_size','remaining_vol'], axis=1, inplace=True)
                    krak_bid.reset_index(drop=True, inplace=True)
                    
                else:
                    
                    bit_bid.rename(columns={'bid_size':'size','bid':'price'}, inplace=True)
                    
                    to_fill = pd.DataFrame(to_fill).transpose()
                    to_fill['bid_added_vol'] = to_fill['size'].values
                    
                    bit_bid = bit_bid.merge(to_fill[['size','price','bid_added_vol']], 
                                            on=['size','price','bid_added_vol'], how='outer'
                                        ).sort_values(by='price', ascending=False, ignore_index=True) 
                
                    bit_bid.rename(columns={'size':'bid_size','price':'bid'}, inplace=True)
                    bit_bid = bit_bid.groupby('bid', as_index=False, sort=False).sum()
                    bit_bid = bit_bid.reindex(columns=['bid_added_vol', 'bid_size', 'bid'])


                    levels_added.drop(0, inplace=True)
                    levels_added.reset_index(drop=True, inplace=True)
                    
            else:
                
                # identify order's fee structure
                fee_type = 'taker' if to_fill['price'] < bit_bid.iloc[0]['bid'] else 'maker'            
                
                if fee_type == 'taker':
                    
                    bit_bid['accum_size'] = bit_bid['bid_size'].cumsum()


                    vol_to_fill = to_fill['size']

                    bit_bid['remaining_vol'] = vol_to_fill - bit_bid['accum_size']
                    to_drop = bit_bid[bit_bid['remaining_vol']>0]

                    bit_bid.drop(to_drop.index, inplace=True)
                    bit_bid.reset_index(drop=True, inplace=True)

                    new_vol = -bit_bid.iloc[0,-1] # remaing volume on surviving level

                    bit_bid.iloc[0,0] = new_vol
                    bit_bid.drop(['accum_size','remaining_vol'], axis=1, inplace=True)
                    bit_bid.reset_index(drop=True, inplace=True)
                    
                    levels_added.drop(0, inplace=True)
                    levels_added.reset_index(drop=True, inplace=True)
                    
                    # Hedge transaction in origin market (Kraken)
                    krak_ask['accum_size'] = krak_ask['bid_size'].cumsum()
                    krak_ask['remaining_vol'] = vol_to_fill - krak_ask['accum_size']
                    to_drop = krak_ask[krak_ask['remaining_vol']>0]
                    
                    krak_ask.drop(to_drop.index, inplace=True)
                    krak_ask.reset_index(drop=True, inplace=True)
                    
                    new_vol = -krak_ask.iloc[0,-1] # remaing volume on surviving level
                    
                    krak_ask.iloc[0,1] = new_vol
                    krak_ask.drop(['accum_size','remaining_vol'], axis=1, inplace=True)
                    krak_ask.reset_index(drop=True, inplace=True)
                    
                    
                else:
                    bit_ask.rename(columns={'ask_size':'size','ask':'price'}, inplace=True)
                    
                    to_fill = pd.DataFrame(to_fill).transpose()
                    to_fill['ask_added_vol'] = to_fill['size'].values
                    
                    bit_ask = bit_ask.merge(to_fill[['size','price','ask_added_vol']], 
                                            on=['size','price','ask_added_vol'], how='outer'
                                        ).sort_values(by='price', ascending=True, ignore_index=True)               
                    bit_ask.rename(columns={'size':'ask_size','price':'ask'}, inplace=True)
                    bit_ask = bit_ask.groupby('ask', as_index=False, sort=False).sum()
                    bit_ask = bit_ask.reindex(columns=['ask', 'ask_size', 'ask_added_vol'])


                    levels_added.drop(0, inplace=True)
                    levels_added.reset_index(drop=True, inplace=True)
                    
        return levels_added