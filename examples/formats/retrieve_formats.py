from zamzar import ZamzarClient
from zamzar.pagination import after

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Retrieve information about a single format
print("jpgs can be converted to:")
jpg = zamzar.formats.find("jpg")
if jpg.targets:
    for target in jpg.targets:
        print(f" - {target.name} ({target.credit_cost} credits)")

# List formats (returns at most 50 formats at a time)
print("All formats:")
for f in zamzar.formats.list().items:
    print(f.name)

# To page through all formats, use the next_page method:
current_page = zamzar.formats.list()
while True:
    for f in current_page.items:
        print(f.name)
    current_page = current_page.next_page()
    if not current_page.items:
        break

# For fine-grained control over pagination, use an anchor and a limit
# For example, retrieve the 20 formats immediately after the "jpg" format
targeted_page = zamzar.formats.list(after("jpg"), 20)
