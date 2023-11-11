import re
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        return None

def find_internal_links(soup, base_url):
    links = []
    for link in soup.find_all('a', href=True):
        link = urljoin(base_url, link['href'])
        if link.startswith(base_url):
            links.append(link)
    return links

def extract_emails(soup):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text_content = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'a', 'span'])])
    emails = re.findall(email_pattern, text_content)
    return emails

def extract_mailto_links(soup, base_url):
    mailto_links = []
    
    # Extraer de las etiquetas 'a' (enlaces)
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('mailto:'):
            mailto_links.append(href[7:])  # Strip 'mailto:' prefix
        else:
            full_url = urljoin(base_url, href)
            if urlparse(full_url).scheme == 'mailto':
                mailto_links.append(urlparse(full_url).path)

    # Extraer de las etiquetas 'p' (párrafos)
    for paragraph in soup.find_all('p'):
        text_content = paragraph.get_text()
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
        mailto_links.extend(emails)

    # Extraer de las etiquetas 'span'
    for span in soup.find_all('span'):
        text_content = span.get_text()
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
        mailto_links.extend(emails)

    return mailto_links

def main():
    base_url = 'https://santiago.soñora.com'  # Reemplaza con la URL de tu sitio web
    visited_links = set()
    links_to_visit = [base_url]
    unique_emails = set()

    with open('emails.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Email'])

        while links_to_visit:
            link = links_to_visit.pop(0)
            if link not in visited_links:
                print(f'Scraping {link}...')
                try:
                    soup = scrape_page(link)
                    if soup:
                        visited_links.add(link)
                        links_to_visit.extend(find_internal_links(soup, base_url))
                        
                        # Extraer direcciones de correo electrónico de múltiples fuentes
                        emails = extract_emails(soup)
                        mailto_links = extract_mailto_links(soup, base_url)
                        
                        # Filtrar direcciones no únicas y no encontradas previamente
                        new_emails = set(emails + mailto_links) - unique_emails
                        unique_emails.update(new_emails)
                        
                        # Escribir las direcciones de correo electrónico al archivo CSV
                        for email in new_emails:
                            writer.writerow([email])
                except Exception as e:
                    print(f'Error scraping {link}: {e}')

if __name__ == '__main__':
    main()
