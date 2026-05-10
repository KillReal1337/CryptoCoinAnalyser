import os
import requests
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class CoinMarketCapAPI:
    def __init__(self):
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        if not self.api_key or self.api_key == 'your_api_key_here':
            raise ValueError("❌ API ключ не найден или не настроен. Проверьте файл .env")
        
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
    
    def get_top_gainers_with_contracts(self, limit=20):
        """
        Получает топ растущих криптовалют за 24 часа с контрактными адресами
        """
        print(f"📊 Загрузка топ {limit} растущих криптовалют...")
        
        # 1. Получаем список всех криптовалют с сортировкой по росту
        url = f"{self.base_url}/cryptocurrency/listings/latest"
        params = {
            'start': 1,
            'limit': 100,  # Загружаем больше для выборки
            'sort': 'percent_change_24h',
            'sort_dir': 'desc',
            'convert': 'USD'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['data']:
                print("❌ Нет данных от API")
                return []
            
            print(f"✅ Загружено {len(data['data'])} криптовалют")
            
            # 2. Берем топ N по росту
            top_coins = data['data'][:limit]
            
            # 3. Получаем детальную информацию с контрактами
            print("🔍 Получение контрактных адресов...")
            result = []
            
            for i, coin in enumerate(top_coins, 1):
                try:
                    # Получаем детальную информацию для каждой монеты
                    coin_info = self._get_coin_info_with_contract(coin['id'])
                    
                    result.append({
                        'rank': i,
                        'name': coin['name'],
                        'symbol': coin['symbol'],
                        'price_usd': coin['quote']['USD']['price'],
                        'volume_24h': coin['quote']['USD']['volume_24h'],
                        'percent_change_24h': coin['quote']['USD']['percent_change_24h'],
                        'contract_address': coin_info.get('contract_address'),
                        'platform': coin_info.get('platform'),
                        'coin_id': coin['id']  # Добавляем ID для отладки
                    })
                    
                    # Небольшая задержка чтобы не превысить лимиты API
                    if i < len(top_coins):
                        time.sleep(0.2)
                        
                except Exception as e:
                    print(f"⚠️ Ошибка для {coin['name']}: {e}")
                    continue
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе: {e}")
            return []
    
    def _get_coin_info_with_contract(self, coin_id):
        """
        Получает информацию о конкретной монете включая контракт
        """
        url = f"{self.base_url}/cryptocurrency/info"
        params = {'id': str(coin_id)}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if str(coin_id) not in data['data']:
                return {'contract_address': None, 'platform': None}
            
            info = data['data'][str(coin_id)]
            platform_data = info.get('platform', {})
            
            # ДЕБАГ: выводим структуру данных
            # print(f"\n🔍 DEBUG для {info.get('name')} (ID: {coin_id}):")
            # print(f"Platform данные: {platform_data}")
            
            # Проверяем разные форматы данных
            contract_address = None
            platform_name = None
            
            if isinstance(platform_data, dict):
                # Формат: {'id': 1027, 'name': 'Ethereum', 'symbol': 'ETH', 'slug': 'ethereum', 'token_address': '0x...'}
                contract_address = platform_data.get('token_address')
                platform_name = platform_data.get('name', 'unknown')
                
                # Иногда адрес может быть в другом поле
                if not contract_address and 'contract_address' in platform_data:
                    contract_address = platform_data.get('contract_address')
            
            elif isinstance(platform_data, str):
                # Просто строка с адресом
                if platform_data.startswith('0x') or len(platform_data) > 20:
                    contract_address = platform_data
                    platform_name = 'unknown'
                else:
                    platform_name = platform_data
            
            return {
                'contract_address': contract_address,
                'platform': platform_name
            }
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ошибка при получении информации для ID {coin_id}: {e}")
            return {'contract_address': None, 'platform': None}
    
    def get_contract_for_coin(self, coin_id_or_symbol):
        """
        Получает контрактный адрес для конкретной монеты по ID или символу
        """
        print(f"🔍 Поиск контракта для: {coin_id_or_symbol}")
        
        try:
            # Пробуем как ID
            if str(coin_id_or_symbol).isdigit():
                coin_id = int(coin_id_or_symbol)
                coin_info = self._get_coin_info_with_contract(coin_id)
                
                if coin_info['contract_address']:
                    print(f"✅ Найден контракт для ID {coin_id}:")
                    print(f"   Адрес: {coin_info['contract_address']}")
                    print(f"   Платформа: {coin_info['platform']}")
                    return coin_info
                else:
                    print(f"❌ Контракт не найден для ID {coin_id}")
                    
            # Пробуем как символ
            else:
                # Сначала получаем ID по символу
                url = f"{self.base_url}/cryptocurrency/map"
                params = {'symbol': coin_id_or_symbol.upper()}
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data['data']:
                    coin_id = data['data'][0]['id']
                    coin_name = data['data'][0]['name']
                    
                    print(f"✅ Найдена монета: {coin_name} (ID: {coin_id})")
                    
                    # Теперь получаем контракт
                    coin_info = self._get_coin_info_with_contract(coin_id)
                    
                    if coin_info['contract_address']:
                        print(f"✅ Найден контракт:")
                        print(f"   Адрес: {coin_info['contract_address']}")
                        print(f"   Платформа: {coin_info['platform']}")
                    else:
                        print(f"❌ Контракт не найден")
                    
                    return coin_info
                else:
                    print(f"❌ Монета с символом {coin_id_or_symbol} не найдена")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        return None

def display_top_gainers(data):
    """Отображает топ растущих криптовалют"""
    if not data:
        print("❌ Нет данных для отображения")
        return
    
    print("\n" + "="*130)
    print("🚀 ТОП РАСТУЩИХ КРИПТОВАЛЮТ ЗА 24 ЧАСА")
    print("="*130)
    print(f"{'№':<3} {'Название':<20} {'Символ':<8} {'ID':<8} {'Цена USD':<12} {'Объем 24ч':<18} {'Рост 24ч':<10} {'Контракт':<50}")
    print("-" * 130)
    
    for coin in data:
        # Форматируем цену
        price = coin['price_usd']
        if price >= 1:
            price_str = f"${price:,.2f}"
        elif price >= 0.01:
            price_str = f"${price:,.4f}"
        else:
            price_str = f"${price:.8f}"
        
        # Форматируем объем
        volume = coin['volume_24h']
        if volume >= 1_000_000_000:
            volume_str = f"${volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            volume_str = f"${volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            volume_str = f"${volume/1_000:.2f}K"
        else:
            volume_str = f"${volume:,.0f}"
        
        # Форматируем процент роста
        change = coin['percent_change_24h']
        change_str = f"{change:+.2f}%"
        
        # Форматируем контрактный адрес
        contract = coin['contract_address']
        if contract:
            # Обрезаем для удобства чтения
            if len(contract) > 46:
                contract_display = f"{contract[:20]}...{contract[-20:]}"
            else:
                contract_display = contract
        else:
            contract_display = "Нет контракта"
        
        print(f"{coin['rank']:<3} {coin['name'][:20]:<20} {coin['symbol']:<8} "
              f"{coin['coin_id']:<8} {price_str:<12} {volume_str:<18} "
              f"{change_str:<10} {contract_display:<50}")
        
        # Дополнительная информация о платформе
        if contract and coin['platform'] and coin['platform'] != 'unknown':
            print(f"    ↳ Платформа: {coin['platform']}")

def save_to_file(data):
    """Сохраняет данные в файл по выбору пользователя"""
    if not data:
        print("❌ Нет данных для сохранения")
        return
    
    print("\n💾 Сохранить результаты в файл?")
    print("1. 💾 Сохранить в CSV")
    print("2. 📄 Сохранить в TXT (с полными адресами)")
    print("3. 📋 Сохранить только контракты в TXT")
    print("4. ❌ Не сохранять")
    
    choice = input("\nВыберите опцию: ").strip()
    
    if choice == '4':
        print("Данные не сохранены")
        return
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        if choice == '1':
            import csv
            filename = f'top_gainers_{timestamp}.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"✅ Данные сохранены в {filename}")
            
        elif choice == '2':
            filename = f'top_gainers_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("🚀 ТОП РАСТУЩИХ КРИПТОВАЛЮТ ЗА 24 ЧАСА\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for coin in data:
                    f.write(f"{coin['rank']}. {coin['name']} ({coin['symbol']}) [ID: {coin['coin_id']}]\n")
                    f.write(f"   Цена: ${coin['price_usd']}\n")
                    f.write(f"   Объем 24ч: ${coin['volume_24h']:,.0f}\n")
                    f.write(f"   Рост 24ч: {coin['percent_change_24h']:+.2f}%\n")
                    
                    if coin['contract_address']:
                        f.write(f"   Контракт: {coin['contract_address']}\n")
                        if coin['platform'] and coin['platform'] != 'unknown':
                            f.write(f"   Платформа: {coin['platform']}\n")
                    else:
                        f.write("   Контракт: Нет\n")
                    
                    f.write("-" * 60 + "\n")
            
            print(f"✅ Данные сохранены в {filename}")
        
        elif choice == '3':
            filename = f'contracts_only_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("🔗 СПИСОК КОНТРАКТНЫХ АДРЕСОВ\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                contract_count = 0
                for coin in data:
                    if coin['contract_address']:
                        contract_count += 1
                        f.write(f"{contract_count}. {coin['name']} ({coin['symbol']})\n")
                        f.write(f"   Контракт: {coin['contract_address']}\n")
                        if coin['platform'] and coin['platform'] != 'unknown':
                            f.write(f"   Платформа: {coin['platform']}\n")
                        f.write("-" * 40 + "\n")
                
                f.write(f"\n📊 Всего контрактов: {contract_count} из {len(data)} монет\n")
            
            print(f"✅ Контракты сохранены в {filename} ({contract_count} адресов)")
        
        else:
            print("❌ Неверный выбор")
    
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")

def main():
    print("🚀 Запуск Crypto Gainers Fetcher...")
    print("="*60)
    
    try:
        api = CoinMarketCapAPI()
    except ValueError as e:
        print(e)
        print("\n📝 Получите API ключ на: https://coinmarketcap.com/api/")
        print("📁 Добавьте ключ в файл .env в формате: COINMARKETCAP_API_KEY=ваш_ключ")
        input("\nНажмите Enter для выхода...")
        return
    
    while True:
        print("\n" + "="*60)
        print("🎯 CRYPTO GAINERS - ТОП РАСТУЩИХ КРИПТОВАЛЮТ")
        print("="*60)
        print("1. 🚀 Получить топ 20 растущих криптовалют")
        print("2. 🔢 Настроить количество (нестандартное)")
        print("3. 🔍 Найти контракт по ID/символу")
        print("4. 📊 Проверить API подключение")
        print("0. ❌ Выход")
        
        choice = input("\nВыберите опцию: ").strip()
        
        if choice == '1':
            data = api.get_top_gainers_with_contracts(limit=20)
            display_top_gainers(data)
            
            if data:
                save_to_file(data)
        
        elif choice == '2':
            try:
                limit = int(input("Сколько криптовалют показать? (макс 100): ") or "20")
                limit = min(limit, 100)
                data = api.get_top_gainers_with_contracts(limit=limit)
                display_top_gainers(data)
                
                if data:
                    save_to_file(data)
            except ValueError:
                print("❌ Ошибка: введите число")
                continue
            
        elif choice == '3':
            search_input = input("Введите ID монеты или символ (например, 5426 или CONCHO): ").strip()
            if search_input:
                api.get_contract_for_coin(search_input)
            else:
                print("❌ Введите ID или символ")
            
        elif choice == '4':
            print("\n🔍 Тестирование API подключения...")
            try:
                # Простой тест API
                url = f"{api.base_url}/cryptocurrency/listings/latest"
                params = {'limit': 1}
                response = requests.get(url, headers=api.headers, params=params)
                
                if response.status_code == 200:
                    print("✅ API подключение успешно!")
                    data = response.json()
                    if data['data']:
                        coin = data['data'][0]
                        print(f"📊 Пример: {coin['name']} - ${coin['quote']['USD']['price']:.2f}")
                        
                        # Проверяем контракт для Bitcoin (должен быть None)
                        print("\n🔍 Тест контракта для Bitcoin (ID: 1):")
                        btc_info = api._get_coin_info_with_contract(1)
                        print(f"   Контракт Bitcoin: {btc_info['contract_address'] or 'Нет (ожидаемо)'}")
                else:
                    print(f"❌ Ошибка API: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            
        elif choice == '0':
            print("👋 Выход...")
            break
            
        else:
            print("❌ Неверный выбор")
            continue
        
        input("\n↵ Нажмите Enter для продолжения...")

# ⭐ ЯВНЫЙ ЗАПУСК ПРОГРАММЫ ⭐
if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")