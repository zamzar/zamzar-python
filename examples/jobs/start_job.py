from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Convert a local file, wait for it to complete (or throw an exception if it fails), and download the result
zamzar \
    .convert("path/to/your/file.docx", "pdf") \
    .store("path/to/your/file.pdf")

# Convert a local file that produces multiple output files (e.g. a multi-page PDF to PNGs)
zamzar \
    .convert("path/to/your/multipage.pdf", "png") \
    .store("path/to/output_directory")

# Convert a local file that produces multiple output files and download them as a ZIP file
zamzar \
    .convert("path/to/your/multipage.pdf", "png") \
    .store("path/to/output.zip", extract_multiple_file_output=False)

# Convert a remote file, wait for it to complete (or throw an exception if it fails), and download the result
zamzar \
    .convert("https://www.zamzar.com/images/zamzar-logo.png", "jpg") \
    .store("path/to/your/file.jpg")

# Convert a file in an S3 bucket, wait for it to complete (throwing if it fails), and upload the result to S3
# (requires Connected Services to be configured in the developer dashboard at https://developers.zamzar.com/)
zamzar.convert(
    "s3://CREDENTIAL_NAME@your-bucket/your-file.docx",
    "pdf",
    export_url="s3://CREDENTIAL_NAME@your-bucket/your-file.pdf",
)

# Override the source format (if it's not correctly detected from the URL / filename)
zamzar \
    .convert("https://www.example.com/example-logo", "jpg", source_format="png") \
    .store("path/to/your/file.jpg")

# Specify conversion options
zamzar \
    .convert("path/to/your/file.txt", "mp3", options={"voice": "en.female"}) \
    .store("path/to/your/file.mp3")

# Check why a job failed
print(zamzar.jobs.find(123456).failure)
