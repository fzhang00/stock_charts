
_API = "a839f239d3e2ff7581a77d72aed58821"

import pandas as pd
import pandas_ta as ta

from math import floor
import numpy as np
from lightweight_charts import Chart
from util import *
from econ import *
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()

rainbow_colors = ['#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#4b0082', '#8f00ff']

# Chart names here. Chart sequence follows as the name sequence here. 
# TODO: there are 21 items, but only 20 spots on the plot layout. See if it can be shrink to 20. 
names = ['Job and Payroll',   'World Index',   'Sector',       'SP500 Breadth',  'NASDAQ100 Speculation',
         'SP500 Speculation', 'CBOE Put/Call', 'NAAIM',        'AAII Sentiment', 'C_Spread, VIX, SP500', 
         'US Rate',           'Inflation',     'Oil/Gold CPI', 'Cu/Gold PPI',    'WEI, GDP',
         'PMI, Durable Goods','Housing Supply','Retail',       'Vehicle Sales',  'Housing Market', 
         'Personal Finance',
        ]

# names to functions lookup dictionary
name_func_dct = {'Job and Payroll': get_job_payroll_dat}

def draw_lines(sub_chart, df):
    """plot lines from dataframe, up to 6 lines"""
    c_step = floor(len(rainbow_colors)/len(df.columns))
    for (i,c) in zip(df.columns, range(0, len(rainbow_colors), c_step)):
        line = sub_chart.create_line(name=i, color = rainbow_colors[c])
        line.set(df[i].to_frame())


if __name__ == '__main__':
    
    chart = Chart(width=1024, inner_width=0.2, inner_height=0.25)
    subcharts = [chart.create_subchart(width=0.2, height=0.25) 
                 for i in range(len(names)-1)]
    charts = {n:c for (n,c) in zip(names, [chart]+subcharts)}
    
    for (key,subchart) in charts.items():
        subchart.legend(True)
        subchart.watermark(key)
        print(key, subchart)
        if key in name_func_dct:
            df = name_func_dct[key]()
            draw_lines(subchart, df)

    chart.show(block=True)