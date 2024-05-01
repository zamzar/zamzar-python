from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Start an import, wait for it to complete, or throw an exception if it fails
imported_file_id = zamzar \
    .imports \
    .start("https://www.zamzar.com/images/zamzar-logo.png") \
    .await_completion(throw_on_failure=True) \
    .imported_file \
    .id

print(f"Imported file ID: {imported_file_id}")

# Check why an import failed
print(zamzar.imports.find(123456).failure)
