from util import *

def get_job_payroll_dat(start="2023-01-01"):
    """Get 3 employment data that indicate the US Job Market;
        - US Continuing Jobless Claims
        - US Initial Jobless Claims
        - Nonfarm Payroll (yearly change, not done)
        Data normalied by min max. Showing percentage change make more sense. (TODO)
    """
    data = get_fred_data(["CCSA", "ICSA", "PAYEMS"], start)
    data.fillna(method="ffill", inplace=True)
    data.fillna(method="bfill", inplace=True) # in case the first row is nan
    return normalize_minmax(data)

