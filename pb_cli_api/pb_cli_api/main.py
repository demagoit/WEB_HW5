import sys
import asyncio
import platform
import aiohttp
import datetime
from copy import deepcopy
from CLI_IO import *


class PB_API():
    def __init__(self):
        self.__URL = {
            'current': 'https://api.privatbank.ua/p24api/pubinfo',
            'archive': 'https://api.privatbank.ua/p24api/exchange_rates'
            
        }

        self.__PARAMS = {
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


    async def fetch(self, urls:list):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        async with aiohttp.ClientSession() as session:
            url_coroutines = [self.request(session=session, url=url) for url in urls]
            reply = await asyncio.gather(*url_coroutines, return_exceptions=True)
            results = []
            errors = []
            for result, status in reply:
                if status == 'OK':
                    results.append(result)
                else:
                    errors.append([result, status])
            result = result if result else None
            errors = errors if errors else None
            return results, errors

    async def request(self, session, url:str) -> tuple:
        try:
            async with session.get(url) as response:
                if response.ok:
                    result = await response.json()
                    return (result, 'OK')
                else:
                    msg = f"Error status: {response.status} at URL: {response.url}"
                    return(msg, 'warning')
        except aiohttp.ClientConnectorError as err:
            msg = 'Connection error: ' + str(err)
            return(msg, 'critical')

    def query_builder(self, url:str, params:dict = {}) -> str:
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

    def run(self, days_2_fetch: int = 0):
        if not isinstance(days_2_fetch, int):
            result = None
            errors = [('Error: expect int number of days to fetch. 0 - for current exchange rate.','warning')]
        elif days_2_fetch == 0:
            # Cash rate
            urls = [self.query_builder(url=self.__URL['current'], params = self.__PARAMS['cash'])]
            # # Cashless rate
            # urls = [self.query_builder(url=URL['current'], params=PARAMS['cashless'])]
            result, errors = asyncio.run(self.fetch(urls))
            result = (result[0], 'current') if result else None
        elif days_2_fetch > 10:
            result = None
            errors = [('Can fetch data for max. 10 days.', 'warning')]
        else:
            dates = [(datetime.date.today()-datetime.timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days_2_fetch)]
            
            urls = []
            for date in dates:
                params = deepcopy(self.__PARAMS['at_date'])
                params['date'] = date
                urls.append(self.query_builder(url=self.__URL['archive'], params = params))
            result, errors = asyncio.run(self.fetch(urls))
            result = (result, 'arch') if result else None
        return result, errors


def main(*args):
    pb = PB_API()
    CLI_In = CLI_Input(api=pb)
    CLI_out = CLI_Output()
    

    if len(args) == 1:
        data, errors = CLI_In.help()
        CLI_out.user_output(data)
        
        while True:
            data, errors = CLI_In.get_input()

            if data:
                CLI_out.user_output(data)
                if data[0] == "Good bye!":
                    exit()
            if errors:
                for error in errors:
                    CLI_out.user_output(error)

    else:
        try:
            days = int(args[1])
        except:
            CLI_out.user_output([f'Usage: {args[0]} <days> - to get exhcnge rates for last <days>', 'warning'])
            sys.exit(1)

        resp, errors = pb.run(days_2_fetch=days)
        if resp:
            CLI_out.user_output(['Archive', 'normal'])
            CLI_out.user_output(resp)
        if errors:
            for error in errors:
                CLI_out.user_output(error)



if __name__ == "__main__":
    main(*sys.argv)