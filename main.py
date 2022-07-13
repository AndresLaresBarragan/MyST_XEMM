"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Python implementation of cross exchange market-making (XEMM)                               -- #
# -- script: functions.py: python script with general functions                                          -- #
# -- author: MoyMFO, AndresLaresBarragan, Miriam1999                                                     -- #
# -- license: GPL-3.0 license                                                                            -- #
# -- repository: https://github.com/AndresLaresBarragan/MyST_XEMM                                        -- #                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import numpy as np
import pandas as pd
import data as dt
from functions import XEMM
from visualizations import XemmVisualization
import warnings
warnings.filterwarnings('ignore')

ob_krak, ob_bit = dt.read_jsonOB(file_name = 'orderbooks_05jul21.json')
obt = XEMM(ob_krak=ob_krak, ob_bit=ob_bit)
ob_xemm = obt.cross_exchange_market_making()
plots = XemmVisualization()
#plots.plot_mid(xemm = ob_xemm['ob_xemm'], origin = ob_krak, destination = ob_bit)
plots.cash_balances(fiat_bal_origin = ob_xemm['fiat_bal_origin'], fiat_bal_dest = ob_xemm['fiat_bal_dest'])
plots.tokens_balances(token_bal_origin = ob_xemm['token_bal_origin'], token_bal_dest = ob_xemm['token_bal_dest'])
plots.fees_comparison(fees_origin = ob_xemm['fees_origin'], fees_dest = ob_xemm['fees_dest'])
#plots.orderbook_history(ob_krak)
