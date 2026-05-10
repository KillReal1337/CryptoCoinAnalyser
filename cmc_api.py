import os
import requests
import time
import numpy as np
from dotenv import load_dotenv

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
            'limit': 100,
            'sort': 'percent_change_24h',
            'sort_dir': 'desc',
            'convert': 'USD'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
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
                        'coin_id': coin['id'],
                        'market_cap': coin['quote']['USD']['market_cap']
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
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if str(coin_id) not in data['data']:
                return {'contract_address': None, 'platform': None}
            
            info = data['data'][str(coin_id)]
            platform_data = info.get('platform', {})
            
            contract_address = None
            platform_name = None
            
            if isinstance(platform_data, dict):
                contract_address = platform_data.get('token_address')
                platform_name = platform_data.get('name', 'unknown')
                
                if not contract_address and 'contract_address' in platform_data:
                    contract_address = platform_data.get('contract_address')
            
            elif isinstance(platform_data, str):
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
    
    def test_connection(self):
        """Тестирует подключение к API"""
        try:
            # Простой тест запроса
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {'limit': 1}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    coin = data['data'][0]
                    return True, f"✅ API подключение успешно! Пример: {coin['name']} - ${coin['quote']['USD']['price']:.2f}"
                else:
                    return False, "❌ API ответил, но данные пустые"
            else:
                return False, f"❌ Ошибка API: {response.status_code}"
                
        except Exception as e:
            return False, f"❌ Ошибка подключения: {e}"
    
    def get_token_info(self, symbol: str):
        """Получает информацию о токене по символу"""
        url = f"{self.base_url}/cryptocurrency/quotes/latest"
        params = {
            'symbol': symbol.upper(),
            'convert': 'USD'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                coin_data = list(data['data'].values())[0]
                return {
                    'name': coin_data['name'],
                    'symbol': coin_data['symbol'],
                    'price': coin_data['quote']['USD']['price'],
                    'market_cap': coin_data['quote']['USD']['market_cap'],
                    'volume_24h': coin_data['quote']['USD']['volume_24h'],
                    'percent_change_24h': coin_data['quote']['USD']['percent_change_24h']
                }
            return None
        except Exception as e:
            print(f"❌ Ошибка получения информации о токене: {e}")
            return None
    
    def get_market_overview(self):
        """Получает общую статистику рынка"""
        url = f"{self.base_url}/global-metrics/quotes/latest"
        params = {'convert': 'USD'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            market_data = data['data']
            
            return {
                'total_market_cap': market_data['quote']['USD']['total_market_cap'],
                'total_volume_24h': market_data['quote']['USD']['total_volume_24h'],
                'btc_dominance': market_data['btc_dominance'],
                'eth_dominance': market_data['eth_dominance'],
                'active_cryptocurrencies': market_data['active_cryptocurrencies'],
                'last_updated': market_data['last_updated']
            }
        except Exception as e:
            print(f"❌ Ошибка получения статистики рынка: {e}")
            return None