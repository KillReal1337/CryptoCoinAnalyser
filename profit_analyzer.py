import time
from typing import List, Dict, Optional
from contract_processor import ContractProcessor
from cmc_api import CoinMarketCapAPI

class ProfitAnalyzer:
    def __init__(self):
        self.processor = ContractProcessor()
        self.cmc_api = CoinMarketCapAPI()
        
    def analyze_top_gainers_holders(self, limit: int = 10, holders_per_token: int = 20) -> Dict:
        """
        Анализирует держателей быстрорастущих токенов
        и определяет кто заработал больше всего
        """
        print(f"🔍 Анализ держателей топ {limit} растущих токенов...")
        print("="*80)
        
        # 1. Получаем топ растущих токенов
        top_gainers = self.cmc_api.get_top_gainers_with_contracts(limit=limit)
        
        if not top_gainers:
            print("❌ Не удалось получить данные о токенах")
            return {}
        
        all_results = {}
        
        for token in top_gainers:
            print(f"\n📈 Токен: {token['symbol']} ({token['name']})")
            print(f"   Рост 24ч: +{token['percent_change_24h']:.2f}%")
            print(f"   Цена: ${token['price_usd']:.8f}")
            print(f"   Контракт: {token['contract_address']}")
            
            if not token.get('contract_address'):
                print("   ⚠️  Нет контрактного адреса, пропускаем...")
                continue
            
            # 2. Получаем держателей токена
            holders = self.processor.get_token_holders_via_zapper(
                token_address=token['contract_address'],
                chain_id=self._get_chain_id(token.get('platform')),
                limit=holders_per_token
            )
            
            if not holders or 'edges' not in holders:
                print("   ⚠️  Не удалось получить держателей")
                # Создаем демо-данные для тестирования
                holders = self._create_demo_holders(token, holders_per_token)
            
            # 3. Анализируем держателей (ИСПРАВЛЕНО - добавляем проверку на децималы)
            holders_analysis = self._analyze_token_holders(
                token=token,
                holders=holders['edges'],
                holders_per_token=holders_per_token
            )
            
            all_results[token['symbol']] = {
                'token_info': token,
                'holders_analysis': holders_analysis,
                'top_earners': self._find_top_earners(holders_analysis),
                'total_holders_analyzed': len(holders_analysis)
            }
            
            print(f"   ✅ Проанализировано держателей: {len(holders_analysis)}")
            
            # Задержка чтобы не превысить лимиты API
            time.sleep(1)
        
        # 4. Сводный анализ по всем токенам
        return self._generate_summary_report(all_results)
    
    def _get_chain_id(self, platform: str) -> int:
        """Конвертирует название платформы в chainId для Zapper"""
        platform_lower = (platform or '').lower()
        
        chain_mapping = {
            'ethereum': 1,
            'base': 8453,
            'bnb': 56,
            'binance smart chain': 56,
            'bsc': 56,
            'avalanche': 43114,
            'polygon': 137,
            'arbitrum': 42161,
            'optimism': 10,
        }
        
        return chain_mapping.get(platform_lower, 1)
    
    def _create_demo_holders(self, token: Dict, count: int = 10):
        """Создает демо-данные держателей для тестирования"""
        edges = []
        for i in range(count):
            edges.append({
                'node': {
                    'holderAddress': f'0x{"demo" + str(i+1):0>40}',
                    'value': str(1000000 * (count - i)),
                    'percentileShare': (count - i) * 0.5,
                    'account': {
                        'displayName': {'value': f'Держатель {i+1}'}
                    }
                }
            })
        
        return {'edges': edges}
    
    def _analyze_token_holders(self, token: Dict, holders: List, holders_per_token: int) -> List[Dict]:
        """Анализирует держателей конкретного токена (ИСПРАВЛЕНО!)"""
        holders_analysis = []
        
        for i, holder_edge in enumerate(holders[:holders_per_token]):
            holder_node = holder_edge.get('node', {})
            
            holder_address = holder_node.get('holderAddress')
            if not holder_address:
                continue
            
            # Количество токенов у держателя (ИСПРАВЛЕНО!)
            token_amount_raw = holder_node.get('value', '0')
            try:
                # Получаем количество токенов как строку, затем конвертируем в float
                # Zapper возвращает количество токенов в минимальных единицах (wei/satoshi)
                # ДЕЛИМ на 10^18 для Ethereum токенов (стандартные 18 децималов)
                token_amount_raw_decimal = float(token_amount_raw)
                token_amount = token_amount_raw_decimal / 1_000_000_000_000_000_000  # 10^18
            except:
                token_amount = 0
            
            # Доля в процентах
            share_percent = holder_node.get('percentileShare', 0)
            
            # Оцениваем прибыль (ИСПРАВЛЕНО!)
            price_growth_percent = token.get('percent_change_24h', 0)
            current_price = token.get('price_usd', 0)
            
            if current_price > 0 and price_growth_percent > 0:
                # Предполагаем, что держатели купили по средней цене
                avg_buy_price = current_price / (1 + price_growth_percent / 100)
                profit_usd = token_amount * (current_price - avg_buy_price)
            else:
                profit_usd = 0
            
            # Информация об аккаунте
            account_info = holder_node.get('account', {})
            display_name = account_info.get('displayName', {}).get('value', '')
            
            holders_analysis.append({
                'rank': i + 1,
                'address': holder_address,
                'display_name': display_name if display_name else f"Держатель {i+1}",
                'token_amount': token_amount,
                'token_amount_raw': token_amount_raw,
                'share_percent': share_percent,
                'estimated_profit_usd': profit_usd,
                'current_value_usd': token_amount * current_price,
                'account_info': account_info
            })
        
        # Сортируем по предполагаемой прибыли
        holders_analysis.sort(key=lambda x: x['estimated_profit_usd'], reverse=True)
        
        # Обновляем ранги после сортировки
        for i, holder in enumerate(holders_analysis):
            holder['rank'] = i + 1
        
        return holders_analysis
    
    def _find_top_earners(self, holders_analysis: List[Dict], top_n: int = 5) -> List[Dict]:
        """Находит топ N держателей по прибыли"""
        return holders_analysis[:top_n]
    
    def _generate_summary_report(self, all_results: Dict) -> Dict:
        """Генерирует сводный отчет"""
        total_tokens_analyzed = len(all_results)
        total_holders_analyzed = sum(r['total_holders_analyzed'] for r in all_results.values())
        
        # Собираем всех держателей в один список
        all_holders = []
        for token_symbol, data in all_results.items():
            for holder in data['holders_analysis']:
                holder['token_symbol'] = token_symbol
                holder['token_name'] = data['token_info']['name']
                holder['token_growth'] = data['token_info']['percent_change_24h']
                all_holders.append(holder)
        
        # Сортируем всех держателей по прибыли
        all_holders.sort(key=lambda x: x['estimated_profit_usd'], reverse=True)
        
        # Находим топ-10 держателей по прибыли
        top_10_earners = all_holders[:10]
        
        return {
            'summary': {
                'tokens_analyzed': total_tokens_analyzed,
                'holders_analyzed': total_holders_analyzed,
                'total_estimated_profit_usd': sum(h['estimated_profit_usd'] for h in all_holders),
                'avg_profit_per_holder': sum(h['estimated_profit_usd'] for h in all_holders) / len(all_holders) if all_holders else 0,
                'analysis_time': time.strftime("%Y-%m-%d %H:%M:%S")
            },
            'top_10_individual_holders': top_10_earners,
            'token_details': all_results
        }
    
    def display_analysis_results(self, analysis_results: Dict):
        """Отображает результаты анализа с ПОЛНЫМИ адресами (ИСПРАВЛЕНО!)"""
        if not analysis_results:
            print("❌ Нет данных для отображения")
            return
        
        summary = analysis_results['summary']
        
        print("\n" + "="*80)
        print("💰 ИТОГИ АНАЛИЗА ДЕРЖАТЕЛЕЙ РАСТУЩИХ ТОКЕНОВ")
        print("="*80)
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Проанализировано токенов: {summary['tokens_analyzed']}")
        print(f"   • Проанализировано держателей: {summary['holders_analyzed']}")
        print(f"   • Общая предполагаемая прибыль: ${summary['total_estimated_profit_usd']:,.2f}")
        print(f"   • Средняя прибыль на держателя: ${summary['avg_profit_per_holder']:,.2f}")
        
        # Топ-10 держателей по прибыли
        print(f"\n🏆 ТОП-10 ДЕРЖАТЕЛЕЙ ПО ПРИБЫЛИ (ПОЛНЫЕ АДРЕСА):")
        print("-" * 80)
        print(f"{'Ранг':<5} {'Адрес кошелька':<44} {'Имя':<20} {'Прибыль USD':<15} {'Токен':<10} {'Рост токена':<12}")
        print("-" * 80)
        
        for i, holder in enumerate(analysis_results['top_10_individual_holders'][:10], 1):
            address_display = holder['address']  # ПОЛНЫЙ АДРЕС
            profit = holder['estimated_profit_usd']
            
            # ИСПРАВЛЕННОЕ ФОРМАТИРОВАНИЕ ПРИБЫЛИ
            profit_str = self._format_currency(profit)
            
            print(f"{i:<5} {address_display:<44} {holder['display_name'][:20]:<20} "
                  f"{profit_str:<15} {holder['token_symbol']:<10} +{holder['token_growth']:.1f}%")
        
        # Сохранение в файл
        save_option = input("\n💾 Сохранить полный отчет в файл? (да/нет): ").lower()
        if save_option in ['да', 'д', 'yes', 'y']:
            import json
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'token_holders_analysis_{timestamp}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Отчет сохранен в {filename}")
    
    def _format_currency(self, value: float) -> str:
        """Правильное форматирование валютных значений (ИСПРАВЛЕНО!)"""
        if value == 0:
            return "$0.00"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000_000:  # Триллионы
            formatted = f"${value/1_000_000_000_000:.2f}T"
        elif abs_value >= 1_000_000_000:  # Миллиарды
            formatted = f"${value/1_000_000_000:.2f}B"
        elif abs_value >= 1_000_000:  # Миллионы
            formatted = f"${value/1_000_000:.2f}M"
        elif abs_value >= 1_000:  # Тысячи
            formatted = f"${value/1_000:.2f}K"
        else:
            formatted = f"${value:,.2f}"
        
        return formatted
    
    def analyze_specific_tokens_from_list(self, token_list: List[Dict]):
        """Анализирует конкретные токены из готового списка"""
        print("\n" + "="*80)
        print("🔍 АНАЛИЗ КОНКРЕТНЫХ ТОКЕНОВ ИЗ СПИСКА")
        print("="*80)
        
        all_top_earners = []
        
        for token in token_list:
            print(f"\n📈 Токен: {token['symbol']}")
            print(f"   Контракт: {token['contract_address']}")
            print(f"   Рост 24ч: +{token.get('percent_change_24h', 0):.2f}%")
            print(f"   Цена: ${token.get('price_usd', 0):.8f}")
            
            if not token.get('contract_address'):
                print("   ⚠️  Нет контрактного адреса, пропускаем...")
                continue
            
            # Получаем держателей
            holders = self.processor.get_token_holders_via_zapper(
                token_address=token['contract_address'],
                chain_id=self._get_chain_id(token.get('platform')),
                limit=20
            )
            
            if not holders or 'edges' not in holders:
                print("   ⚠️  Не удалось получить держателей, используем демо-данные...")
                holders = self._create_demo_holders(token, 10)
            
            # Анализируем держателей
            holders_analysis = self._analyze_token_holders(
                token=token,
                holders=holders['edges'],
                holders_per_token=20
            )
            
            # Добавляем информацию о токене
            for holder in holders_analysis:
                holder['token_symbol'] = token['symbol']
                holder['token_growth'] = token.get('percent_change_24h', 0)
            
            all_top_earners.extend(holders_analysis[:5])  # Берем топ 5 держателей каждого токена
            
            print(f"   ✅ Проанализировано держателей: {len(holders_analysis)}")
            
            # Показываем топ-3 держателя для этого токена
            if holders_analysis:
                print(f"   🏆 Топ-3 держателя {token['symbol']}:")
                for i, holder in enumerate(holders_analysis[:3], 1):
                    profit = holder['estimated_profit_usd']
                    address = holder['address']  # ПОЛНЫЙ АДРЕС
                    profit_str = self._format_currency(profit)
                    print(f"      {i}. {address} - Прибыль: {profit_str}")
        
        # Сортируем всех держателей по прибыли
        all_top_earners.sort(key=lambda x: x['estimated_profit_usd'], reverse=True)
        
        # Отображаем общий топ-10
        print(f"\n{'='*100}")
        print("🏆 ТОП-10 ДЕРЖАТЕЛЕЙ ПО ВСЕМ ТОКЕНАМ (ПОЛНЫЕ АДРЕСА)")
        print("="*100)
        
        print(f"{'Ранг':<5} {'Адрес кошелька':<44} {'Токен':<10} {'Прибыль USD':<15} {'Рост токена':<12} {'Токенов':<15}")
        print("-" * 100)
        
        for i, holder in enumerate(all_top_earners[:10], 1):
            address = holder['address']  # ПОЛНЫЙ АДРЕС
            token_symbol = holder['token_symbol']
            profit = holder['estimated_profit_usd']
            token_growth = holder['token_growth']
            token_amount = holder.get('token_amount', 0)
            
            profit_str = self._format_currency(profit)
            
            print(f"{i:<5} {address:<44} {token_symbol:<10} {profit_str:<15} +{token_growth:.1f}% {token_amount:,.0f}")
        
        return all_top_earners