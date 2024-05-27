import requests
from bs4 import BeautifulSoup

def fetch_category_links(url="https://en.wikibooks.org/wiki/Category:Recipes"):
    """
    Fetch category links from a Wikibooks recipe category page.

    Args:
        url (str): The URL to fetch the recipe categories from. Default is the Wikibooks recipe category page.

    Returns:
        list: A list of strings, each representing a category link URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    category_links = []

    toc = soup.find('table', {'id': 'toc'})
    if toc:
        links = toc.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                category_links.append(href)

    # Remove the first two navigation links if present
    category_links = category_links[2:] if len(category_links) > 2 else category_links
    return category_links

def fetch_recipe_links(url):
    """
    Fetch all recipe links from a given category URL.

    Args:
        url (str): Specific category URL to fetch recipe links from.

    Returns:
        list: A list of URLs, each pointing to a specific recipe within the category.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)

    recipe_links = []
    for link in links:
        if '/wiki/Cookbook:' in link['href']:
            full_url = 'https://en.wikibooks.org' + link['href']
            recipe_links.append(full_url)

    recipe_links = [link for link in recipe_links if not link.endswith('Table_of_Contents')]
    if recipe_links:
        recipe_links.pop(0)  # Remove a possible navigation link

    return recipe_links

def scrape_recipe_and_save(url, category_name):
    """
    Scrape recipe details from a specific URL and save them to a text file.

    Args:
        url (str): Specific URL of the recipe to scrape.
        category_name (str): The name of the category for organizational purposes (not used in current function).

    Returns:
        dict: A dictionary containing the recipe details such as title, ingredients, procedure, and notes.
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    recipe = {
        'title': '',
        'ingredients': [],
        'procedure': [],
        'notes': []
    }

    title = soup.find('h1').text.replace('Cookbook:', '').strip()
    recipe['title'] = title

    ingredients_section = soup.find(lambda tag: tag.name == 'h2' and 'Ingredients' in tag.text)
    if ingredients_section:
        for ul in ingredients_section.find_next_siblings('ul', limit=1):
            for li in ul.find_all('li'):
                recipe['ingredients'].append(li.text.strip())

    procedure_section = soup.find(lambda tag: tag.name == 'h2' and 'Procedure' in tag.text)
    if procedure_section:
        for ol in procedure_section.find_next_siblings('ol', limit=1):
            for li in ol.find_all('li'):
                recipe['procedure'].append(li.text.strip())

    notes_section = soup.find(lambda tag: tag.name == 'h2' and 'Notes, tips, and variations' in tag.text)
    if notes_section:
        for ul in notes_section.find_next_siblings('ul', limit=1):
            for li in ul.find_all('li'):
                recipe['notes'].append(li.text.strip())

    file_name = f"{title.replace(' ', '_')}.txt"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(f"Title: {recipe['title']}\n\n")
        f.write("Ingredients:\n")
        for ingredient in recipe['ingredients']:
            f.write(f"- {ingredient}\n")
        f.write("\nProcedure:\n")
        for step in recipe['procedure']:
            f.write(f"- {step}\n")
        f.write("\nNotes, Tips, and Variations:\n")
        for note in recipe['notes']:
            f.write(f"- {note}\n")

    print(f"Saved: {file_name}")
    return recipe

# Main script
if __name__ == "__main__":
    category_urls = fetch_category_links()
    for category_url in category_urls:
        category_name = category_url.split('&from=')[1]
        recipe_urls = fetch_recipe_links(category_url)
        for recipe_url in recipe_urls:
            scrape_recipe_and_save(recipe_url, category_name)
