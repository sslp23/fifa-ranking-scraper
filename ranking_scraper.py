import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import os

headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

def extract_select_options(url):
    """
    Extract all options from a select element in the given HTML.
    
    Args:
        html_string (str): HTML string containing the select element
    
    Returns:
        list: List of dictionaries with 'value' and 'text' for each option
    """
    response = requests.get(url, headers=headers)
    html_string = response.text
    soup = BeautifulSoup(html_string, 'html.parser')
    
    # Find the select element (you can adjust the selector as needed)
    select = soup.find('select', {'name': 'datum'})
    
    if not select:
        # Try to find any select element if the specific one isn't found
        select = soup.find('select')
    
    if not select:
        return []
    
    # Extract all option elements
    options = []
    for option in select.find_all('option'):
        option_data = {
            'value': option.get('value', ''),
        }
        options.append(option_data)
    
    return options

def parse_fifa_ranking_table(soup):
    """
    Parse the FIFA ranking table and extract all values.
    
    Args:
        html_string (str): HTML string containing the table
    
    Returns:
        list: List of dictionaries with extracted data
        pandas.DataFrame: DataFrame with the data (optional)
    """
    # Find the table
    table = soup.find('table', {'class': 'items'})
    
    if not table:
        return []
    
    # Extract headers
    headers = []
    thead = table.find('thead')
    if thead:
        for th in thead.find_all('th'):
            header_text = th.get_text(strip=True)
            # Clean up header names
            if header_text == '#':
                headers.append('rank')
            elif header_text.lower() == 'nation':
                headers.append('nation')
            elif header_text.lower() == 'confederation':
                headers.append('confederation')
            elif header_text.lower() == 'points':
                headers.append('points')
            else:
                headers.append(header_text.lower())
    
    # Extract rows data
    data = []
    tbody = table.find('tbody')
    
    if tbody:
        for row in tbody.find_all('tr'):
            row_data = {}
            cells = row.find_all('td')
            
            for i, cell in enumerate(cells):
                if i < len(headers):
                    cell_text = cell.get_text(strip=True)
                    
                    # Parse specific columns
                    if headers[i] == 'rank':
                        # Extract rank number (remove arrow indicator)
                        rank_parts = cell_text.split()
                        row_data[headers[i]] = rank_parts[0] if rank_parts else cell_text
                        
                        # Extract previous position from title attribute
                        arrow_span = cell.find('span')
                        if arrow_span and arrow_span.has_attr('title'):
                            title = arrow_span['title']
                            if 'Previous position:' in title:
                                prev_pos = title.replace('Previous position:', '').strip()
                                row_data['previous_position'] = prev_pos
                        
                        # Extract arrow direction (green=up, red=down)
                        if arrow_span:
                            class_names = arrow_span.get('class', [])
                            if 'green-arrow-ten' in class_names:
                                row_data['trend'] = 'up'
                            elif 'red-arrow-ten' in class_names:
                                row_data['trend'] = 'down'
                            else:
                                row_data['trend'] = 'stable'
                    
                    elif headers[i] == 'nation':
                        # Extract nation name and flag URL
                        nation_link = cell.find('a')
                        if nation_link:
                            row_data['nation'] = nation_link.get_text(strip=True)
                            row_data['nation_url'] = nation_link.get('href', '')
                        
                        # Extract flag image URL
                        flag_img = cell.find('img')
                        if flag_img:
                            row_data['flag_url'] = flag_img.get('src', '')
                            row_data['nation_full_name'] = flag_img.get('title', '')
                    
                    elif headers[i] == 'confederation':
                        row_data[headers[i]] = cell_text
                    
                    elif headers[i] == 'points':
                        row_data[headers[i]] = cell_text
                
            data.append(row_data)
    
    return pd.DataFrame(data)

def extract_table_date(date):
    url = f"https://www.transfermarkt.com/statistik/weltrangliste/statistik/stat/datum/{date['value']}"


    response = requests.get(url, headers=headers)
    html_string = response.text
    soup = BeautifulSoup(html_string, 'html.parser')

    total_pages = 1
    last_page_li = soup.find('li', {'class': 'tm-pagination__list-item tm-pagination__list-item--icon-last-page'})
    if last_page_li and last_page_li.find('a'):
        total_pages = int(last_page_li.find('a')['href'].split('/')[-1])
    else:
        # If last page button is not there, find the highest page number from the links
        page_links = soup.select('.tm-pagination__list-item a')
        pages = [int(a['href'].split('/')[-1]) for a in page_links if a.get('href') and a['href'].split('/')[-1].isdigit()]
        if pages:
            total_pages = max(pages)

    dfs = []
    for i in range(1, total_pages+1, 1):
        page_url = f"https://www.transfermarkt.com/statistik/weltrangliste/statistik/stat/datum/{date['value']}/plus/0/galerie/0/page/{i}"
        response = requests.get(page_url, headers=headers)
        html_string = response.text
        soup = BeautifulSoup(html_string, 'html.parser')

        df = parse_fifa_ranking_table(soup)

        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    if len(dfs)>1:
        full_df = pd.concat(dfs, ignore_index=True)
        full_df['rank_date'] = [date['value']]*len(full_df)
        return full_df
    else:
        return pd.DataFrame()
    

if __name__ == "__main__":
    output_csv_path = 'data/resulting_data.csv'
    
    os.makedirs('data', exist_ok=True)
    
    existing_dates = set()
    if os.path.exists(output_csv_path):
        try:
            existing_df = pd.read_csv(output_csv_path)
            if 'rank_date' in existing_df.columns:
                existing_dates = set(existing_df['rank_date'].astype(str))
        except (pd.errors.EmptyDataError, FileNotFoundError):
            pass  # File is empty or not found, treat as no existing dates

    url = "https://www.transfermarkt.com/statistik/weltrangliste/statistik/stat/plus/0/galerie/0?datum=1994-03-15"
    possible_dates = extract_select_options(url)
    
    dates_to_process = [d for d in possible_dates if str(d['value']) not in existing_dates]

    if not dates_to_process:
        print("All ranking dates are already present in data/resulting_data.csv.")
    else:
        print(f"Found {len(dates_to_process)} new ranking dates to process.")
        
        file_exists_and_has_content = os.path.exists(output_csv_path) and os.path.getsize(output_csv_path) > 0

        for p in tqdm(dates_to_process):
            
            df = extract_table_date(p)
            if not df.empty:
                df.to_csv(output_csv_path, mode='a', header=not file_exists_and_has_content, index=False)
                file_exists_and_has_content = True
    
