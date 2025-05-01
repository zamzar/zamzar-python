from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Download the file with the specified ID from the Zamzar API
zamzar.download(123456, "path/to/your/file.docx")
