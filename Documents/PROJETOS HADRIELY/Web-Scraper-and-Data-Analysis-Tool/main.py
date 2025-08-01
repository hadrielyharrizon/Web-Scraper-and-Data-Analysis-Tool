from scraper.scraper_main import get_title
from analysis.analyze import analyze_data

def main():
    url = 'https://example.com'
    title = get_title(url)
    print('Título capturado:', title)
    analyze_data()

if __name__ == '__main__':
    main()
