import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import csv

# Credentials
USERNAME = 'sabzi.online@gmail.com'
PASSWORD = 'Sabzi@1190'

# URLs to scrape
input_csv = 'sectors.csv'
output_csv = 'stock_details.csv'


async def login(page):
    await page.goto('https://www.screener.in/login/')
    await page.fill('//*[@id="id_username"]', USERNAME)
    await page.fill('//*[@id="id_password"]', PASSWORD)
    await page.click('button.button-primary')
    await page.wait_for_load_state('networkidle')

async def scrape_data(page, url):
    await page.goto(url)
    # elements_to_scrape = [
    #     ('//*[@id="top"]/div[2]/a[2]/span', 'symbol'),
    #     ('//*[@id="top"]/div[1]/div/div[2]/div[1]/span[1]', 'price'),
    #     ('//*[@id="top-ratios"]/li[1]/span[2]/span', 'mcap'),
    #     ('//*[@id="top-ratios"]/li[5]/span[2]/span', 'book_value'),
    #     ('//*[@id="top-ratios"]/li[11]/span[2]/span', 'intrinsic_value'),
    #     ('//*[@id="top-ratios"]/li[4]/span[2]/span', 'stock_pe'),
    #     ('//*[@id="top-ratios"]/li[10]/span[2]/span', 'industry_pe'),
    #     ('//*[@id="top-ratios"]/li[14]/span[2]/span', 'debt'),
    #     ('//*[@id="top-ratios"]/li[23]/span[2]/span', 'int_coverage'),
    #     ('//*[@id="top-ratios"]/li[12]/span[2]/span', 'promoter_holding'),
    #     ('//*[@id="top-ratios"]/li[13]/span[2]/span', 'change_in_prom_hold'),
    #     ('//*[@id="top-ratios"]/li[18]/span[2]/span', 'fii_holding'),
    #     ('//*[@id="top-ratios"]/li[19]/span[2]/span', 'change_in_fii_holding'),
    #     ('//*[@id="top-ratios"]/li[20]/span[2]/span', 'dii_holding'),
    #     ('//*[@id="top-ratios"]/li[21]/span[2]/span', 'change_in_dii_holding'),
    #     ('//*[@id="top-ratios"]/li[22]/span[2]/span', 'debt_to_equity'),
    #     ('//*[@id="top-ratios"]/li[3]/span[2]/span[1]', 'high_52week'),
    #     ('//*[@id="top-ratios"]/li[3]/span[2]/span[2]', 'low_52week')
    # ]
    # tt = page.wait_for_timeout()
    # elem = page.innerText('//*[@id="top-ratios"]/li[1]/span[2]/span')
    # elem = await page.query_selector('#top-ratios')
    try:
        # elem = await page.wait_for_timeout(f'xpath=//*[@id="top-ratios"]/li[1]/span[2]/span')
        # if page.query_selector('#top-ratios') is not None:
        symbol = await page.text_content('//*[@id="top"]/div[2]/a[3]/span')
        price = await page.text_content('//*[@id="top"]/div[1]/div/div[2]/div[1]/span[1]')
        mcap = await page.text_content('//*[@id="top-ratios"]/li[1]/span[2]/span')
        book_value = await page.text_content('//*[@id="top-ratios"]/li[5]/span[2]/span')
        intrinsic_value = await page.text_content('//*[@id="top-ratios"]/li[11]/span[2]/span')
        stock_pe = await page.text_content('//*[@id="top-ratios"]/li[4]/span[2]/span')
        industry_pe = await page.text_content('//*[@id="top-ratios"]/li[10]/span[2]/span')
        debt = await page.text_content('//*[@id="top-ratios"]/li[14]/span[2]/span')
        int_coverage = await page.text_content('//*[@id="top-ratios"]/li[23]/span[2]/span')
        promoter_holding = await page.text_content('//*[@id="top-ratios"]/li[12]/span[2]/span')
        change_in_prom_hold = await page.text_content('//*[@id="top-ratios"]/li[13]/span[2]/span')
        fii_holding = await page.text_content('//*[@id="top-ratios"]/li[18]/span[2]/span')
        change_in_fii_holding = await page.text_content('//*[@id="top-ratios"]/li[19]/span[2]/span')
        dii_holding = await page.text_content('//*[@id="top-ratios"]/li[20]/span[2]/span')
        change_in_dii_holding = await page.text_content('//*[@id="top-ratios"]/li[21]/span[2]/span')
        debt_to_equity = await page.text_content('//*[@id="top-ratios"]/li[22]/span[2]/span')
        high_52week = await page.text_content('//*[@id="top-ratios"]/li[3]/span[2]/span[1]')
        low_52week = await page.text_content('//*[@id="top-ratios"]/li[3]/span[2]/span[2]')

        return (symbol, price, mcap, book_value, intrinsic_value, stock_pe,
        industry_pe, debt, int_coverage, promoter_holding,
        change_in_prom_hold, fii_holding, change_in_fii_holding,
        dii_holding, change_in_dii_holding, debt_to_equity,
        high_52week, low_52week)

        # else:
        #     print('element does not exists')
    except:
        print("detail not found")
        symbol = price = mcap = book_value = intrinsic_value = stock_pe = None
        industry_pe = debt = int_coverage = promoter_holding = None
        change_in_prom_hold = fii_holding = change_in_fii_holding = None
        dii_holding = change_in_dii_holding = debt_to_equity = None
        high_52week = low_52week = None

        return (symbol, price, mcap, book_value, intrinsic_value, stock_pe,
        industry_pe, debt, int_coverage, promoter_holding,
        change_in_prom_hold, fii_holding, change_in_fii_holding,
        dii_holding, change_in_dii_holding, debt_to_equity,
        high_52week, low_52week)
    # Loop through each XPath expression and variable name

    # # Define XPath expressions
    # xpath_symbol = '//*[@id="top"]/div[2]/a[2]/span'
    # xpath_price = '//*[@id="top"]/div[1]/div/div[2]/div[1]/span[1]'
    # xpath_mcap = '//*[@id="top-ratios"]/li[1]/span[2]/span'
    # xpath_book_value = '//*[@id="top-ratios"]/li[5]/span[2]/span'
    # xpath_intrinsic_value = '//*[@id="top-ratios"]/li[11]/span[2]/span'
    # xpath_stock_pe = '//*[@id="top-ratios"]/li[4]/span[2]/span'
    # xpath_industry_pe = '//*[@id="top-ratios"]/li[10]/span[2]/span'
    # xpath_debt = '//*[@id="top-ratios"]/li[14]/span[2]/span'
    # xpath_int_coverage = '//*[@id="top-ratios"]/li[23]/span[2]/span'
    # xpath_promoter_holding = '//*[@id="top-ratios"]/li[12]/span[2]/span'
    # xpath_change_in_prom_hold = '//*[@id="top-ratios"]/li[13]/span[2]/span'
    # xpath_fii_holding = '//*[@id="top-ratios"]/li[18]/span[2]/span'
    # xpath_change_in_fii_holding = '//*[@id="top-ratios"]/li[19]/span[2]/span'
    # xpath_dii_holding = '//*[@id="top-ratios"]/li[20]/span[2]/span'
    # xpath_change_in_dii_holding = '//*[@id="top-ratios"]/li[21]/span[2]/span'
    # xpath_debt_to_equity = '//*[@id="top-ratios"]/li[22]/span[2]/span'
    # xpath_high_52week = '//*[@id="top-ratios"]/li[3]/span[2]/span[1]'
    # xpath_low_52week = '//*[@id="top-ratios"]/li[3]/span[2]/span[2]'

    # # Initialize variables to store scraped data
    # symbol = price = mcap = book_value = intrinsic_value = stock_pe = None
    # industry_pe = debt = int_coverage = promoter_holding = None
    # change_in_prom_hold = fii_holding = change_in_fii_holding = None
    # dii_holding = change_in_dii_holding = debt_to_equity = None
    # high_52week = low_52week = None

    # # Define a list of tuples for easy iteration
    # elements_to_scrape = [
    #     (xpath_symbol, 'NSE', 'symbol'),
    #     (xpath_price, '₹', 'price'),
    #     (xpath_mcap, 'Market Cap', 'mcap'),
    #     (xpath_book_value, 'Book Value', 'book_value'),
    #     (xpath_intrinsic_value, 'Intrinsic Value', 'intrinsic_value'),
    #     (xpath_stock_pe, 'Industry PE', 'stock_pe'),
    #     (xpath_industry_pe, 'Industry PE', 'industry_pe'),
    #     (xpath_debt, 'Debt', 'debt'),
    #     (xpath_int_coverage, 'Int Coverage', 'int_coverage'),
    #     (xpath_promoter_holding, 'Promoter holding', 'promoter_holding'),
    #     (xpath_change_in_prom_hold, 'Change in Prom Hold', 'change_in_prom_hold'),
    #     (xpath_fii_holding, 'FII holding', 'fii_holding'),
    #     (xpath_change_in_fii_holding, 'Chg in FII Hold', 'change_in_fii_holding'),
    #     (xpath_dii_holding, 'DII holding', 'dii_holding'),
    #     (xpath_change_in_dii_holding, 'Chg in DII Hold', 'change_in_dii_holding'),
    #     (xpath_debt_to_equity, 'Debt to equity', 'debt_to_equity'),
    #     (xpath_high_52week, 'High', 'high_52week'),
    #     (xpath_low_52week, 'High', 'low_52week')
    # ]

    # # Loop through each XPath expression and variable name
    # for xpath, label, var_name in elements_to_scrape:
    #     try:
    #         # element = await page.xpath(xpath)
    #         # element = page.locator('xpath=' + xpath).wait_for
    #         element = page.query_selector(xpath)
    #         if element:
    #             # If element exists, extract its text content
    #             # globals()[var_name] = await element.text()
    #             tt = await page.text_content(xpath)
    #             print(f'tt - {tt}')
    #             globals()[var_name] = tt
    #         else:
    #             # Handle case where element does not exist (optional)
    #             globals()[var_name] = None  # or any default value you want
    #     except Exception as e:
    #         print(f"Error while scraping {var_name}: {str(e)}")
    #         globals()[var_name] = None

    # # Return all scraped data
    # return (symbol, price, mcap, book_value, intrinsic_value, stock_pe,
    #         industry_pe, debt, int_coverage, promoter_holding,
    #         change_in_prom_hold, fii_holding, change_in_fii_holding,
    #         dii_holding, change_in_dii_holding, debt_to_equity,
    #         high_52week, low_52week)
    # Initialize variables to store scraped data
    # symbol = price = mcap = book_value = intrinsic_value = stock_pe = None
    # industry_pe = debt = int_coverage = promoter_holding = None
    # change_in_prom_hold = fii_holding = change_in_fii_holding = None
    # dii_holding = change_in_dii_holding = debt_to_equity = None
    # high_52week = low_52week = None

    # for xpath, var_name in elements_to_scrape:
    #     # element = await page.query_selector(xpath)
    #     element = page.xpath(xpath)
    #     if element:
    #         # If element exists, extract its text content
    #         globals()[var_name] = await element.text_content()
    #     else:
    #         # Handle case where element does not exist (optional)
    #         globals()[var_name] = None  # or any default value you want

    # return symbol, price, mcap, book_value, intrinsic_value, stock_pe, industry_pe, debt, int_coverage, promoter_holding, change_in_prom_hold, fii_holding, change_in_fii_holding, dii_holding, change_in_dii_holding, debt_to_equity, high_52week, low_52week

