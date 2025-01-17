from datetime import datetime
from decimal import Decimal
from ..services import get_etherscan_transactions, get_crypto_prices

def calculate_wallet_evolution(address, devise="ETH"):
    # Récupérer les transactions pour l'adresse
    transactions = get_etherscan_transactions(address)
    if not transactions:  # Vérifiez si la liste est vide
        print(f"Aucune transaction trouvée pour l'adresse {address}")
        return []

    # Récupérer le prix de la crypto (en EUR)
    crypto_prices = get_crypto_prices(devise)
    if "EUR" not in crypto_prices:
        print(f"Impossible de récupérer le prix pour {devise} en EUR")
        return []

    eth_price_in_eur = Decimal(crypto_prices["EUR"])  # Prix actuel en EUR

    # Calculer l'évolution du portefeuille
    evolution = {}
    balance_in_eth = 0
    balance_in_eur = 0

    for tx in transactions:
        if not isinstance(tx, dict):  # Vérifiez que chaque élément est un dictionnaire
            print(f"Transaction mal formée : {tx}")
            continue

        # Vérifier que tous les champs nécessaires sont présents
        if not all(key in tx for key in ["timeStamp", "value", "to", "from", "gasUsed", "gasPrice"]):
            print(f"Transaction incomplète : {tx}")
            continue

        # Convertir le timestamp Unix en une date
        date = datetime.fromtimestamp(int(tx["timeStamp"])).date()

        # Convertir la valeur de la transaction en ETH
        value_in_eth = Decimal(tx["value"]) / Decimal(10**18)  # Wei à ETH

        # Mise à jour du solde (en ETH)
        if tx["to"].lower() == address.lower():
            balance_in_eth += value_in_eth
        elif tx["from"].lower() == address.lower():
            gas_fee_in_eth = (Decimal(tx["gasUsed"]) * Decimal(tx["gasPrice"])) / Decimal(10**18)
            balance_in_eth -= (value_in_eth + gas_fee_in_eth)

        # Calculer la valeur en EUR
        balance_in_eur = balance_in_eth * eth_price_in_eur
        evolution[date] = float(balance_in_eur)  # Stocker le solde en EUR pour chaque date

    # Transformer l'évolution en liste triée
    return [{"date": str(date), "price": price} for date, price in sorted(evolution.items())]



