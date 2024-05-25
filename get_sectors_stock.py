import asyncio
import csv
import pandas as pd
from playwright.async_api import async_playwright

async def fetch_sector(stock_symbol, page):
    # Fill in the search form with the stock symbol
    await page.fill('input#navbar-desktop-search', stock_symbol)

    # Wait for the auto-suggestions to appear
    await page.wait_for_selector('.ui-menu-item', timeout=5000)

    # Select the first suggestion
    await page.click('.ui-menu-item')

    # Wait for the page to load
    await page.wait_for_load_state('networkidle')

    # Scrape the sector information
    sector_xpath = '/html/body/main/div[4]/div[1]/div[1]/div/ol/li[2]/a/span'
    sector_element = await page.query_selector(f'xpath={sector_xpath}')
    sector_text = await sector_element.inner_text() if sector_element else 'N/A'

    # Scrape the industry information
    subsector_xpath = '/html/body/main/div[4]/div[1]/div[1]/div/ol/li[3]/a/span'
    subsector_element = await page.query_selector(f'xpath={subsector_xpath}')
    subsector_text = await subsector_element.inner_text() if subsector_element else 'N/A'

    # Scrape the Company Name information
    companyname_xpath = '/html/body/main/div[4]/div[1]/div[1]/div/ol/li[4]/a/span'
    companyname_element = await page.query_selector(f'xpath={companyname_xpath}')
    companyname_text = await companyname_element.inner_text() if companyname_element else 'N/A'

    return sector_text, subsector_text, companyname_text

async def main():
    input_csv = 'input_symbols.csv'
    output_csv = 'output_results.csv'

    # Read stock symbols from the input CSV file
    symbols_df = pd.read_csv(input_csv)
    symbols = symbols_df['symbol'].tolist()

    # Prepare the output CSV file
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['symbol', 'sector', 'subsector', 'name'])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set headless=True for headless mode
        page = await browser.new_page()

        # Navigate to the Trendlyne homepage
        await page.goto("https://trendlyne.com/")

        for symbol in symbols:
            try:
                sector, subsector, name = await fetch_sector(symbol, page)
                print(f"Symbol: {symbol} | Sector: {sector} | Subsector: {subsector} | Name: {name}")

                # Append the result to the output CSV file
                with open(output_csv, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([symbol, sector, subsector, name])
            except Exception as e:
                print(f"Failed to fetch data for symbol {symbol}: {e}")

        # Close the browser
        await browser.close()

# Run the main function
asyncio.run(main())
