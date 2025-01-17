from eth_account import Account

new_account = Account.create()

# Afficher les informations
print(f"Adresse Ethereum : {new_account.address}")
print(f"Clé privée : {new_account.key.hex()}")
