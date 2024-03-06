from fileinput import filename
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager
import robin_stocks.robinhood as r
import re
import os
from dotenv import load_dotenv

#I reccomend commenting out the everything in main except get_stocks() and Stock.print_all_instances() and running it once to see what the output looks like and then you can see what you want to do with the data, ajust any of the parameters you need to get your expected output then you can run it for real
#these are the basics for modifying this for your own use
params = {
    #modefies the base url to get the information you want from the website
        'per_page': '96', #this is just for ease of use so you dont have to iterate through multiple pages, if you are looking at a lot of data you may want to implement a way to iterate through multiple pages in the get_stocks function might add this later
        'txDate': '90d', #how far back you want to look
        'tradeSize': ['10', '9', '8', '7', '6', '5', '4'], #how much money was spent on the stock
        'assetType': ['stock', 'etf', 'crypto'], #what type of asset you want to look at
        'party': 'democrat' #what party you want to look at
    }
#risk * 1/1000 is the proportion you are investing compared to congress, there is a built in 1/1000 multiplier because no one will be investing that much
risk = (1/20) # Risk factor for the stocks fractional multiplier. the lower the value the less youll invest in each stock, i reccomend 1/10 for a low risk and 1/5 for a high risk but you can change it to whatever you want 1/10 means you invest 1/10000 of what congress does and 10 means you invest 1/100 of what congress does
#if you change risk you should delete the stock_info.txt file because the average amounts will be different and so it will write the same stock twice, part of the way it checks if the stock has already been written is by checking if the average amount is the same
file_path = 'C:/Python/Trading_Bot/stock_info.txt' # File to store the stock information this is a back up way to do it so if server goes down etc it know which ones have already been read
delay = 30 # Delay for the web scraping in minutes, how often you want it to check if new stock have been posted i recommend something high like 30-60 minutes becasue you dont want to make to many requests and getting the stocks right as there posted wont give you that much of an edge

#must create your own .env file with your own username and password
#gets password and username from a file so you dont have to hard code it in
load_dotenv()

class FileManager:

    def __init__(self):
        self.filename = file_path
        self.ensure_file_exists()
        
    def check_existing_values(self, new_line_values):
        """Check if new line values match any existing line's first 6 values."""
        with open(self.filename, 'r') as file:
            existing_lines = file.readlines()

        for line in existing_lines:
            # Splitting the line into values separated by comma
            existing_values = line.strip().split(',')
            
            # Checking if the first 6 values match
            if existing_values[:6] == new_line_values[:6]:
                return True
        
        return False

    def write_info(self, rep, stock_code, buy, average_amount, date_published, date_traded):
        """
        Writes stock information to a file only if it is not already present with all attributes matching.

        Args:
        rep (str): The name of the representative who made the trade.
        stock_code (str): The stock code.
        buy (str): Whether the trade was a buy or sell.
        average_amount (str): The average amount of the trade.
        date_published (str): The date the trade was published.
        date_traded (str): The date the trade was made.
        """

        # Ensure file exists
        self.ensure_file_exists()

        # Check if values already exist
        new_info = [str(rep), str(stock_code), str(buy), str(average_amount), str(date_published), str(date_traded)]
        if self.check_existing_values(new_info):
            return

        # If not, write the new info
        with open(self.filename, "a") as f:
            f.write(f"{','.join(new_info)}\n")    

    def read_stock_codes(self):
        """
        Returns a list of stock codes from the file.

        Returns:
            list: A list of stock codes.
        """

        stock_codes = []
        with open(self.filename, "r") as f:
            for line in f:
                stock_codes.append(line.split(",")[1])
        return (stock_codes)

    def read_buy_signals(self):
        """
        Returns a list of buy signals from the file.

        Returns:
            list: A list of buy signals ("buy" or "sell").
        """

        buy_signals = []
        with open(self.filename, "r") as f:
            for line in f:
                buy_signals.append(line.split(",")[2])
        return (buy_signals)

    def read_average_amounts(self):
        """
        Returns a list of average amounts from the file.

        Returns:
            list: A list of average amounts.
        """

        average_amounts = []
        with open(self.filename, "r") as f:
            for line in f:
                average_amounts.append(line.split(",")[3])
        return (average_amounts)
    
    def ensure_file_exists(self):
        # Check if the file exists, and create it if it doesn't
        if not os.path.exists(self.filename):
            with open(self.filename, 'w'):
                pass

'''def ensure_file_exists(filename):
    """
    Checks if the file exists, and creates it if it doesn't.

    Args:
        filename (str): The name of the file.
    """

    if not os.path.exists(filename):
        with open(filename, "w"):
            pass'''


