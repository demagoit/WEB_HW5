import sys
import asyncio
import platform
import requests
from concurrent.futures import ThreadPoolExecutor
import aiohttp

URL = {
    # 'current':'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5',
    # 'archive': 'https://api.privatbank.ua/p24api/exchange_rates?json&date=01.12.2014',
    'current':'https://api.privatbank.ua/p24api/pubinfo',
    'archive': 'https://api.privatbank.ua/p24api/exchange_rates'
    
}

PARAMS = {
    'cash': 'json&exchange&coursid=5',
    'cashless': 'json&exchange&coursid=11',
    'at_date': 'json&date'
}

FIELDS = {
    'Curency_to_name': 'ccy',
    'Curency_base_name': 'base_ccy',
    'Curency_base_amount_2_buy': 'buy',
    'Curency_base_amount_2_sell': 'sale'
}


async def request(session, url:str, params:str):
    # print(url, params)
    try:
        async with session.get(url, params=params) as response:
            print(response.url)
            if response.status == 200:
                print("Status:", response.status)
                # print("Content-type:", response.headers['content-type'])
                # print('Cookies: ', response.cookies)
                # print(response.ok)
                result = await response.json()
                return result
            else:
                print(f"Error status: {response.status}")
    except aiohttp.ClientConnectorError as err:
        print('Connection error: ', str(err))

def output(data):
    if isinstance(data, str):
        print(data)
    elif isinstance(data, list):
        for i in data:
            print(f'{i[FIELDS["Curency_base_amount_2_buy"]]} {i[FIELDS["Curency_base_name"]]} to buy 1 {i[FIELDS["Curency_to_name"]]}')
            print(f'{i[FIELDS["Curency_base_amount_2_sell"]]} {i[FIELDS["Curency_base_name"]]} for sell 1 {i[FIELDS["Curency_to_name"]]}')


async def fetch(url:str, params:list):
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    async with aiohttp.ClientSession() as session:
        # r = await request(session=session, url=URL['current'], params='json&exchange&coursid=5')
        t = [request(session=session, url=url, params=parameter) for parameter in params]
        r = await asyncio.gather(*t, return_exceptions=True)
        
        return r[0]


def main(*args):
    output(args)
    if len(args) == 1:
        r = asyncio.run(fetch(url=URL['current'], params=[PARAMS['cash']]))
        output(r)
        r = asyncio.run(fetch(url=URL['current'], params=[PARAMS['cashless']]))
        output(r)

    else:
        try:
            days = int(args[1])
            if days > 10:
                output('Can fetch data for max. 10 days.')
            else:
                r = asyncio.run(fetch())
        except:
            output (f'Usage: {args[0]} <days> - to get exhcnge rates for last <days>')
            sys.exit(1)


if __name__ == "__main__":
    main(*sys.argv)