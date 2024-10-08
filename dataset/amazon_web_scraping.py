import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import re

product_link = []
review_link = []
next_page_link = []

dataset =   {
                'product_title': [], 
                'user_name': [], 
                'rating': [], 
                'review': [],
                'review_date': []
            }

unique_reviews = set()

# Function to make requests with retry logic
def make_request(url, headers, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 503:
                print("503 Error: Service Unavailable. Retrying...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                retries += 1
            else:
                print(response)
                return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            retries += 1
            time.sleep(5)  # Wait before retrying
    return None  # Return None if all retries fail



# get title of the product
def get_title(soup):
    try:
        raw_title = soup.find('a', attrs={'data-hook':'product-link'}).text.strip()
        cleaned_title = re.sub(r'[^\w\s]', '', raw_title).strip()
        words = cleaned_title.split()
        title = ' '.join(words[:3])
        print(title)
    except AttributeError:
        title = ""
    return title



# get reviewer names
def get_users(soup):
    users = []
    try:
        user_tags = soup.find_all('span', attrs={'class': 'a-profile-name'})
        for tag in user_tags:
            user_name = tag.text.strip()
            cleaned_name = re.sub(r'[^\w\s]', '', user_name).strip()
            words = cleaned_name.split()
            final_user = ' '.join(words[:3])
            users.append(final_user)
    except AttributeError:
        pass
    return users



# get ratings
def get_ratings(soup):
    ratings = []
    try:
        rating_tags = soup.find_all('i', {'data-hook': 'review-star-rating'})
        for tag in rating_tags:
            ratings.append(tag.text.replace('out of 5 stars', '').strip())
    except AttributeError:
        pass
    return ratings



# get reviews
def get_reviews(soup):
    reviews = []
    try:
        review_tags = soup.find_all('span', {'data-hook': 'review-body'})
        for tag in review_tags:
            review = tag.find('span')
            reviews.append(review.text.strip())
    except AttributeError:
        pass
    return reviews



# Get Review Dates
def get_review_dates(soup):
    dates = []
    try:
        date_tags = soup.find_all('span', attrs={'data-hook': 'review-date'})
        for tag in date_tags:
            date_text = tag.text.strip()
            if 'on ' in date_text:
                date_text = date_text.split('on ')[-1]
            dates.append(date_text)
    except AttributeError:
        pass
    return dates



URLS = ['https://www.amazon.com/s?k=smartphone&i=mobile&rh=n%3A7072561011%2Cp_123%3A253649&dc&crid=1Z0X66VU1LOIU&qid=1725834058&refresh=2&rnid=85457740011&sprefix=%2Caps%2C340&ref=sr_nr_p_123_4&ds=v1%3Ancgcu1%2BVo3awjGPzBuGfG1xOJmgEJSQWS4s9%2Fg%2Bt%2BLw',
        'https://www.amazon.com/s?k=smartphone&i=mobile&rh=n%3A7072561011%2Cp_123%3A253649&dc&page=2&crid=1Z0X66VU1LOIU&qid=1725834063&refresh=2&rnid=85457740011&sprefix=%2Caps%2C340&ref=sr_pg_2',
        'https://www.amazon.com/s?k=smartphone&i=mobile&rh=n%3A7072561011%2Cp_123%3A46655&dc&crid=1Z0X66VU1LOIU&qid=1725834127&refresh=2&rnid=85457740011&sprefix=%2Caps%2C340&ref=sr_nr_p_123_1&ds=v1%3A0VOcg%2Fg8gbeG5rDwzolJajaNeZa%2BgOGYOHD22qXYfz0',
        'https://www.amazon.com/s?k=smartphone&i=mobile&rh=n%3A7072561011%2Cp_123%3A46655&dc&page=2&crid=1Z0X66VU1LOIU&qid=1725834130&refresh=2&rnid=85457740011&sprefix=%2Caps%2C340&ref=sr_pg_2']


HEADERS_LIST = [
    {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        'Cache-Control': 'no-cache',
        'Origin': 'https://www.amazon.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.amazon.com/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    },
]



# Scraping Product links from search results
for URL in URLS:
    headers = random.choice(HEADERS_LIST)
    webpage = make_request(URL, headers)
    if webpage:
        soup = BeautifulSoup(webpage.content, 'html.parser')
        links = soup.find_all('a', attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        for link in links:
            href = link.get('href')
            if href and href not in product_link:
                product_link.append(href)
    time.sleep(random.uniform(2, 5))



# Scraping Review Links from Product links
for link in product_link:
    headers = random.choice(HEADERS_LIST)
    new_webpage = make_request('https://www.amazon.com' + link, headers)
    if new_webpage:
        new_soup = BeautifulSoup(new_webpage.content, 'html.parser')
        comment_tags = new_soup.find_all('a', attrs={'data-hook': 'see-all-reviews-link-foot'})
        for tag in comment_tags:
            href = tag.get('href')
            if href and href not in review_link:
                review_link.append(href)
    time.sleep(random.uniform(2, 5))



# Scraping Next Page Links from Review links
for link in review_link:
    headers = random.choice(HEADERS_LIST)
    new_webpage = make_request('https://www.amazon.com' + link, headers)  
    if new_webpage:
        soup = BeautifulSoup(new_webpage.content, 'html.parser')
        pagination = soup.find('li', class_='a-last')
        if pagination:
            next_page_tag = pagination.find('a')  # Find the <a> tag inside <li class='a-last'>
            if next_page_tag:
                href = next_page_tag.get('href')
                if href and href not in next_page_link:
                    next_page_link.append(href)
    time.sleep(random.uniform(2, 5)) 



# Function to increment page number in the URL
def generate_next_page_links(base_link, start_page, max_pages):
    next_page_links = []
    for page_number in range(start_page, max_pages + 1):
        new_link = base_link.replace('cm_cr_arp_d_paging_btm_2', f'cm_cr_arp_d_paging_btm_{page_number}')
        new_link = new_link.replace('pageNumber=2', f'pageNumber={page_number}')
        next_page_links.append(new_link)
    return next_page_links



# Scraping product details from multiple pages
for base_link in next_page_link:
    page_links = generate_next_page_links(base_link, 1, 10)
    
    for link in page_links:
        headers = random.choice(HEADERS_LIST)
        new_webpage = make_request('https://www.amazon.com' + link, headers)
        if new_webpage:
            new_soup = BeautifulSoup(new_webpage.content, 'html.parser')
            product_title = get_title(new_soup)
            users = get_users(new_soup)
            ratings = get_ratings(new_soup)
            reviews = get_reviews(new_soup)
            dates = get_review_dates(new_soup)

            for user, rating, review, date in zip(users, ratings, reviews, dates):
                if review not in unique_reviews:
                    unique_reviews.add(review)
                    
                    dataset['product_title'].append(product_title)
                    dataset['user_name'].append(user)
                    dataset['rating'].append(rating)
                    dataset['review'].append(review)
                    dataset['review_date'].append(date)

        time.sleep(random.uniform(2, 5))

amazon_df = pd.DataFrame.from_dict(dataset)
amazon_df['user_name'] = amazon_df['user_name'].fillna("Amazon Customer")
amazon_df.insert(0, 'ID', range(1, len(amazon_df) + 1))
amazon_df.to_csv('amazon_dataset.csv', header=True, index=False)

print("CSV File Created Successfully")