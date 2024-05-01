from zamzar import ZamzarClient
from zamzar.pagination import after

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Retrieve information about a single job
job = zamzar.jobs.find(123456).model
print(f"Job ID: {job.id} was created at {job.created_at}")

# List jobs (returns at most 50 jobs at a time)
for job in zamzar.jobs.list().items:
    print(f"Job ID: {job.id} was created at {job.created_at}")

# To page through all jobs, use the next_page method:
current_page = zamzar.jobs.list()
while True:
    for job in current_page.items:
        print(f"Job ID: {job.id} was created at {job.created_at}")
    current_page = current_page.next_page()
    if len(current_page.items) == 0:
        break

# For fine-grained control over pagination, use an anchor and a limit
# For example, retrieve the 20 jobs immediately after job ID 123456
targeted_page = zamzar.jobs.list(after(123456), 20)
