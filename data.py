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
import os, sys, json

def read_jsonOB(file_name:str, file_dir:str = None):
    """
    Reads selected json type file in specified directory. 
    Transforms data to dictionary type, drops 'None' keys, and creates pandas DataFrames 
    from dictionary values.
    
    Parameters
    ----------
    
    file_name:str
        String indicating the name of the file to be read. (must include '.json')
        
    file_dir:str (default: None)
        String indicating the directory where the file is saved.
        If left unspecified, file's directory is assumed to be in current folder.
        
    exchnage:str (default:'bitfinex')        
        Indicates the desired exchange from which to filter the OrderBooks data.
        i.e. ['bitfinex','kraken']

    
    Returns
    -------
    
    ob_origin:dict
        Dictionary with sequential timestamps as keys and pandas DataFrames containing 
        orderbook data from the origin exchange as the dictionary values.
        
    ob_dest:dict
        Dictionary with sequential timestamps as keys and pandas DataFrames containing 
        orderbook data from the destination exchange as the dictionary values.
    
    """
    
    # obtain file directory if left unspecified
    if file_dir==None:
        abs_dir = os.path.abspath('.')+'\\files'
        sys.path.insert(0,abs_dir)
        file_dir = abs_dir
    
    # read JSON object
    f = open(file_dir+"\\"+file_name)

    # Origin exchange
        
    # return JSON object as dictionary
    orderbooks_data = json.load(f)
    ob_origin = orderbooks_data['kraken']  # select specific exchange
    
    # drop None keys
    ob_origin = {i_key: i_value for i_key, i_value in ob_origin.items() if i_value is not None}
    
    # create Dataframe and rearange columns
    ob_origin = {i_ob: pd.DataFrame(ob_origin[i_ob])[['bid_size','bid','ask','ask_size']]
               if ob_origin[i_ob] is not None else None for i_ob in list(ob_origin.keys())}
    
    # Destination exchange
    # return JSON object as dictionary
    ob_dest = orderbooks_data['bitfinex']  # select specific exchange
    
    # drop None keys
    ob_dest = {i_key: i_value for i_key, i_value in ob_dest.items() if i_value is not None}
    
    # create Dataframe and rearange columns
    ob_dest = {i_ob: pd.DataFrame(ob_dest[i_ob])[['bid_size','bid','ask','ask_size']]
               if ob_dest[i_ob] is not None else None for i_ob in list(ob_dest.keys())}

    
    
    return ob_origin, ob_dest

def describe(file_name:str, data:dict):
    """
    Brief description of input data.
    
    Parameters
    ----------
    
    file_name:str
        Indicates the name of the origin file.
        (the file from which the data was extracted from)
    
    data:dict
        dictionary object to be described.
    """
    
    keys = list(data.keys())
    
    print(f"\
          File name: {file_name} \n\
          Data type: {type(data)} \n\
          Size: {len(keys):,} entries\n\
          First/Last key: {keys[0], keys[-1]}\n\n\
          Keys data type: {type(keys[0])} \n\n\
          First value (first 3 rows): \n{data[keys[0]].head(3)} \n\
          ")
    
