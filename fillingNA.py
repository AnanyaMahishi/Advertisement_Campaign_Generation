import pandas as pd
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import requests
from bs4 import BeautifulSoup

genai.configure(
    api_key="AIzaSyBohtXiaZB0SXU-AXDgGdpdjVnwystOofY"
)  # Replace "YOUR_API_KEY" with your actual API key

df = pd.DataFrame(
    columns=[
        "company_name",
        "company_message",
        "car_model",
        "car_description",
        "car_price",
        "type_mode_of_campaign",
        "date_of_campaign",
        "duration_of_campaign",
        "description_of_campaign",
        "concept_of_campaign",
        "slogan_of_campaign",
        "target_audience_of_campaign",
        "success_failure_of_campaign",
        "reason_for_success_failure_of_campaign",
    ]
)

model = genai.GenerativeModel("gemini-pro")


def search_online_for_details(row, column_name):
    # Construct a search query using the available data in the row and the column name
    search_query = f"{row['company_name']} {row['car_model']} {column_name}"

    # Define the URL for Google search
    google_search_url = f"https://www.google.com/search?q={search_query}"

    # Send a GET request to Google Search
    response = requests.get(google_search_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the search results page
        soup = BeautifulSoup(response.text, "html.parser")

        search_result_text = soup.get_text()

        # Construct a prompt using the search result text
        prompt = f"Give a short conscise phrase or answer  for {column_name} for {row['company_name']} {row['car_model']}? from the paragraph and only if nothing relevant is found give NA {search_result_text}"

        # Generate concise and relevant information using the Gemini API
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
        generated_info = response.text

        return generated_info
    else:
        # If the request was unsuccessful, return an empty string
        print(f"Error: Failed to retrieve search results for '{search_query}'")
        return ""


def fill_empty_cells(row):
    # Iterate over each cell in the row
    for column, value in row.items():
        # Check if the cell is empty and content is not already generated
        if pd.isnull(value):
            if column in [
                "car_price",
                "date_of_campaign",
                "duration_of_campaign",
            ]:  # Columns to search online
                # Search online for specific columns
                row[column] = search_online_for_details(row, column)
            else:
                # Search online for the specific column
                online_search_result = search_online_for_details(row, column)

                if (
                    online_search_result and online_search_result != "NA"
                ):  # If online search found something
                    row[column] = online_search_result
                elif (
                    online_search_result == "NA" or online_search_result == ""
                ):  # If online search didn't find anything, generate using Gemini API
                    # Construct a prompt using the available data in the row and the column name
                    prompt = f"{column} {row['company_name']} {row['car_model']}"
                    # Generate content using Gemini API with additional context of the column name
                    response = model.generate_content(
                        prompt,
                        safety_settings={
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        },
                    )
                    generated_text = response.text

                    # Check if generated content is empty
                    if (
                        generated_text.strip()
                    ):  # Strip whitespaces and check if not empty
                        # Fill the empty cell with the generated content
                        row[column] = generated_text

    return row


# Read data from CSV file
#df = pd.read_csv("jha2.csv")

try:
  # Assuming you've saved the CSV as UTF-8 without BOM
  df = pd.read_csv('combined8.csv', encoding='utf-8')
  print(df)
except UnicodeDecodeError:
  # Try a different encoding if UTF-8 fails
  print("Couldn't decode using UTF-8. Trying latin-1...")
  try:
    df = pd.read_csv('combined8.csv', encoding='latin-1')
    print(df)
  except UnicodeDecodeError:
    print("Couldn't decode the data using UTF-8 or latin-1 encodings")

# Iterate over each row
for i, row in df.iterrows():
    try:
        print(
            f"Processing row {i + 1}----------------------------------------------------------------------------------------------"
        )
        # Fill empty cells in the row using Gemini API or online search
        filled_row = fill_empty_cells(row)
        # Append the filled row to the DataFrame
        df.loc[i] = filled_row
        print(
            "done----------------------------------------------------------------------------------------------------------------------------"
        )
    except Exception as e:
        print(f"Error occurred while processing row {i + 1}: {e}")

# Save the DataFrame to a CSV file
df.to_csv("part1.csv", index=False)
print(df)
