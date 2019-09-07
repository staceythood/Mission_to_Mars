from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import time


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    # Visit url
    url = "https://mars.nasa.gov/news"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Collect the latest News Title and Paragraph Text. Assign the text to variables to reference later.
    news_title = soup.find("div", class_="content_title").get_text()
    news_p = soup.find("div", class_="article_teaser_body").get_text()

    # Use splinter to navigate the site and find the image url for the current Featured Mars Image
    # and assign the url string to a variable
    img_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(img_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    featured_image_url = (
        "https://www.jpl.nasa.gov"
        + soup.find("a", class_="button fancybox")["data-fancybox-href"]
    )

    # Scrape the latest Mars weather tweet from the page. Save the tweet text for the weather report
    # as a variable called mars_weather.
    tweet_url = "https://twitter.com/MarsWxReport"
    browser.visit(tweet_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    mars_weather = soup.find_all("div", class_="js-tweet-text-container")[0].get_text()

    # Visit the Mars Facts webpage and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    # Use Pandas to convert the data to a HTML table string
    facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(facts_url)
    facts_df = tables[1]
    facts_df.columns = ["Description", "Value"]

    # Visit the USGS Astrogeology site to obtain high resolution images for each of Mar's hemispheres.
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    browser.is_element_present_by_css("img.thumb", wait_time=5)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    # Save both the image url string for the full resolution hemisphere image, and the Hemisphere title containing the hemisphere name.
    # Use a Python dictionary to store the data using the keys img_url and title.
    # Append the dictionary with the image url string and the hemisphere title to a list.
    # This list will contain one dictionary for each hemisphere.

    img_link_list = []
    title_list = []

    for link in range(0, 4):
        browser.is_element_present_by_css("a.product-item h3", wait_time=1)
        browser.find_by_css("a.product-item h3")[link].click()
        browser.is_element_present_by_text("Sample", wait_time=1)
        img_link = browser.find_link_by_text("Sample").first
        img_link_list.append(img_link["href"])
        title = browser.find_by_css("h2.title").text
        title_list.append(title)
        browser.back()

    hemi_image_urls = []
    for i in range(len(img_link_list)):
        link_dict = {}
        link_dict["title"] = title_list[i]
        link_dict["img_url"] = img_link_list[i]
        hemi_image_urls.append(link_dict)

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "facts_df": facts_df.to_html(escape=True),
        "hemi_image_urls": hemi_image_urls,
    }

    # facts_dict = facts_df.to_dict()

    # for _, row in facts_df.iterrows():
    #     mars_data[row["Description"]] = row["Value"]

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

