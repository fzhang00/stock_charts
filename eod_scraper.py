import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eod_scraper.log'),
        logging.StreamHandler()
    ]
)

def create_symbol_table(symbol, conn):
    """Create a table for the symbol if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS symbol_{symbol} (
            date DATE PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume INTEGER,
            open_interest INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def parse_value(value):
    """Convert string value to float/int, handling empty strings"""
    try:
        return float(value.replace(',', '')) if value else 0
    except ValueError:
        return 0

def scrape_eod_data(symbol):
    """Scrape EOD data for a given symbol"""
    url = f"https://www.eoddata.com/stockquote/INDEX/{symbol}.htm"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with recent EOD prices
        table = soup.find('table', {'class': 'quotes'})  # You might need to adjust this selector
        if not table:
            print(f"No data table found for symbol {symbol}")
            return []
        
        rows = table.find_all('tr')[1:]  # Skip header row
        data = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 7:
                data.append({
                    'date': datetime.strptime(cols[0].text.strip(), '%m/%d/%y').strftime('%Y-%m-%d'),
                    'open': parse_value(cols[1].text.strip()),
                    'high': parse_value(cols[2].text.strip()),
                    'low': parse_value(cols[3].text.strip()),
                    'close': parse_value(cols[4].text.strip()),
                    'volume': parse_value(cols[5].text.strip()),
                    'open_interest': parse_value(cols[6].text.strip())
                })
        
        return data
    
    except Exception as e:
        print(f"Error scraping data for {symbol}: {str(e)}")
        return []

def update_database(symbol, conn):
    """Update database with new EOD data"""
    try:
        data = scrape_eod_data(symbol)
        if not data:
            logging.warning(f"No data retrieved for symbol {symbol}")
            return
        
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        create_symbol_table(symbol, conn)
        
        # Insert new data
        for row in data:
            cursor.execute(f'''
                INSERT OR REPLACE INTO symbol_{symbol}
                (date, open, high, low, close, volume, open_interest)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['date'], row['open'], row['high'], row['low'],
                row['close'], row['volume'], row['open_interest']
            ))
        
        conn.commit()
        logging.info(f"Updated {len(data)} records for {symbol}")
        
    except Exception as e:
        logging.error(f"Error updating database for {symbol}: {str(e)}")
        conn.rollback()

def update_all_symbols(symbols, db_path):
    """Update data for all symbols once"""
    conn = sqlite3.connect(db_path)
    current_time = datetime.now()
    logging.info(f"Starting update at {current_time}")
    
    try:
        for symbol in symbols:
            try:
                update_database(symbol, conn)
                # Add small delay between symbols
                time.sleep(2)
            except Exception as e:
                logging.error(f"Failed to update {symbol}: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    DB_PATH = 'market_data.db'
    SYMBOLS = [
        'S5TH',  # S&P 500 Stocks Above 200-Day Average
        'S5OH',  # S&P 500 Stocks Above 50-Day Average
        'S5FI',  # S&P 500 Stocks Above 5-Day Average
        'MMFI',  # NASDAQ 100 Stocks Above 5-Day Average
        'MMOH',  # NASDAQ 100 Stocks Above 50-Day Average
        'MMTH'   # NASDAQ 100 Stocks Above 200-Day Average
    ]
    
    update_all_symbols(SYMBOLS, DB_PATH) 