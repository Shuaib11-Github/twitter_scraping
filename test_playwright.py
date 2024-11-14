import pandas as pd  # Import pandas for data manipulation and saving data to CSV
import time  # Import time for delays
from playwright.sync_api import sync_playwright  # Import Playwright for browser automation

# Define the path to the CSV file containing profile URLs
input_file = r'C:\Users\arabb\Twitter Scraping\twitter_links.csv'

# Read the CSV file, assuming it has no header, and load it into a DataFrame
profile_links_df = pd.read_csv(input_file, header=None)

# Convert the first column of the DataFrame into a list of profile URLs
profile_links = profile_links_df[0].tolist()

# Initialize an empty dictionary to store extracted data
data = {
    "Bio": [],  # List to store bios
    "Location": [],  # List to store locations
    "Following Count": [],  # List to store following counts
    "Followers Count": [],  # List to store follower counts
    "Website": []  # List to store websites
}

# Define a function to extract profile information from each URL
def extract_profile_info(page, url):
    # Initialize a dictionary with default values for the profile data
    profile_data = {
        "Bio": "Not available",
        "Location": "Not available",
        "Following Count": "Not available",
        "Followers Count": "Not available",
        "Website": "Not available"
    }

    try:
        # Navigate to the profile URL with a 5-second timeout
        page.goto(url, timeout=5000)
        # Wait an additional 5 seconds for elements to load fully
        page.wait_for_timeout(5000)

        # Extract bio information if available
        bio_element = page.query_selector("div[data-testid='UserDescription']")
        profile_data["Bio"] = bio_element.inner_text() if bio_element else "Not available"

        # Extract location if available
        location_element = page.query_selector("span[data-testid='UserLocation']")
        profile_data["Location"] = location_element.inner_text() if location_element else "Not available"

        # Extract following count if available
        following_element = page.query_selector("a[href*='/following'] span")
        profile_data["Following Count"] = following_element.inner_text() if following_element else "Not available"

        # Extract followers count if available
        followers_element = page.query_selector("a[href*='/verified_followers'] span")
        profile_data["Followers Count"] = followers_element.inner_text() if followers_element else "Not available"

        # Extract website if available (displayed text within <span> inside <a>)
        website_text_element = page.query_selector("a[data-testid='UserUrl'] span")
        profile_data["Website"] = website_text_element.inner_text() if website_text_element else "Not available"

    except Exception as e:
        # Print error if any issues occur while extracting data
        print(f"Error extracting data for {url}: {e}")

    # Return the extracted profile data
    return profile_data

# Start a Playwright session to automate browser actions
with sync_playwright() as p:
    # Launch a headless Chromium browser (without GUI)
    browser = p.chromium.launch(headless=True)
    # Open a new page (tab) in the browser
    page = browser.new_page()

    # Navigate to the Twitter login page
    page.goto("https://x.com/login")
    # Wait 5 seconds for the page to load
    time.sleep(5)
    
    # Enter the username in the username input field
    page.fill('//input[@name="text"]', "UserName")
    # Click the 'Next' button to proceed to the password entry step
    page.click('//span[contains(text(),"Next")]')
    # Wait 3 seconds for the next step to load
    time.sleep(3)
    
    # Enter the password in the password input field
    page.fill('//input[@name="password"]', "Password")
    # Click the 'Log in' button to log into the account
    page.click('//span[contains(text(),"Log in")]')
    # Wait 5 seconds to ensure the login is completed
    time.sleep(5)

    # Loop through each profile URL in the list
    for profile_url in profile_links:
        # Call the function to extract profile information for the current URL
        profile_data = extract_profile_info(page, profile_url)
        
        # Append each extracted piece of data to the respective list in the data dictionary
        data["Bio"].append(profile_data["Bio"])
        data["Following Count"].append(profile_data["Following Count"])
        data["Followers Count"].append(profile_data["Followers Count"])
        data["Location"].append(profile_data["Location"])
        data["Website"].append(profile_data["Website"])

    # Close the browser after processing all profiles
    browser.close()

# Define the output file path for the extracted data
output_file = 'Twitter_Profile_Data_Playwright.csv'

# Create a DataFrame from the data dictionary
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file without the index column
df.to_csv(output_file, index=False)

# Print a message indicating that the data has been saved
print(f"Data saved to {output_file}")
