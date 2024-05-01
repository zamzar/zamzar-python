from zamzar import ZamzarClient, Environment

# By default, a client will use the production environment
zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

# You can also specify the environment explicitly to switch to the sandbox environment
sandboxed_zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE", environment=Environment.SANDBOX)
