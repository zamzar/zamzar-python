from zamzar_sdk import ZamzarClient
from zamzar_sdk.pagination import after

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Retrieve information about a single file
file = zamzar.files.find(123456).model
print(f"File ID: {file.id} was created at {file.created_at}")

# List files (returns at most 50 files at a time)
for file_manager in zamzar.files.list().items:
    print(f"File ID: {file_manager.model.id} was created at {file_manager.model.created_at}")

# To page through all files, use the next_page method:
current_page = zamzar.files.list()
while True:
    for file_manager in current_page.items:
        print(f"File ID: {file_manager.model.id} was created at {file_manager.model.created_at}")
    current_page = current_page.next_page()
    if not current_page.items:
        break

# For fine-grained control over pagination, use an anchor and a limit
# For example, retrieve the 20 files immediately after file ID 123456
targeted_page = zamzar.files.list(after(123456), 20)
