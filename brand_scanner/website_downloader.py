import requests
from bs4 import BeautifulSoup
import os
import re

def get_page_urls(url, max_pages:(int | None)):
    base_url = url
    stack = [base_url]
    urls = set()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    
    while stack:
        url = stack.pop()
        response = requests.get(url, headers={'User-Agent': user_agent})
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            url = link['href']
            if not url.startswith('http') or base_url not in url or url in urls:
                continue
            urls.add(url)
            stack.append(url)
            if max_pages and len(urls) == max_pages:
                return urls
    return urls

def create_file_path(url:str) -> None:
    path_comps = url.split('/')
    if path_comps[-1] == '':
        path_comps.pop()
    directory = os.path.dirname(os.getcwd())
    directory = os.path.join(directory, 'data')
    
    for comp in path_comps[:-1]:
        directory = os.path.join(directory, comp)
        if not os.path.exists(directory):
            os.makedirs(directory)
    file_name = path_comps[-1] + '.md'
    file_path = os.path.join(directory, file_name)
    return file_path

def save_pages(homepage_url:str, max_pages:int=None):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    urls = get_page_urls(homepage_url, max_pages)
    for url in urls:
        response = requests.get(url, headers={'User-Agent': user_agent})
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.content, 'html.parser')
        
        subs = {'https://www.': '', '.': '_'}
        for orig, sub in subs.items():
            url = url.replace(orig, sub)
            
        file_path = create_file_path(url)
                
        with open(file_path, 'w') as file:
            if not soup.main:
                continue
            text = soup.main.text
            text = re.sub(r'(\n){2,}|(\t){2,}', r'\n', text)
            markdown = f'# {soup.title.string}\n\n{text}'
            file.write(markdown)

save_pages('https://www.gmmb.com', 150)