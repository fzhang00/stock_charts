
_API = "a839f239d3e2ff7581a77d72aed58821"

import pandas as pd

from math import floor
import numpy as np
from lightweight_charts import Chart
from util import *
from econ import *
from chart import get_ticker_data
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()

rainbow_colors = ['#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#4b0082', '#8f00ff']

# Chart names here. Chart sequence follows as the name sequence here. 
# TODO: there are 21 items, but only 20 spots on the plot layout. See if it can be shrink to 20. 
names = ['World Index',   'Sector',  'SP500 Breadth', 'NASDAQ100 Speculation',
         'SP500 Speculation', 'CBOE Put/Call', 'NAAIM',        'AAII Sentiment', 'C_Spread, VIX, SP500', 
         'US Rate',           'Inflation',     'Oil/Gold CPI', 'Cu/Gold PPI',    'WEI, GDP',
         'PMI, Durable Goods','Housing Supply','Retail',       'Vehicle Sales',  'Housing Market', 
         'Job and Payroll', 'Personal Finance',
        ]

# names to functions lookup dictionary
name_func_dct = {'Job and Payroll': get_job_payroll_dat,
                 'Sector':get_sector_data,
                 'SP500 Breadth': get_sp_above_avg,
                 'World Index':get_index}

def draw_lines(sub_chart, df):
    """plot lines from dataframe, up to 6 lines"""
    # c_step = floor(len(rainbow_colors)/len(df.columns))
    colorcodes = get_hex_color_list(len(df.columns))
    for (i,c) in zip(df.columns, colorcodes):
        line = sub_chart.create_line(name=i, color=c)
        line.set(df[i].to_frame())


if __name__ == '__main__':
    
    chart = Chart(width=1024, inner_width=0.2, inner_height=0.25)
    print(chart.id)
    subcharts = [chart.create_subchart(width=0.2, height=0.25, sync=False) 
                 for i in range(len(names)-1)]
    charts = {n:c for (n,c) in zip(names, [chart]+subcharts)}
    
    for (key,subchart) in charts.items():
        subchart.legend(True)
        subchart.watermark(key)
        print(key, subchart)
        if key in name_func_dct:
            # if key == 'SP500 Breadth':
            #     update_sp_above_avg()
            df = name_func_dct[key]()
            print(df.columns, df.size)
            draw_lines(subchart, df)
        # # TODO: This piece is not good, the scale is too different from the breadth data which is percentage.
        # #         Probably a better choice is to sync all the time scale of the charts. 
        # if key == 'SP500 Breadth':
        #     # add sp500
        #     df = read_db_table('stock_data.db', '^GSPC')
        #     subchart.set(df)
    chart.show(block=True)