async def main():
    # Read stock symbols from the input CSV file
    symbols_df = pd.read_csv(input_csv)
    symbols = symbols_df['SYMBOL'].tolist()
    urls = []
    for s in symbols:
        url = "https://www.screener.in/company/" + s
        # print(url)
        urls.append(url)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Perform login
        await login(page)
        # print(urls)
        # Prepare the output CSV file
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['symbol', 'price', 'mcap', 'book_value', 'intrinsic_value', 'stock_pe', 'industry_pe', 'debt', 'int_coverage', 'promoter_holding', 'change_in_prom_hold', 'fii_holding', 'change_in_fii_holding', 'dii_holding', 'change_in_dii_holding', 'debt_to_equity', 'high_52week', 'low_52week'])
        # Scrape data from each URL
        for url in urls:
            # Check if session is still valid
            # print(f'url {url}')
            retry_count = 0
            while retry_count < 5:  # Retry up to 5 times
                try:
                    await page.goto(url)
                    if page.url == 'https://www.screener.in/login/':
                        print('Session expired. Logging in again...')
                        await login(page)
                        await page.goto(url)
                    symbol, price, mcap, book_value, intrinsic_value, stock_pe, industry_pe, debt, int_coverage, promoter_holding, change_in_prom_hold, fii_holding, change_in_fii_holding, dii_holding, change_in_dii_holding, debt_to_equity, high_52week, low_52week = await scrape_data(page, url)
                    print(f'fetched data from {url}: {symbol} - {price} - {intrinsic_value}')
                    # Append the result to the output CSV file
                    with open(output_csv, mode='a', newline='',  encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([url, price, mcap, book_value, intrinsic_value, stock_pe, industry_pe, debt, int_coverage, promoter_holding, change_in_prom_hold, fii_holding, change_in_fii_holding, dii_holding, change_in_dii_holding, debt_to_equity, high_52week, low_52week])
                    # Delay between requests to avoid rate limiting
                    time.sleep(4)
                    break
                except TimeoutError:
                    retry_count += 1
                    print(f'Request timed out. Retrying {retry_count}/5...')
                    time.sleep(10)  # Wait before retrying

        await browser.close()

asyncio.run(main())
