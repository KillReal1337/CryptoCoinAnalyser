import os
from dotenv import load_dotenv
import requests

def quick_menu():
    load_dotenv()
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    
    while True:
        print("\n🎯 CRYPTO DATA FETCHER - CoinMarketCap API")
        print("=" * 50)
        print("1. 📊 Быстрая проверка API")
        print("2. 🚀 Топ 10 криптовалют")
        print("3. 📈 Топ 5 растущих")
        print("0. ❌ Выход")
        
        choice = input("\nВыберите опцию: ").strip()
        
        if choice == '1':
            test_api(api_key)
        elif choice == '2':
            get_top_cryptos(api_key)
        elif choice == '3':
            get_top_gainers(api_key)
        elif choice == '0':
            print("👋 Выход...")
            break
        else:
            print("❌ Неверный выбор")
        
        input("\n↵ Нажмите Enter для продолжения...")

def test_api(api_key):
    print("\n🔍 Тестирование API...")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {'X-CMC_PRO_API_KEY': api_key}
    params = {'limit': 1}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            print("✅ API подключение успешно!")
            data = response.json()
            coin = data['data'][0]
            print(f"📊 Пример: {coin['name']} - ${coin['quote']['USD']['price']:.2f}")
        else:
            print(f"❌ Ошибка API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def get_top_cryptos(api_key):
    print("\n🏆 Топ 10 криптовалют:")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {'X-CMC_PRO_API_KEY': api_key}
    params = {'limit': 10, 'sort': 'market_cap'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for i, coin in enumerate(data['data'], 1):
                price = coin['quote']['USD']['price']
                change = coin['quote']['USD']['percent_change_24h']
                print(f"{i:2d}. {coin['name']:15} ${price:8.2f} ({change:+.2f}%)")
        else:
            print(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def get_top_gainers(api_key):
    print("\n🚀 Топ 5 растущих:")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {'X-CMC_PRO_API_KEY': api_key}
    params = {'limit': 50, 'sort': 'percent_change_24h', 'sort_dir': 'desc'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for i, coin in enumerate(data['data'][:5], 1):
                price = coin['quote']['USD']['price']
                change = coin['quote']['USD']['percent_change_24h']
                print(f"{i:2d}. {coin['name']:15} ${price:8.4f} ({change:+.2f}%)")
        else:
            print(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# ⭐ ЯВНЫЙ СТАРТ ПРОГРАММЫ ⭐
if __name__ == "__main__":
    print("🚀 Запуск Crypto Data Fetcher...")
    quick_menu()
