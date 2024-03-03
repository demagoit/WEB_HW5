import sys
import asyncio
import platform
import aiohttp
import datetime
from copy import deepcopy
from CLI_IO import *

URL = {
    'current':'https://api.privatbank.ua/p24api/pubinfo',
    'archive': 'https://api.privatbank.ua/p24api/exchange_rates'
    
}

PARAMS = {
    'cash': {'json': None,
             'exchange': None,
             'coursid': '5'
             },
    'cashless': {'json': None,
                 'exchange': None,
                 'coursid': '11'
                 },
    'at_date': {'json': None,
                'date': None}
}

FIELDS_TD = {
    'Curency_to_name': 'ccy',
    'Curency_base_name': 'base_ccy',
    'Curency_base_amount_2_sell': 'buy',
    'Curency_base_amount_2_buy': 'sale'
}

FIELDS_ARCH = {
    'Date': 'date',
    'Curency_to_name': 'currency',
    'Curency_base_name_head': 'baseCurrencyLit',
    'Rates': 'exchangeRate',
    'Curency_base_name_rec': 'baseCurrency',
    'Curency_base_amount_2_sell_NBU': 'purchaseRateNB',
    'Curency_base_amount_2_buy_NBU': 'saleRateNB',
    'Curency_base_amount_2_sell_PB': 'purchaseRate',
    'Curency_base_amount_2_buy_PB': 'saleRate'
}


async def request(session, url:str):
    # print(url)
    try:
        async with session.get(url) as response:
            # print(response.url)
            if response.ok:
                # print("Status:", response.status)
                # print("Content-type:", response.headers['content-type'])
                # print('Cookies: ', response.cookies)
                # print(response.ok)
                result = await response.json()
                return result
            else:
                print(f"Error status: {response.status}")
    except aiohttp.ClientConnectorError as err:
        print('Connection error: ', str(err))

def output(data, srs: str = 'msg') -> None:
    cli_out = CLI_Output()
    if srs == 'msg':
        cli_out.user_output([data, 'normal'])
    elif srs == 'current':
        header = ['Today', 'Buy', 'Sell']
        tbl = [header]
        for item in data:
            cur = item[FIELDS_TD["Curency_to_name"]]
            sel_val = [item[FIELDS_TD["Curency_base_amount_2_buy"]], item[FIELDS_TD["Curency_base_name"]]]
            buy_val = [item[FIELDS_TD["Curency_base_amount_2_sell"]], item[FIELDS_TD["Curency_base_name"]]]
            tbl.append([cur, buy_val, sel_val])
        cli_out.user_output([tbl, 'table'])
    elif srs == 'arch':
        print(len(data))
        header = ['Date', 'USD Buy', 'USD Sell']
        tbl = [header]
        for record in data:
            data_dict = arch_parser(record)
            # print(data_dict)
            dt = data_dict['Date']
            for tick, price in data_dict['PB'].items():
                if tick == 'USD':
                    usd_buy = [price['buy'], data_dict['Base']]
                    usd_sell = [price['sell'], data_dict['Base']]
                    # print([dt, usd_buy, usd_sell])
                    tbl.append([dt, usd_buy, usd_sell])
        # print(tbl)
        cli_out.user_output([tbl, 'table'])

def arch_parser(data: dict) -> dict:
    out_dict = {
        'Date': None,
        'Base': None,
        'NBU': {
            'tick': {
                'sell': None,
                'buy': None
            }
        },
        'PB': {
            'tick': {
                'sell': None,
                'buy': None
            }
        },
    }
    
    out_dict['Date'] = data[FIELDS_ARCH['Date']]
    out_dict['Base'] = data[FIELDS_ARCH['Curency_base_name_head']]
    
    for item in data[FIELDS_ARCH['Rates']]:
        tick = item[FIELDS_ARCH['Curency_to_name']]
        try:
            out_dict['NBU'][tick] = {
                'sell': item[FIELDS_ARCH['Curency_base_amount_2_buy_NBU']],
                'buy': item[FIELDS_ARCH['Curency_base_amount_2_sell_NBU']]
            }
        except:
            pass
        try:
            out_dict['PB'][tick] = {
                'sell': item[FIELDS_ARCH['Curency_base_amount_2_buy_PB']],
                'buy': item[FIELDS_ARCH['Curency_base_amount_2_sell_PB']]
            }
        except:
            pass

    # cleansing
    try:
        out_dict['NBU'].pop('tick')
        out_dict['PB'].pop('tick')
    except:
        pass
    return out_dict

async def fetch(urls:list):
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    async with aiohttp.ClientSession() as session:
        t = [request(session=session, url=url) for url in urls]
        r = await asyncio.gather(*t, return_exceptions=True)
        return r

def query_builder(url:str, params:dict = {}) -> str:
    if params:
        par_str = []
        for key, value in params.items():
            if value:
                par_str.append('='.join([key, value]))
            else:
                par_str.append(key)
        par_str = '&'.join(par_str)

        req = '?'.join([url, par_str])
    else:
        req = url
    return req


def main(*args):
    # output(args, 'msg')

    if len(args) == 1:
        urls = [query_builder(url=URL['current'], params = PARAMS['cash'])]
        r = asyncio.run(fetch(urls))
        output('Cash', 'msg')
        output(r[0], 'current')

        urls = [query_builder(url=URL['current'], params=PARAMS['cashless'])]
        r = asyncio.run(fetch(urls))
        output('Cashless', 'msg')
        output(r[0], 'current')

    else:
        try:
            days = int(args[1])
        except:
            output (f'Usage: {args[0]} <days> - to get exhcnge rates for last <days>', 'msg')
            sys.exit(1)

        if days > 10:
            output('Can fetch data for max. 10 days.', 'msg')
        else:
            dates = [(datetime.date.today()-datetime.timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days)]
            
            urls = []
            for date in dates:
                params = deepcopy(PARAMS['at_date'])
                params['date'] = date
                urls.append(query_builder(url=URL['archive'], params = params))
            r = asyncio.run(fetch(urls))
            # print(r)
            output(r, 'arch')



if __name__ == "__main__":
    main(*sys.argv)