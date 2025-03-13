import requests
from bs4 import BeautifulSoup

# Configuration
login_url = 'https://www.eoddata.com/login.aspx'
download_url = 'https://www.eoddata.com/download.aspx'
symbol = 'S5TH'

# Your credentials
credentials = {
    'ctl00$cp1$txtEmail': 'fzhang00@gmail.com',
    'ctl00$cp1$txtPassword': '124097FzHl',
    'ctl00$cp1$btnLogin': 'Login'
}

with requests.Session() as s:
    # 1. Get login page to capture viewstate
    login_page = s.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    
    # Add required ASP.NET fields to credentials
    credentials.update({
        '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
        '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
        '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
    })
    
    # 2. Perform login
    s.post(login_url, data=credentials)
    # After successful login, get the download form page
    download_form_url = f'https://www.eoddata.com/stockquote/INDEX/{symbol}.htm'
    download_page = s.get(download_form_url)
    soup = BeautifulSoup(download_page.text, 'html.parser')

    # Extract ALL required ASP.NET hidden fields
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
    viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']

    # Prepare the download request payload with ALL required fields
    download_payload = {
        # ASP.NET required fields
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': event_validation,
        '__VIEWSTATEGENERATOR': viewstate_generator,
        
        # Form values
        '__EVENTTARGET': 'ctl00$cp1$btnD1',  # The download button's event target
        'ctl00$cp1$txtSymbol': symbol,
        'ctl00$cp1$dpPeriod': '1M',  # 1 month
        'ctl00$cp1$cboExchange': 'Global Indices',  # Must match the exchange parameter
        'ctl00$cp1$cboDataFormat': '9',  # CSV format code
        'ctl00$cp1$cboPeriod': '0',  # End-of-day data
        'ctl00$cp1$txtEndDate': '02/13/2025'  # Use current date from the form
    }

    # Add any additional required fields found in the form
    for input_tag in soup.select('input[type="hidden"]'):
        name = input_tag.get('name')
        if name and name not in download_payload:
            download_payload[name] = input_tag.get('value', '')

    # Send the download request
    response = s.post(download_form_url, data=download_payload)    
    # Save the result
    with open(f'{symbol}_data.csv', 'wb') as f:
        f.write(response.content)
