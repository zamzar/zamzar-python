from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Convert a file that is already present on Zamzar's servers to PDF, wait for completion, and download PDF
zamzar.convert(123456, "pdf").store("path/to/your/file.pdf")
