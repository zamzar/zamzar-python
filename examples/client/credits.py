from zamzar import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# Make an API call to get the remaining credits
remaining_credits = zamzar.get_production_credits_remaining()
remaining_test_credits = zamzar.get_sandbox_credits_remaining()
print(
    f"You currently have {remaining_credits} production credits remaining "
    f"and {remaining_test_credits} test credits remaining."
)

# Or, if you've made an API call already (such as to convert a file), retrieve the last known credits
last_remaining_credits = zamzar.last_production_credits_remaining
last_remaining_test_credits = zamzar.last_sandbox_credits_remaining
print(
    f"At the time of your last request, you had {last_remaining_credits} production credits remaining "
    f"and {last_remaining_test_credits} test credits remaining."
)
