import pandas as pd
from IPython.display import Markdown
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import requests
from bs4 import BeautifulSoup
import csv
import google.generativeai as genai
import json

genai.configure(api_key = "AIzaSyAU1RvIrI_U8IvZgKiymmwGNKsuxiVH9ms")

# List of car models
car_models = [
  "MG Astor",  # Mid-size SUV (not mentioned before)
  "Hyundai Aura",  # Compact Sedan (not mentioned before)
  "Honda WR-V",  # Compact SUV (not mentioned before)
  "Toyota Glanza",  # Hatchback (rebranded Maruti Suzuki Baleno, but not mentioned before)
  "Toyota Urban Cruiser",  # Mid-size SUV (rebranded Maruti Suzuki Brezza, but not mentioned before)
  "MG ZS EV",  # Electric SUV (included for completeness, might have been mentioned before)
  "Nissan Kicks",  # Compact SUV (might have been mentioned before)  
  "Force Gurkha",  # Off-road SUV (not mentioned before)
  "MG One",  # Electric SUV (not mentioned before)
  "Morris Garage ZS EV MG ZS EV",  # Electric SUV (variation, not mentioned before)
  "Citroen C5 Aircross",  # Mid-size SUV (not mentioned before)
  "MG ZS EV MG ZS EV Excite",  # Electric SUV (variation, not mentioned before)
  "Jeep Compass Trailhawk",  # Off-road variant of Compass (not mentioned before)
  "MG ZS EV MG ZS EV Exclusive",  # Electric SUV (variation, not mentioned before)
]

df = pd.DataFrame(columns=["company_name", "company_message", "car_model", "car_description", "car_price", "type_mode_of_campaign", "date_of_campaign", "duration_of_campaign", "description_of_campaign", "concept_of_campaign", "slogan_of_campaign", "target_audience_of_campaign", "success_failure_of_campaign", "reason_for_success_failure_of_campaign"])

model = genai.GenerativeModel('gemini-pro')

def search_car_ad_campaigns(car_models):
    base_url = "https://www.google.com/search?q="
    links = []
    links_per_model = 3  # Number of links to find for each model
    
    for model in car_models:
        print(f"Searching for campaigns for {model}...")
        model_links = 0  # Reset the link counter for each model
        try:
            # Construct the search query with specific keywords related to advertisement campaigns
            search_query = f"{model} campaign advertisement marketing promotion"
            search_url = base_url + search_query.replace(" ", "+")
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links in the search results
            for link in soup.find_all('a'):
                # Check if the link is a search result link
                if 'href' in link.attrs and '/url?q=' in link['href']:
                    # Extract the actual URL from the search result link
                    actual_url = link['href'].split('/url?q=')[1].split('&')[0]
                    # Check if the URL is not an image or a Google search result or a YouTube link
                    if not actual_url.endswith('.jpg') and not actual_url.endswith('.png') and not actual_url.endswith('.gif') and not 'google.com' in actual_url and not 'youtube.com' in actual_url:
                        print(f"Found link: {actual_url}")
                        # Add the URL to the list of links
                        links.append(actual_url)
                        model_links += 1  # Increment the link counter for this model
                        # Stop adding links for this model once we've found the desired number
                        if model_links >= links_per_model:
                            break
        except Exception as e:
            print(f"Error occurred while searching for {model}: {e}")
    
    return links

# Call the function with the list of car models
links = search_car_ad_campaigns(car_models)

# Open the file to store the text content
# Open the file to store the text content
# Open the file to store the text content
with open('content.txt', 'w', encoding='utf-8') as file:
    # Go through each link
    for i, link in enumerate(links):
        try:

            print(f"Getting content from link {i+1}----------------------------------------------------------------------------------------------")
            # Get the HTML content of the link
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract the text from the HTML content, remove whitespaces and write it to the file
            text= soup.get_text().split()
            response = model.generate_content(f"""Given the following data on car campaigns, I want you to extract info on the following columns: "company_name", "company_message", "car_model", "car_description", "car_price", "type_mode_of_campaign", "date_of_campaign", "duration_of_campaign", "description_of_campaign", "concept_of_campaign", "slogan_of_campaign", "target_audience_of_campaign", "success_failure_of_campaign", "reason_for_success_failure_of_campaign". Be smart and extract the car related data from all the nonsense you get, if you can't find a relevant thing replace it with 'NA'.
The response should only have results of a single CAR CAMPAIGN, no other data should be included, no non-car brands must be included.
The response should always be a JSON markdown code. Always return all columns in the json object and if you cannot find relevant data return NA. All the keys should be in snake lower case. Be sure to give me only 1 JSON object, no nested objects with array. Per column, only include 1 value.
Here is the raw data: {text}
            """,
            safety_settings={HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE})

        # Parse the response text into a dictionary
            #print(response.text)
            response_text = response.text

            # Split the response text into lines
            lines = response_text.splitlines()

            # Remove the first and last lines
            cleaned_lines = lines[1:-1]

            # Join the cleaned lines back into a single string
            cleaned_response_text = '\n'.join(cleaned_lines)
            print(cleaned_response_text)

            # Parse the cleaned response text into a dictionary
            data = json.loads(cleaned_response_text)

            data_df = pd.DataFrame([data])

            # Append the data to the DataFrame
            df = pd.concat([df, data_df], ignore_index=True)
            


            #file.write(' '.join(text))
            # Write a separator line with the link number
            #file.write(f'\n\n--- Link {i+1} End ---\n\n')
        except Exception as e:
            print(f"Error occurred while getting content from {link}: {e}")
        print("done----------------------------------------------------------------------------------------------------------------------------")
    df.to_csv('data.csv', index=False)
    print(df)
