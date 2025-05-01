from zamzar import ZamzarClient
from zamzar.pagination import after

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Retrieve information about a single import
_import = zamzar.imports.find(123456).model
print(f"Import ID: {_import.id} was created at {_import.created_at}")

# List imports (returns at most 50 imports at a time)
for i in zamzar.imports.list().items:
    print(f"Import ID: {i.model.id} was created at {i.model.created_at}")

# To page through all imports, use the nextPage method:
current_page = zamzar.imports.list()
while True:
    for i in current_page.items:
        print(f"Import ID: {i.model.id} was created at {i.model.created_at}")
    current_page = current_page.next_page()
    if len(current_page.items) == 0:
        break

# For fine-grained control over pagination, use an anchor and a limit
# For example, retrieve the 20 imports immediately after import ID 123456
targetedPage = zamzar.imports.list(after(123456), 20)
