import os
import requests
from bs4 import BeautifulSoup

base_url = "https://www.midiworld.com/search/"
query = "?q=pop"

output_folder = "pop_midi_files"
os.makedirs(output_folder, exist_ok=True)

num_pages = 1  # 0 means all available pages


def download_midi_files(page_url):
    """
    Download all MIDI files from a given search results page.

    Args:
        page_url (str): The URL of the search results page to process.

    Returns:
        bool: True if files were downloaded successfully, False if no download links were found.
    """
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        download_links = soup.find_all("a", string="download")

        if not download_links:
            return False

        for link in download_links:
            midi_url = link["href"]
            if not midi_url.startswith("https://www.midiworld.com"):
                midi_url = "https://www.midiworld.com" + midi_url

            filename = os.path.basename(midi_url)

            if not filename.endswith(".mid"):
                filename += ".mid"

            output_path = os.path.join(output_folder, filename)

            try:
                midi_response = requests.get(midi_url, timeout=10)
                midi_response.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(midi_response.content)
                print(f"Downloaded file: {output_path}")
            except Exception as e:
                print(f"Error downloading file {midi_url}: {e}")
        return True
    except Exception as e:
        print(f"Error processing page {page_url}: {e}")
        return False


def process_pages(num_pages):
    """
    Main function to iterate through pages and process them.

    Args:
        num_pages (int): The number of pages to process. Set to 0 to process all available pages.
            - If num_pages > 0: Process up to the specified number of pages.
            - If num_pages == 0: Continue processing until no more results are found.
    """
    page_num = 1
    while True:
        page_url = f"{base_url}{page_num}/{query}"
        print(f"Processing page: {page_url}")
        has_more_results = download_midi_files(page_url)

        if not has_more_results or (num_pages > 0 and page_num >= num_pages):
            if not has_more_results:
                print("No more results. Stopping.")
            else:
                print(f"Reached maximum number of pages: {num_pages}")
            break

        page_num += 1


process_pages(num_pages)

print("Download complete.")
