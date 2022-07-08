
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: THE LICENSE TYPE AS STATED IN THE REPOSITORY                                               -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import numpy as np
import pandas as pd
import data as dt
from functions import OrderBooksPreparation, XEMM

ob_krak, ob_bit = dt.read_jsonOB(file_name = 'orderbooks_05jul21.json')
obt = XEMM(ob_krak=ob_krak, ob_bit=ob_bit, bp=10)

#df_krak = ob_krak[list(ob_krak.keys())[0]]
#df_bit = ob_bit[list(ob_bit.keys())[0]]
# destination exchange
#bit_ask = df_bit[['ask','ask_size']]
#bit_bid = df_bit[['bid_size','bid']]

#bit_ask['ask_added_vol'] = np.zeros(bit_ask.shape[0])
#bit_bid['bid_added_vol'] = np.zeros(bit_bid.shape[0])

# origin exchnage
#krak_bid = df_krak[['bid_size','bid']]
#krak_ask = df_krak[['ask','ask_size']]


