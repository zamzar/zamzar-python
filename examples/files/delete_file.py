from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Delete the file with the specified ID from the Zamzar API
zamzar.files.delete(123456)

# Or if you need to download and then delete:
zamzar.download(123456, "path/to/your/file.docx").delete()
