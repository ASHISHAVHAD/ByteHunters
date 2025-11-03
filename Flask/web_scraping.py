import requests
from bs4 import BeautifulSoup

def scrape_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text from common article content tags
        text_elements = soup.find_all(['p', 'article'])
        
        full_text = []
        for element in text_elements:
            text = element.get_text(separator=" ", strip=True)
            if len(text) > 40:  # Filter out small/irrelevant chunks
                full_text.append(text)

        article_text = "\n".join(full_text)
        return article_text

    except Exception as e:
        print(f"Error: {e}")
        return ""


if __name__ == "__main__":
    url = input("Enter a news/article URL: ")
    article_content = scrape_article_text(url)

    print("\n--- Article Content ---\n")
    print(article_content)
