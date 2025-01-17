import requests
from django.conf import settings

def get_etherscan_transactions(address):
    url = f"https://api.etherscan.io/api"

    # Transactions normales
    normal_params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': settings.ETHERSCAN_API_KEY
    }

    # Transactions internes
    internal_params = {
        'module': 'account',
        'action': 'txlistinternal',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': settings.ETHERSCAN_API_KEY
    }

    try:
        # Récupérer les transactions normales
        normal_response = requests.get(url, params=normal_params, timeout=10)
        normal_data = normal_response.json()
        if "status" not in normal_data or normal_data["status"] != "1":
            print("Erreur dans les transactions normales :", normal_data)
            normal_transactions = []
        else:
            normal_transactions = normal_data["result"]

        # Récupérer les transactions internes
        internal_response = requests.get(url, params=internal_params, timeout=10)
        internal_data = internal_response.json()
        if "status" not in internal_data or internal_data["status"] != "1":
            print("Erreur dans les transactions internes :", internal_data)
            internal_transactions = []
        else:
            internal_transactions = internal_data["result"]

        # Combiner les deux types de transactions
        all_transactions = normal_transactions + internal_transactions
        return all_transactions

    except requests.RequestException as e:
        print(f"Erreur réseau lors de l'appel à l'API Etherscan : {e}")
        return []
    except ValueError as e:
        print(f"Erreur lors de l'analyse JSON : {e}")
        return []



def get_crypto_prices(devise):
    url = f"https://min-api.cryptocompare.com/data/price"
    params = {
        'fsym': devise,
        'tsyms': 'USD,EUR',
        'api_key': settings.CRYPTOCOMPARE_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()
