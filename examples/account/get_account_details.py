from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# The account object is read-only; any changes are not persisted to the Zamzar API
account = zamzar.account.get()

# Print the direct properties of the account object
print(account.credits_remaining)
print(account.test_credits_remaining)

# Print the plan object
print(account.plan)
