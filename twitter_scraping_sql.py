import pandas as pd
import time
from playwright.sync_api import sync_playwright
import mysql.connector

# Database connection parameters
db_host = 'localhost'
db_user = 'mysql username'  # Replace with your MySQL username
db_password = 'mysql password'  # Replace with your MySQL password
db_name = 'twitter_db'

# Connect to the MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Define the path to the CSV file containing profile URLs
input_file = r'C:\Users\arabb\Twitter Scraping\twitter_links.csv'

# Read the CSV file, assuming it has no header, and load it into a DataFrame
profile_links_df = pd.read_csv(input_file, header=None)

# Convert the first column of the DataFrame into a list of profile URLs
profile_links = profile_links_df[0].tolist()

# Initialize an empty dictionary to store extracted data
data = {
    "Bio": [],
    "Location": [],
    "Following Count": [],
    "Followers Count": [],
    "Website": []
}

# Define a function to extract profile information from each URL
def extract_profile_info(page, url):
    profile_data = {
        "Bio": "Not available",
        "Location": "Not available",
        "Following Count": "Not available",
        "Followers Count": "Not available",
        "Website": "Not available"
    }

    try:
        page.goto(url, timeout=5000)
        page.wait_for_timeout(5000)

        bio_element = page.query_selector("div[data-testid='UserDescription']")
        profile_data["Bio"] = bio_element.inner_text() if bio_element else "Not available"

        location_element = page.query_selector("span[data-testid='UserLocation']")
        profile_data["Location"] = location_element.inner_text() if location_element else "Not available"

        following_element = page.query_selector("a[href*='/following'] span")
        profile_data["Following Count"] = following_element.inner_text() if following_element else "Not available"

        followers_element = page.query_selector("a[href*='/verified_followers'] span")
        profile_data["Followers Count"] = followers_element.inner_text() if followers_element else "Not available"

        website_text_element = page.query_selector("a[data-testid='UserUrl'] span")
        profile_data["Website"] = website_text_element.inner_text() if website_text_element else "Not available"

    except Exception as e:
        print(f"Error extracting data for {url}: {e}")

    return profile_data

# Start a Playwright session to automate browser actions
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://x.com/login")
    time.sleep(5)
    
    page.fill('//input[@name="text"]', "UserName")
    page.click('//span[contains(text(),"Next")]')
    time.sleep(3)
    
    page.fill('//input[@name="password"]', "Password")
    page.click('//span[contains(text(),"Log in")]')
    time.sleep(5)

    for profile_url in profile_links:
        profile_data = extract_profile_info(page, profile_url)
        data["Bio"].append(profile_data["Bio"])
        data["Location"].append(profile_data["Location"])
        data["Following Count"].append(profile_data["Following Count"])
        data["Followers Count"].append(profile_data["Followers Count"])
        data["Website"].append(profile_data["Website"])

    browser.close()

# Create a DataFrame from the data dictionary
df = pd.DataFrame(data)

# Save data to MySQL database
try:
    connection = connect_to_database()
    cursor = connection.cursor()

    # Insert data row by row
    insert_query = '''
    INSERT INTO twitter_profiles (Bio, Location, Following_Count, Followers_Count, Website)
    VALUES (%s, %s, %s, %s, %s)
    '''
    for index, row in df.iterrows():
        cursor.execute(insert_query, (
            row['Bio'],
            row['Location'],
            row['Following Count'],
            row['Followers Count'],
            row['Website']
        ))

    connection.commit()
    print("Data saved to MySQL database successfully.")

except mysql.connector.Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