class Stock:
    instances = []

    def __init__(self, stock_code, buy, average_amount, rep, date_traded, date_published):
        self.stock_code = stock_code
        self.buy = buy
        self.average_amount = str(average_amount)
        self.rep = rep
        self.date_traded = date_traded
        self.date_published = date_published
        self.counter = 1
        self.file = 'C:\Python\stock_info.txt' # File to store the stock information this is a back up way to do it so if server goes down etc it know which ones have already been read
        Stock.instances.append(self)

    @classmethod
    def print_all_instances(cls):
        for instance in cls.instances:
            print(f"Rep: {instance.rep}, Stock Code: {instance.stock_code}, Buy: {instance.buy}, Average Amount: {instance.average_amount}, Date Traded: {instance.date_traded}, Date Published: {instance.date_published} Counter: {instance.counter}")

# Function to convert a range string to an average value
def get_average_from_range(range_str):
    min_val, max_val = map(float, re.findall(r'\d+', range_str))
    return ((risk*((min_val + max_val) )/ 2)+1)

def get_stocks():
    driver = webdriver.Chrome()
    base_url = 'https://www.capitoltrades.com/trades'
    
    url_params = '&'.join([f'{key}={value}' if not isinstance(value, list) else '&'.join([f'{key}={v}' for v in value]) for key, value in params.items()])
    url = f'{base_url}?{url_params}'
    
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    stock_list = soup.find_all('tr', class_='q-tr')

    for item in stock_list:
        stock_name_element = item.find('span', class_='q-field issuer-ticker')
        amount_element = item.find('div', class_='q-range-icon-wrapper')
        buy_element = item.find('td', class_='q-td q-column--txType')
        representitive = item.find('h3', class_='q-fieldset politician-name')
        trade = item.find_all('div', class_='q-cell cell--tx-date')
        for date in trade:
            date_traded = date.find('div', class_='q-value')
        published = item.find_all('div', class_='q-cell cell--pub-date')
        for date in published:
            date_published = date.find('div', class_='q-value')

        if stock_name_element and amount_element and buy_element:
            stock_name = stock_name_element.text.strip()
            stock_code_match = re.search(r'\b[A-Z]{1,4}\b', stock_name)
            if stock_code_match:
                stock_code = stock_code_match.group()
            else:
                stock_code = "Stock code not found"

            amount_range = amount_element.text.strip()
            average_amount = get_average_from_range(amount_range)
            buy = buy_element.text.strip()
            rep = representitive.text.strip()
            date_traded = date_traded.text.strip()
            date_published = date_published.text.strip()
           
            Stock(stock_code, buy, average_amount, rep, date_traded, date_published)

    driver.quit()

def main():
    r.login(os.getenv("username"),os.getenv("password"))  # Login to Robinhood
    get_stocks()
    #Stock.print_all_instances()

    file_manager = FileManager()
    for stock in Stock.instances:
        file_manager.write_info(
            stock.rep,
            stock.stock_code,
            stock.buy,
            stock.average_amount,
            stock.date_published,
            stock.date_traded
        )

# Uses the file manager to read the stock codes, buy signals, and average amounts from the file and makes them into lists
    buy_signals = file_manager.read_buy_signals()
    stock_codes = file_manager.read_stock_codes()
    average_amounts = file_manager.read_average_amounts()
    #print(buy_signals, stock_codes, average_amounts)

    with open(file_manager.filename, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for i, line in enumerate(lines):
            parts = line.strip().split(',')
            if len(parts) != 6:
                continue  # Skip lines that don't have exactly six elements this is to skip lines that have already been read
            rep, stock_code, buy, average_amount, date_published, date_traded = parts
            for buys, stock, amount in zip(buy_signals, stock_codes, average_amounts):
                if buys == "buy":
                    r.orders.order_buy_fractional_by_price(stock, float(amount))
                    #print(f"buying {stock} at {amount}")
                else:
                    r.orders.order_sell_fractional_by_quantity(stock, float(amount))
                    #print(f"selling {stock} at {amount}")
                lines[i] = ','.join([rep, stock_code, buy, average_amount, date_published, date_traded, 'read\n'])

        file.seek(0)
        file.writelines(lines)
        file.truncate()

    
        
    print(f"just finished reading all trades. Will check again in {delay} minutes")

#this just runs everything it on a delay and will run indefinetly until you stop it
if __name__ == "__main__":
    while True:
        main()
        time.sleep(delay * 60)