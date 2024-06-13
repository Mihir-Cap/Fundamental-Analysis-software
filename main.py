from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil
import pandas as pd
from datetime import datetime

# Function to download CSV using Selenium
def download_csv(url, download_dir, filename):
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': download_dir}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Delete the existing file if it exists
        file_path = os.path.join(download_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted existing file: {file_path}")

        driver.get(url)
        time.sleep(5)
        wait = WebDriverWait(driver, 20)
        parent_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dt-buttons.btn-group")))
        time.sleep(2)
        button_tags = parent_container.find_elements(By.TAG_NAME, 'button')

        for button in button_tags:
            if 'CSV' in button.text:
                csv_button = button
                break
        else:
            print("CSV Button not found")
            return

        try:
            csv_button.click()
        except Exception as click_exception:
            driver.execute_script("arguments[0].click();", csv_button)
        
        time.sleep(10)

        files = os.listdir(download_dir)
        paths = [os.path.join(download_dir, basename) for basename in files]
        latest_file = max(paths, key=os.path.getctime)
        new_file_path = os.path.join(download_dir, filename)
        shutil.move(latest_file, new_file_path)
        print(f"File renamed to {new_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

# Function to read stock names from a CSV or Excel file and return a DataFrame
def read_stock_names(file_path, file_name, symbol_column):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format for file '{file_path}'")
    
    if symbol_column not in df.columns:
        raise ValueError(f"The file '{file_path}' does not contain a '{symbol_column}' column.")
    
    df.rename(columns={symbol_column: 'SYMBOL'}, inplace=True)
    df['File'] = file_name
    return df

# Function to delete the previous output file if it exists
def delete_output_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# Main logic to download CSV files and combine data
def main():
    download_directory = os.path.dirname(os.path.abspath(__file__))
    
    url1 = 'https://chartink.com/screener/mihir-rocket-base'
    url2 = 'https://chartink.com/screener/mihir-vcp'
    
    download_csv(url1, download_directory, 'Mihir RB.csv')
    download_csv(url2, download_directory, 'Mihir VCP.csv')
    
    file1 = 'Mihir RB.csv'
    file2 = 'swing_trading_output.xlsx'
    file3 = 'Mihir VCP.csv'
    
    output_file = 'common_stocks.xlsx'
    
    try:
        df1 = read_stock_names(file1, 'RB', 'Symbol')
        df2 = read_stock_names(file2, 'Swing Trading', 'SYMBOL')
        df3 = read_stock_names(file3, 'VCP', 'Symbol')
        
        combined_df = pd.concat([df1, df2, df3])
        
        pivot_df = combined_df.pivot_table(index='SYMBOL', columns='File', aggfunc='size', fill_value=0)
        
        common_all_three = pivot_df[(pivot_df['RB'] == 1) & (pivot_df['Swing Trading'] == 1) & (pivot_df['VCP'] == 1)]
        common_file1_file2 = pivot_df[(pivot_df['RB'] == 1) & (pivot_df['Swing Trading'] == 1) & (pivot_df['VCP'] == 0)]
        common_file2_file3 = pivot_df[(pivot_df['RB'] == 0) & (pivot_df['Swing Trading'] == 1) & (pivot_df['VCP'] == 1)]
        common_file1_file3 = pivot_df[(pivot_df['RB'] == 1) & (pivot_df['Swing Trading'] == 0) & (pivot_df['VCP'] == 1)]
        
        result_df = pd.concat([common_all_three, common_file1_file2, common_file2_file3, common_file1_file3])
        result_df.reset_index(inplace=True)
        
        current_time = datetime.now()
        result_df['Scan Date'] = current_time.strftime('%Y-%m-%d')
        result_df['Scan Time'] = current_time.strftime('%H:%M:%S')
        
        delete_output_file(output_file)
        result_df.to_excel(output_file, index=False)
        
        print(f'Common stock names with file details have been saved to {output_file}')
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
