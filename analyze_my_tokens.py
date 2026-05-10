#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ конкретных токенов из списка
"""

from profit_analyzer import ProfitAnalyzer

def analyze_my_tokens():
    """Анализирует конкретные токены из вашего списка"""
    
    # Ваши токены из списка
    tokens_to_analyze = [
        {
            'symbol': 'BOYSCLUB',
            'name': "Matt Furie's Boys Cl",
            'contract_address': '0x6968676661ac9851c38907bdfcc22d5dd77b564d',
            'platform': 'Ethereum',
            'percent_change_24h': 10780.21,
            'price_usd': 0.00130622
        },
        {
            'symbol': 'GO',
            'name': 'GoChain',
            'contract_address': '0x845f4fbf04d03958be38ff91e43dfb5d40dd8241',
            'platform': 'Base',
            'percent_change_24h': 3889.16,
            'price_usd': 0.00087993
        },
        {
            'symbol': 'DEUSD',
            'name': 'Elixir deUSD',
            'contract_address': '0x15700b564ca08d9439c58ca5053166e8317aa138',
            'platform': 'Ethereum',
            'percent_change_24h': 2986.43,
            'price_usd': 0.00611990
        },
        {
            'symbol': 'CATX',
            'name': 'CATX',
            'contract_address': '0x8d0C064AB0973fE124Fa9EFAAd492060bAaCb62c',
            'platform': 'BNB',
            'percent_change_24h': 1539.76,
            'price_usd': 0.00000245
        },
        {
            'symbol': 'DOGEX',
            'name': 'DOGEX',
            'contract_address': '0x6f00d7AF383f79000A1fEBd9A251bf52b0B4f1f8',
            'platform': 'BNB',
            'percent_change_24h': 1398.82,
            'price_usd': 0.00000020
        },
        {
            'symbol': 'CSAS',
            'name': 'csas (Ordinals)',
            'contract_address': '0x11bac0c3c81838022327198aa46124cdb8ce6ab9',
            'platform': 'Ethereum',
            'percent_change_24h': 1199.89,
            'price_usd': 0.00013002
        },
        {
            'symbol': 'PINK',
            'name': 'Dot Finance',
            'contract_address': '0x9133049Fb1FdDC110c92BF5b7Df635abB70C89DC',
            'platform': 'BNB',
            'percent_change_24h': 861.43,
            'price_usd': 0.00009131
        },
        {
            'symbol': 'PLYR',
            'name': 'PLYR L1',
            'contract_address': '0xC09a033927f9fD558C92CF7AeAbE34B71ce4B31E',
            'platform': 'Avalanche',
            'percent_change_24h': 727.30,
            'price_usd': 0.00234382
        },
        {
            'symbol': 'RATS',
            'name': 'rats (Ethereum)',
            'contract_address': '0x8e18141efd10C3Df7a33B4D53f608E10Dc4D4fE3',
            'platform': 'Ethereum',
            'percent_change_24h': 546.16,
            'price_usd': 7725224255.60
        },
        {
            'symbol': 'COP',
            'name': 'Copiosa Coin',
            'contract_address': '0x8789337a176e6e7223ff115f1cd85c993d42c25c',
            'platform': 'BNB',
            'percent_change_24h': 542.98,
            'price_usd': 0.00025962
        }
    ]
    
    print("🔍 АНАЛИЗ ВАШИХ КОНКРЕТНЫХ ТОКЕНОВ")
    print("="*80)
    print(f"📊 Всего токенов для анализа: {len(tokens_to_analyze)}")
    print("="*80)
    
    # Инициализируем анализатор
    analyzer = ProfitAnalyzer()
    
    # Запускаем анализ
    results = analyzer.analyze_specific_tokens_from_list(tokens_to_analyze)
    
    # Сохраняем результаты
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'my_tokens_analysis_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'tokens_analyzed': tokens_to_analyze,
            'top_holders': results[:20],
            'analysis_time': timestamp,
            'total_holders_analyzed': len(results)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Полный отчет сохранен в {filename}")
    print("✅ Анализ завершен!")

if __name__ == "__main__":
    analyze_my_tokens()