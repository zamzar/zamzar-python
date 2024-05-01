from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Upload a file to the Zamzar API
file_id = zamzar.upload("path/to/your/file.docx").id
print(f"File ID: {file_id}")
