import requests, csv, os, zipfile, io
# TEMPLATE: Replace resource URLs with exact data source links from data.gov.au or ABS.
# This script demonstrates how to download CSV data and merge into suburb_medians_sample.csv
DATA_SOURCES = [
    # Example: ('https://example.com/nsw_medians.csv', 'NSW'),
]

OUT_CSV = 'suburb_medians_sample.csv'
def download_and_merge():
    rows = []
    for url, state in DATA_SOURCES:
        print('Would download:', url, 'for state', state)
        # resp = requests.get(url)
        # content = resp.content.decode('utf-8')
        # parse CSV and extend rows
    # For now this is a template; user must populate DATA_SOURCES with real dataset download URLs.
    print('Template complete. Populate DATA_SOURCES with real data source URLs from data.gov.au, ABS, or provider APIs.')
if __name__ == '__main__':
    download_and_merge()
