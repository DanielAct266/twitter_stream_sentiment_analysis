"""
    Script for scrapping posts from Facebook
"""

import os

from facebook_scraper import get_posts
import matplotlib.pyplot as plt
import pandas as pd

#pd.options.display.max_columns = 30


if __name__ == "__main__":

    print("\nStarting Facebook Scrapping")

    posts = []
    # Obtenemos la información de las publicaciones
    for post in get_posts('VolkswagenMX', pages=5):
        print(post)
        posts.append(post)

    # Pasamos a formato base de datos
    fb_posts = pd.DataFrame(posts)

    columns = ["time", "text", "likes", "comments", "shares"]

    fb_posts = fb_posts[columns]

    print(f"\nNumber of posts extracted: {fb_posts.shape[0]}")

    print("\nShowing first registers:")
    print(fb_posts.head())
    
    fb_posts.to_csv('data/fb_emp.csv', index=False)

    print("\nPosts Extracted and Saved Successfully!!\n\n")