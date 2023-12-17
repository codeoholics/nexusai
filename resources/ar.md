def extract_file_content_from_s3_url(url):
    try:
        # Download the file
        response = requests.get(url)
        response.raise_for_status()

        # Check if the response is empty
        if not response.content:
            log.error("The response content is empty.")
            return None

        # Log the response status and content length
        log.info(f"Response Status: {response.status_code}, Content Length: {len(response.content)}")

        # Extract filename from URL
        filename = url.split('/')[-1]
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, filename)

        # Write the content to a temporary file with the same name
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response.content)

        log.info(f"Downloaded the file to {temp_file_path}")

        # Extract text from the file
        summary = extract_text_from_file(temp_file_path)
        log.info(f"Extracted the following text from the file: {summary}")

        # Clean up: Delete the temporary file after use
        os.remove(temp_file_path)

        return summary

    except requests.RequestException as e:
        log.error(f"Failed to download the file: {e}")
        return None
    except Exception as e:
        log.error(f"Error processing the file: {e}")
        return None