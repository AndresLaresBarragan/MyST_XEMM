"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Python implementation of cross exchange market-making (XEMM)                               -- #
# -- script: functions.py: python script with general functions                                          -- #
# -- author: MoyMFO, AndresLaresBarragan, Miriam1999                                                     -- #
# -- license: GPL-3.0 license                                                                            -- #
# -- repository: https://github.com/AndresLaresBarragan/MyST_XEMM                                        -- #                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
import numpy as np

class XEMM:
    """
    This class allows to create objects of processes of the XEMM according to the origin and destination 
    orderbooks, the cash and token balance and the fees.

    Parameters:
    -----------
        ob_krak: origin orderbook (dict)
        ob_bid: destination orderbook (dict)
        bp: level depth basis points (int)
        prcnt: the proportion of levels to add (float)
        fiat_bal_dest: destination orderbook cash initial balance (float) (default = 1,000,000)
        token_bal_dest: destination orderbook token initial balance (float) (default = 100)
        fiat_bal_origin: origin orderbook cash initial balance (float) (default = 1,000,000)
        token_bal_origin: origin orderbook token initial balance (float) (default = 100)
        fee_taker_dest: taker position fee of the destination (float) (default = 0.003)
        fee_maker_dest: maker position fee of the destination (float) (default = 0.0015)
        fee_taker_origin: taker position fee of the origin (float) (default = 0.002)
        fee_maker_origin: maker position fee of the origin (float) (default = 0.001)

    Methods:
    --------
        --origin_destination_alignment: aligns the destination timestaps after the origin ones.
        --cross_exchange_market_making: implements all the processes of the cross exchange market-making. 
          It updates the balances and adds levels.
    """
    def __init__(self, ob_krak: dict, ob_bit: dict, bp: int=10, prcnt: float=1,
                 fiat_bal_dest: float=1000000, token_bal_dest: float=100,
                 fiat_bal_origin: float=1000000, token_bal_origin: float=100,
                 fee_taker_dest: float=.003, fee_maker_dest: float=.0015,
                 fee_taker_origin: float=.002, fee_maker_origin:float=.001):
        self.ob_krak = ob_krak
        self.ob_bit = ob_bit
        self.bp = bp
        self.prcnt = prcnt
        self.fiat_bal_dest = fiat_bal_dest
        self.token_bal_dest = token_bal_dest
        self.fiat_bal_origin = fiat_bal_origin
        self.token_bal_origin = token_bal_origin
        self.fee_taker_dest = fee_taker_dest
        self.fee_maker_dest = fee_maker_dest
        self.fee_taker_origin = fee_taker_origin
        self.fee_maker_origin = fee_maker_origin


    def origin_destination_alignment(self) -> list.pop:
        """
        This function aligns the timestamps of the origin and destination orderbooks.

        Parameters:
        -----------
            Already defined in the class constructor.

        Returns:
        --------
            Aligned destination orderbook after origin.
        """
        aux = sum(pd.to_datetime(pd.Series((self.ob_bit.keys()))) 
                  < pd.to_datetime(pd.Series(self.ob_krak.keys()))[0])
        return [self.ob_bit.pop(key) for key in list(self.ob_bit.keys())[:aux]]


    def cross_exchange_market_making(self) -> dict:
        """
        This function adds levels from the origin orderbook to the destination one. Additionally, it
        consumes the levels if they are traded. Moreover, it saves the payed fees and updates the balances.

        Parameters:
        -----------
            Already defined in the class constructor.

        Returns:
        --------
            Dictionary containing the orderbooks with the levels added and the balances.
        """
        # Orderbook aligment
        self.origin_destination_alignment()

        # Storing variables
        ob_xemm = {}
        bids_to_fill_hist = []
        asks_to_fill_hist = []
        size_to_fill_hist = []

        fiat_hist_dest = [self.fiat_bal_dest]
        fiat_hist_origin = [self.fiat_bal_origin]
        token_hist_dest = [self.token_bal_dest]
        token_hist_origin = [self.token_bal_origin]

        fees_dest = []
        fees_origin = []
        latency_limit = 1500 # median timedelta between OB updates in destination exchange

        # Origin OB
        df_krak = self.ob_krak[list(self.ob_krak.keys())[0]]
        mid_krak = (df_krak['bid'][0] + df_krak['ask'][0]) / 2

        # Destination OB
        df_bit = self.ob_bit[list(self.ob_bit.keys())[0]]
        bit_ask = df_bit[['ask', 'ask_size']]
        bit_bid = df_bit[['bid_size', 'bid']]
        bit_ask['ask_added_vol'] = np.zeros(bit_ask.shape[0])
        bit_bid['bid_added_vol'] = np.zeros(bit_bid.shape[0])

        for t in range(50): #len(ob_krak.keys())-1
            krak_bid = df_krak[['bid_size', 'bid']]
            krak_ask = df_krak[['ask', 'ask_size']]
            
            upper_krak = mid_krak*(1 + self.bp / 10000)
            lower_krak = mid_krak*(1 - self.bp / 10000)
            
            bids_krak = df_krak[df_krak['bid'] > lower_krak][['bid', 'bid_size']]
            asks_krak = df_krak[df_krak['ask'] < upper_krak][['ask', 'ask_size']]
            levels = pd.concat([bids_krak, asks_krak], axis = 1)
            
            # replicate origin levels on destination
            bid_levels = levels[['bid_size', 'bid']]
            bid_levels['bid_flag'] = ['bid'] * bid_levels.shape[0]
            bid_levels.rename(columns={'bid_size':'size',
                                    'bid':'price',
                                    'bid_flag':'type'}, inplace=True)
            bid_levels['size'] = bid_levels['size']*self.prcnt
            
            ask_levels = levels[['ask_size', 'ask']]
            ask_levels['ask_flag'] = ['ask'] * ask_levels.shape[0]
            ask_levels.rename(columns={'ask_size':'size',
                                    'ask':'price',
                                    'ask_flag':'type'}, inplace=True)
            ask_levels['size'] = ask_levels['size'] * self.prcnt
            
            levels_added = bid_levels.append(ask_levels, ignore_index=True).dropna()
            np.random.seed(123)
            
            # sort queue by transaction time
            levels_added['transaction_time'] = np.random.uniform(250, size=levels_added.shape[0])
            levels_added.sort_values(by='transaction_time', inplace=True, ignore_index=True)
            
            
            # cut list of levels_added by a specified latency limit
            levels_added['elapsed_time'] = levels_added['transaction_time'].cumsum()
            to_drop = levels_added[levels_added['elapsed_time'] > latency_limit]
            levels_added.drop(to_drop.index, inplace=True)
            levels_added.drop('elapsed_time', axis=1, inplace=True)
            levels_added.reset_index(drop=True, inplace=True)
            
            size_to_fill_hist.append(levels_added['size'].sum())
            
            for i in range(levels_added.shape[0]): # loop to add levels unto destination
                aux = levels_added
                to_fill = levels_added.iloc[0,:]

                if to_fill['type']=='bid':
                    # identify order's fee structure
                    fee_type = 'taker' if to_fill['price'] >= bit_ask.iloc[0]['ask'] else 'maker'


                    if fee_type=='taker':
                        
                        # register fees paid
                        fees_dest.append(to_fill['size']*bit_ask['ask'][0]*self.fee_taker_dest)
                        fees_origin.append(to_fill['size']*krak_bid['bid'][0]*self.fee_taker_origin)
                        # register effects on balances
                        self.fiat_bal_dest += -fees_dest[-1] - (to_fill['size']*bit_ask['ask'][0])
                        self.fiat_bal_origin += -fees_origin[-1] + (to_fill['size']*krak_bid['bid'][0])
                        self.token_bal_dest += to_fill['size']
                        self.token_bal_origin += -to_fill['size']

                        bit_ask['accum_size'] = bit_ask['ask_size'].cumsum()

                        vol_to_fill = to_fill['size']
                        bit_ask['remaining_vol'] = vol_to_fill - bit_ask['accum_size']
                        to_drop = bit_ask[bit_ask['remaining_vol'] > 0]

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
                        
                        # register paid fees
                        fees_dest.append(to_fill['size']*bit_bid['bid'][0]*self.fee_taker_dest)
                        fees_origin.append(to_fill['size']*krak_ask['ask'][0]*self.fee_taker_origin)
                        # register effects on balances
                        self.fiat_bal_dest += -fees_dest[-1] + (to_fill['size']*bit_bid['bid'][0])
                        self.fiat_bal_origin += -fees_origin[-1] - (to_fill['size']*krak_ask['ask'][0])
                        self.token_bal_dest += -to_fill['size']
                        self.token_bal_origin += to_fill['size']

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
                        krak_ask['accum_size'] = krak_ask['ask_size'].cumsum()
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
            
            ob_xemm[list(self.ob_bit.keys())[t]]  = pd.concat([bit_bid, bit_ask], axis=1)
            # Destination OB at the following timestamp            
            next_ob_bit = self.ob_bit[list(self.ob_bit.keys())[t+1]]
            new_tob = (next_ob_bit.loc['0','bid'], next_ob_bit.loc['0','ask'])

            # levels to drop after comparison with next destination TOB
            bids_to_drop = bit_bid[bit_bid['bid']>new_tob[0]]
            asks_to_drop = bit_ask[bit_ask['ask']<new_tob[1]]
            
            # Register fees and transaction effects on balances
            fees_dest.append((bids_to_drop['bid_size']*bids_to_drop['bid']*self.fee_maker_dest).sum())
            self.fiat_bal_dest += -fees_dest[-1] - (bids_to_drop['bid']*bids_to_drop['bid_size']).sum()
            self.token_bal_dest += bids_to_drop['bid_size'].sum() 
            fees_origin.append((krak_bid['bid'][0]*bids_to_drop['bid_size']*self.fee_maker_origin).sum())
            self.fiat_bal_origin += -fees_origin[-1] + (krak_bid['bid'][0]*bids_to_drop['bid_size']).sum()
            self.token_bal_origin += -bids_to_drop['bid_size'].sum() 
            
            fees_dest.append((asks_to_drop['ask_size']*asks_to_drop['ask']*self.fee_maker_dest).sum())
            self.fiat_bal_dest += -fees_dest[-1] + (asks_to_drop['ask']*asks_to_drop['ask_size']).sum()
            self.token_bal_dest += -asks_to_drop['ask_size'].sum() 
            fees_origin.append((krak_ask['ask'][0]*asks_to_drop['ask_size']*self.fee_maker_origin).sum())
            self.fiat_bal_origin += -fees_origin[-1] - (krak_ask['ask'][0]*asks_to_drop['ask_size']).sum()
            self.token_bal_origin += asks_to_drop['ask_size'].sum() 
            

            bit_bid.drop(bids_to_drop.index, inplace=True)
            bit_bid.reset_index(drop=True, inplace=True)
            bit_ask.drop(asks_to_drop.index, inplace=True)
            bit_ask.reset_index(drop=True, inplace=True)    
            
            # Destination after adding origin's levels and comparing to following OB's ToB.
            bit_ob = pd.concat([bit_bid, bit_ask], axis=1)

            # Destination XEMM output OrderBook
            bit_bid_new_tob = bit_ob[['bid_added_vol','bid_size','bid']]
            bit_ask_new_tob = bit_ob[['ask_added_vol','ask_size','ask']]

            # Destination's next OrderBook
            next_ob_bit_bids = next_ob_bit[['bid_size','bid']]
            next_ob_bit_asks = next_ob_bit[['ask','ask_size']]
            next_ob_bit_bids['bid_added_vol'] = np.zeros(next_ob_bit_bids.shape[0]) 
            next_ob_bit_asks['ask_added_vol'] = np.zeros(next_ob_bit_asks.shape[0]) 


            # Origin's next OrderBook
            next_ob_krak = self.ob_krak[list(self.ob_krak.keys())[t+1]] 
            next_ob_krak_bids = next_ob_krak[['bid_size','bid']]
            next_ob_krak_asks = next_ob_krak[['ask_size','ask']]
            
                
            # generate new OrderBook based on next OB data (modify depth of output OB 'bit_ob')
            
            # Bids
            
            # data prep
            new_vols_bid = pd.merge(bit_bid_new_tob, next_ob_bit_bids, on=['bid', 'bid_added_vol'], how='outer').fillna(0)
            new_vols_bid = new_vols_bid.groupby(by='bid', as_index=False, sort=False).sum()
            new_vols_bid.sort_values(by='bid', ascending=False, ignore_index=True, inplace=True)
            new_vols_bid.rename(columns={'bid_size_x':'current_vol','bid_size_y':'next_vol'}, inplace=True)
            
            # procedure
            new_vols_bid['original_vol'] = new_vols_bid['current_vol'] - new_vols_bid['bid_added_vol']
            
            # scenario a: existing level w/o volume in next ob
            new_vols_bid['new_vol'] = np.zeros(new_vols_bid.shape[0]) 
            
            # scenario b: added level with volume in next ob
            indx_b = new_vols_bid[(new_vols_bid['original_vol']==0) & (new_vols_bid['next_vol']!=0)].index
            new_vols_bid.loc[indx_b,'new_vol'] = new_vols_bid.loc[indx_b, 'current_vol'] + new_vols_bid.loc[indx_b,'next_vol'] 
            
            # scenario c: added level w/o volume in next ob
            indx_c = new_vols_bid[(new_vols_bid['original_vol']==0) & (new_vols_bid['next_vol']==0)].index
            new_vols_bid.loc[indx_c,'new_vol'] = new_vols_bid.loc[indx_c, 'bid_added_vol']
                
            # scenario d: existing level with volume in next ob
            
            indx_d = new_vols_bid[(new_vols_bid['original_vol']!=0) & (new_vols_bid['next_vol']!=0)].index
            new_vols_bid.loc[indx_d,'new_vol'] = new_vols_bid.loc[indx_d, 'current_vol'] + (new_vols_bid.loc[indx_d, 'next_vol'] 
                                                                                            - new_vols_bid.loc[indx_d, 'original_vol'])
            
            # identify filled orders
            to_drop = new_vols_bid[new_vols_bid['new_vol'] == 0]
            new_vols_bid.drop(to_drop.index, inplace=True)
            new_vols_bid.reset_index(drop=True, inplace=True)
            # output
            df_bid = new_vols_bid[['bid_added_vol','new_vol', 'bid']]
            df_bid.rename(columns={'new_vol':'bid_size'}, inplace=True)
            
            # Asks
            
            # data prep
            new_vols_ask = pd.merge(bit_ask_new_tob, next_ob_bit_asks, on=['ask', 'ask_added_vol'], how='outer').fillna(0)
            new_vols_ask = new_vols_ask.groupby(by='ask', as_index=False, sort=False).sum()
            new_vols_ask.sort_values(by='ask', ignore_index=True, inplace=True)
            new_vols_ask.rename(columns={'ask_size_x':'current_vol','ask_size_y':'next_vol'}, inplace=True)
            
            # procedure
            new_vols_ask['original_vol'] = new_vols_ask['current_vol'] - new_vols_ask['ask_added_vol']
            new_vols_ask.drop(new_vols_ask[new_vols_ask['ask']==0].index, inplace=True) # drop levels whose price is 0
            new_vols_ask.reset_index(drop=True, inplace=True)
            
            # scenario a: existing level w/o volume in next ob
            new_vols_ask['new_vol'] = np.zeros(new_vols_ask.shape[0]) 
            
            # scenario b: added level with volume in next ob
            indx_b = new_vols_ask[(new_vols_ask['original_vol']==0) & (new_vols_ask['next_vol']!=0)].index
            new_vols_ask.loc[indx_b,'new_vol'] = new_vols_ask.loc[indx_b, 'current_vol'] + new_vols_ask.loc[indx_b,'next_vol'] 
            
            # scenario c: added level w/o volume in next ob
            indx_c = new_vols_ask[(new_vols_ask['original_vol']==0) & (new_vols_ask['next_vol']==0)].index
            new_vols_ask.loc[indx_c,'new_vol'] = new_vols_ask.loc[indx_c, 'ask_added_vol']
            
            # scenario d: existing level with volume in next ob
            indx_d = new_vols_ask[(new_vols_ask['original_vol']!=0) & (new_vols_ask['next_vol']!=0)].index
            new_vols_ask.loc[indx_d,'new_vol'] = new_vols_ask.loc[indx_d, 'current_vol'] + (new_vols_ask.loc[indx_d, 'next_vol'] 
                                                                                            - new_vols_ask.loc[indx_d, 'original_vol'])
            to_drop = new_vols_ask[new_vols_ask['new_vol'] == 0]
            new_vols_ask.drop(to_drop.index, inplace=True)
            new_vols_ask.reset_index(drop=True, inplace=True)
            
            # output
            df_ask = new_vols_ask[['ask','new_vol','ask_added_vol']]
            df_ask.rename(columns={'new_vol':'ask_size'}, inplace=True)
            df_out = pd.concat([df_bid, df_ask], axis=1)

            # fill bid limit orders
            bids_to_fill = new_vols_bid[(new_vols_bid['original_vol']!=0) & (new_vols_bid['next_vol']==0)][['bid_added_vol','bid']]
            bids_to_fill_hist.append(bids_to_fill['bid_added_vol'].sum())
            
            for vol_to_fill in bids_to_fill['bid_added_vol'].values:
                # Hedge transaction in origin market (Kraken)
                next_ob_krak_asks['accum_size'] = next_ob_krak_asks['ask_size'].cumsum()
                next_ob_krak_asks['remaining_vol'] = vol_to_fill - next_ob_krak_asks['accum_size']
                to_drop = next_ob_krak_asks[next_ob_krak_asks['remaining_vol']>0]

                next_ob_krak_asks.drop(to_drop.index, inplace=True)
                next_ob_krak_asks.reset_index(drop=True, inplace=True)

                new_vol = -next_ob_krak_asks.iloc[0,-1] # remaing volume on surviving level

                next_ob_krak_asks.iloc[0,1] = new_vol
                next_ob_krak_asks.drop(['accum_size','remaining_vol'], axis=1, inplace=True)
                next_ob_krak_asks.reset_index(drop=True, inplace=True)



            # fill ask limit orders
            asks_to_fill = new_vols_ask[(new_vols_ask['original_vol']!=0) & (new_vols_ask['next_vol']==0)][['ask_added_vol','ask']]
            asks_to_fill_hist.append(asks_to_fill['ask_added_vol'].sum())

            for vol_to_fill in asks_to_fill['ask_added_vol'].values:
                # Hedge transaction in origin market (Kraken)
                next_ob_krak_bids['accum_size'] = next_ob_krak_bids['bid_size'].cumsum()
                next_ob_krak_bids['remaining_vol'] = vol_to_fill - next_ob_krak_bids['accum_size']
                to_drop = next_ob_krak_bids[next_ob_krak_bids['remaining_vol']>0]

                next_ob_krak_bids.drop(to_drop.index, inplace = True)
                next_ob_krak_bids.reset_index(drop = True, inplace = True)

                new_vol = -next_ob_krak_bids.iloc[0, -1] # remaining volume on surviving level

                next_ob_krak_bids.iloc[0, 1] = new_vol
                next_ob_krak_bids.drop(['accum_size', 'remaining_vol'], axis = 1, inplace = True)
                next_ob_krak_bids.reset_index(drop = True, inplace = True)

            # re-assign variables for next iteration           
            df_bit = df_out
            bit_ask = df_bit[['ask', 'ask_size', 'ask_added_vol']]
            bit_bid = df_bit[['bid_added_vol', 'bid_size', 'bid']]

            df_krak = pd.concat([next_ob_krak_bids, next_ob_krak_asks], axis = 1)        
            mid_krak = (df_krak['bid'][0] + df_krak['ask'][0]) / 2       
        
        results = {'fiat_bal_dest': self.fiat_bal_dest, 'token_bal_dest': self.token_bal_dest,
                   'fiat_bal_origin': self.fiat_bal_origin, 'token_bal_origin': self.token_bal_origin,
                   'ob_xemm': ob_xemm, 'fees_dest': fees_dest, 'fees_origin': fees_origin}
        return results

        