from util import *

def get_job_payroll_dat(start="2000-01-01"):
    """Get 3 employment data that indicate the US Job Market;
        - US Continuing Jobless Claims
        - US Initial Jobless Claims
        - Nonfarm Payroll (yearly change, not done)
    """
    data = get_fred_data(["CCSA", "ICSA", "PAYEMS"], start)
    data.fillna(method="ffill", inplace=True)
    return normalize_minmax(data)

# names to functions lookup dictionary
name_func_dct = {'Job and Payroll': get_job_payroll_dat}