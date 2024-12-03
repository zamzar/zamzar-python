from zamzar_sdk import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

zamzar \
    .convert("/tmp/example.docx", "pdf") \
    .store("/tmp/") \
    .delete_all_files()
