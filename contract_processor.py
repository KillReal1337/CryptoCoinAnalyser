import requests
import json
import time
import random
from datetime import datetime
from typing import List, Dict
from zapper_api import ZapperAPI

class ContractProcessor:
    def __init__(self, external_api_url=None, external_api_key=None):
        self.external_api_url = external_api_url
        self.external_api_key = external_api_key
        
        # Инициализируем Zapper API
        try:
            self.zapper_api = ZapperAPI()
            print("✅ Zapper API инициализирован")
        except ValueError as e:
            print(f"⚠️  {e}")
            self.zapper_api = None
        except Exception as e:
            print(f"⚠️  Ошибка инициализации: {e}")
            self.zapper_api = None
    
    def extract_contracts(self, crypto_data):
        """Извлекает контрактные адреса из данных о криптовалютах"""
        contracts = []
        
        for coin in crypto_data:
            if coin.get('contract_address'):
                contracts.append({
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'contract_address': coin['contract_address'],
                    'platform': coin.get('platform', 'unknown'),
                    'price_usd': coin.get('price_usd'),
                    'growth_24h': coin.get('percent_change_24h'),
                    'volume_24h': coin.get('volume_24h'),
                    'market_cap': coin.get('market_cap', 0)
                })
        
        return contracts
    
    def get_token_holders_via_zapper(self, token_address: str, chain_id: int = 1, limit: int = 50):
        """
        Получает держателей токена через Zapper API
        """
        if not self.zapper_api:
            print("⚠️  Zapper API не доступен")
            return None
        
        try:
            print(f"🔍 Запрос держателей для {token_address[:15]}...")
            holders_data = self.zapper_api.get_token_holders(token_address, chain_id, limit)
            
            if not holders_data:
                print("  ⚠️  Держатели не найдены")
                return None
            
            return holders_data
            
        except Exception as e:
            print(f"⚠️  Ошибка получения держателей: {e}")
            return None
    
    def find_top_wallets_for_tokens(self, tokens: List[Dict], wallets_per_token: int = 10) -> Dict:
        """
        Находит топ кошельки для каждого токена
        """
        if not self.zapper_api:
            return {}
        
        results = {}
        
        # Ограничиваем количество токенов
        test_tokens = tokens[:2]
        
        for token in test_tokens:
            contract_address = token['contract_address']
            symbol = token['symbol']
            
            if not contract_address:
                print(f"⚠️  Нет контракта для {symbol}")
                continue
            
            print(f"\n🔍 Поиск держателей {symbol}...")
            
            # Получаем держателей токена
            holders = self.get_token_holders_via_zapper(contract_address, chain_id=1, limit=wallets_per_token)
            
            if holders and 'edges' in holders:
                holders_list = []
                for edge in holders['edges']:
                    node = edge['node']
                    holders_list.append({
                        'address': node.get('holderAddress'),
                        'balance': node.get('value'),
                        'share_percent': node.get('percentileShare', 0),
                        'display_name': node.get('account', {}).get('displayName', {}).get('value', '')
                    })
                
                results[symbol] = {
                    'contract': contract_address,
                    'holders': holders_list[:wallets_per_token],
                    'total_holders': len(holders_list)
                }
                
                print(f"  ✅ Найдено {len(holders_list)} держателей")
            else:
                print(f"  ⚠️  Не удалось получить держателей для {symbol}")
                # Демо-данные для тестирования
                results[symbol] = {
                    'contract': contract_address,
                    'holders': [
                        {'address': f'0x{"holder1":0>40}', 'balance': '1000000', 'display_name': 'Крупный держатель'},
                        {'address': f'0x{"holder2":0>40}', 'balance': '500000', 'display_name': 'Средний держатель'},
                    ],
                    'total_holders': 100,
                    'note': 'Демо-данные'
                }
            
            time.sleep(0.5)  # Задержка между запросами
        
        return results
    
    def find_top_trading_wallets(self, sample_wallets: List[str] = None, days: int = 1, top_n: int = 5) -> List[Dict]:
        """
        Находит топ торговых кошельков
        """
        if not self.zapper_api:
            print("❌ Zapper API не доступен")
            return []
        
        # Если не переданы кошельки, используем известные
        if not sample_wallets:
            sample_wallets = self._get_known_active_wallets()
        
        print(f"🔍 Поиск топ {top_n} кошельков...")
        
        results = []
        
        for i, wallet in enumerate(sample_wallets[:top_n*2]):
            print(f"  {i+1}/{len(sample_wallets[:top_n*2])}: Адрес: {wallet}")  # ПОЛНЫЙ АДРЕС
            
            analysis = self.zapper_api.analyze_wallet_performance(wallet, days=days)
            
            if 'error' not in analysis:
                results.append(analysis)
            
            # Задержка чтобы не превысить лимиты API
            if i < len(sample_wallets[:top_n*2]) - 1:
                time.sleep(0.5)
        
        # Сортируем по дневной прибыли
        results.sort(key=lambda x: x.get('estimated_daily_profit_usd', 0), reverse=True)
        
        return results[:top_n]
    
    def _get_known_active_wallets(self) -> List[str]:
        """
        Возвращает список известных активных кошельков
        """
        known_wallets = [
            '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',  # Виталик (работает!)
            '0x849151d7d0bf1f34b70d5cad5149d28cc2308bf1',  # Кошелек из теста (работает!)
            '0x3d280fde2ddb59323c891cf30995e1862510342f',  # Пример из документации
            '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',  # Gitcoin
        ]
        
        return known_wallets
    
    def analyze_wallet_advanced(self, wallet_address: str, days: int = 7) -> Dict:
        """
        Расширенный анализ кошелька
        """
        if not self.zapper_api:
            return {'error': 'Zapper API не доступен', 'wallet_address': wallet_address}
        
        try:
            # Анализ за 1 день
            analysis = self.zapper_api.analyze_wallet_performance(wallet_address, days=1)
            
            if 'error' in analysis:
                return analysis
            
            # Добавляем расширенные метрики
            current_balance = analysis.get('current_balance_usd', 0)
            
            if current_balance > 0:
                consistency_score = min(analysis.get('roi_percent', 0) * 2 + 50, 100)
                risk_score = min(analysis.get('daily_volume_usd', 0) / current_balance * 100, 100)
            else:
                consistency_score = 50
                risk_score = 50
            
            return {
                'wallet_address': wallet_address,
                'current_balance_usd': current_balance,
                'daily_analysis': analysis,
                'top_tokens': analysis.get('top_tokens', []),
                'consistency_score': round(consistency_score, 1),
                'risk_score': round(risk_score, 1),
                'success_rating': self._calculate_success_rating(analysis)
            }
            
        except Exception as e:
            return {'error': str(e), 'wallet_address': wallet_address}
    
    def _calculate_success_rating(self, analysis: Dict) -> str:
        """Рассчитывает рейтинг успеха"""
        daily_profit = analysis.get('estimated_daily_profit_usd', 0)
        win_rate = analysis.get('win_rate_percent', 0)
        
        if daily_profit > 1000 and win_rate > 60:
            return "S-Tier 🏆"
        elif daily_profit > 500 and win_rate > 50:
            return "A-Tier ⭐"
        elif daily_profit > 100 and win_rate > 40:
            return "B-Tier 👍"
        elif daily_profit > 0:
            return "C-Tier 📈"
        else:
            return "D-Tier 📉"
    
    def save_wallets_to_file(self, wallets_data: List[Dict], filename: str = None):
        """Сохраняет данные о кошельках в файл"""
        if not wallets_data:
            print("❌ Нет данных для сохранения")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'top_wallets_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(wallets_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Данные сохранены в {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return None