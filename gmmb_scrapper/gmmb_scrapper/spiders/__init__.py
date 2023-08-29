from scrapy.spiders import SitemapSpider
from markdownify import markdownify as md
import os

def create_file_path(url:str, base_dir:str, output_type:str='.md') -> None:
    subs = {'https://www.': '', '.': '_'}
    for orig, sub in subs.items():
        url = url.replace(orig, sub)
    
    path_comps = url.split('/')
    if path_comps[-1] == '':
        path_comps.pop()
    directory = base_dir
    directory = os.path.join(directory, 'data')
    
    for comp in path_comps[:-1]:
        directory = os.path.join(directory, comp)
        if not os.path.exists(directory):
            os.makedirs(directory)
    file_name = path_comps[-1] + output_type
    file_path = os.path.join(directory, file_name)
    return file_path

class GmmbSpider(SitemapSpider):
    name = "gmmb_sitemap"
    sitemap_urls = ['https://www.gmmb.com/sitemap_index.xml']
    
    def parse(self, response):
        # Your parsing logic here
        base_dir = '/Users/blakevanfleteren/Programs/GitHub/brand_scanner/'
        filename = create_file_path(response.url, base_dir, '.md')
        with open(filename, 'w') as file:
            content = response.css('main').get()
            content = md(content)
            file.write(content)
        self.log(f'Saved file {filename}')
        