from abc import abstractclassmethod, ABC

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table


class Input(ABC):
    @abstractclassmethod
    def get_input(self):
        pass


class Output(ABC):
    @abstractclassmethod
    def user_output(self, data):
        pass


class CLI_Input(Input):
        
    __PROMPTS = {
                'command_prompt': 'Please enter your command: ',
                'arch_depth': 'How many days: ',
                }

    def __init__(self, api):
        self.__api = api
        self.__NAME_COMMANDS = {

        'help': self.help,
        'hello': self.__hello,
        'close': self.__exit,
        'exit': self.__exit,

        'today': self.__today,
        'past': self.__past,
    }

    def __today(self):
        resp, errors = self.__api.run(days_2_fetch=0)
        return resp, errors

    def __past(self):
        days = input(self.__PROMPTS['arch_depth'])
        try:
            days= int(days)
        except:
            pass
        resp, errors = self.__api.run(days_2_fetch=days)
        return resp, errors

    def __hello(self):
        resp = ['How can I help you?', 'normal']
        errors = None
        return resp, errors

    def help(self):
        help_list = [
            ['Command', 'Description'], #header
            ['help', 'command description'],
            ['hello', 'greets the user'],
            ['close | exit', 'for exit'],


            ['today', 'fetch current exchange rates'],
            ['past', 'fetch echange rates for past <days>'],
        ]
        resp = [help_list, 'table']
        errors = None
        return resp, errors

    def __exit(self):
        resp =['Good bye!', 'normal']
        errors = None
        return resp, errors
  
    def get_input(self):
        try:
            user_input = prompt(self.__PROMPTS.get('command_prompt'), completer=WordCompleter(
                self.__NAME_COMMANDS.keys(), ignore_case=True))

            return_data, errors = self.__NAME_COMMANDS[user_input]()

        except KeyboardInterrupt:
            exit()
        except KeyError:
            return_data = None
            errors = [['Wrong command, try again', 'critical']]

        return return_data, errors

class CLI_Output(Output):
    def __init__(self):
        self.__styles = {
            'normal': 'green',
            'warning': 'yellow',
            'critical': 'red',
            'table': {
                'header_style': 'bold blue', 
                'row_style': 'bright_green'
            }
        }
        self.__FIELDS_TD = {
            'Curency_to_name': 'ccy',
            'Curency_base_name': 'base_ccy',
            'Curency_base_amount_2_sell': 'buy',
            'Curency_base_amount_2_buy': 'sale'
        }

        self.__FIELDS_ARCH = {
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

    def table(self, title=None, title_style=None, header=[], header_style=None, rows=[], row_style=None):

        table = Table()
        if title:
            table.title = title
            table.title_style = title_style
            table.title_justify = 'left'

        longest_row = max([len(row) for row in rows])
        if len(header) < longest_row:
            for i in range(longest_row - len(header)):
                header.append(f'Column_{i}')

        for column in header:
            table.add_column(column, header_style=header_style, width=20)

        for row in rows:
            row = [self.__value_getter(item) for item in row]
            table.add_row(*row, style=row_style)

        table.show_lines = True

        Console().print(table)

    def __value_getter(self, value):

        if isinstance(value, list):
            value = ' '.join([str(i) for i in value])
        elif value:
            value = str(value)
        else:
            value = ''
        return value

    def form_data_structure(self, data) -> list:
        data, srs = data
        if srs in ['normal', 'warning', 'critical']:
            result = [data, srs]
        elif srs == 'current':
            header = ['Today', 'Buy', 'Sell']
            tbl = [header]
            for item in data:
                cur = item[self.__FIELDS_TD["Curency_to_name"]]
                sel_val = [item[self.__FIELDS_TD["Curency_base_amount_2_buy"]], item[self.__FIELDS_TD["Curency_base_name"]]]
                buy_val = [item[self.__FIELDS_TD["Curency_base_amount_2_sell"]], item[self.__FIELDS_TD["Curency_base_name"]]]
                tbl.append([cur, buy_val, sel_val])
            result = [tbl, 'table']
        elif srs == 'arch':
            header = ['Date', 'USD Buy', 'USD Sell']
            tbl = [header]
            for record in data:
                data_dict = self.arch_parser(record)
                dt = data_dict['Date']
                for tick, price in data_dict['PB'].items():
                    if tick == 'USD':
                        usd_buy = [price['buy'], data_dict['Base']]
                        usd_sell = [price['sell'], data_dict['Base']]
                        tbl.append([dt, usd_buy, usd_sell])
            result = [tbl, 'table']
        elif srs == 'table':
            result = [data, srs]
        return result

    def arch_parser(self, data: dict) -> dict:
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
        
        out_dict['Date'] = data[self.__FIELDS_ARCH['Date']]
        out_dict['Base'] = data[self.__FIELDS_ARCH['Curency_base_name_head']]
        
        for item in data[self.__FIELDS_ARCH['Rates']]:
            tick = item[self.__FIELDS_ARCH['Curency_to_name']]
            try:
                out_dict['NBU'][tick] = {
                    'sell': item[self.__FIELDS_ARCH['Curency_base_amount_2_buy_NBU']],
                    'buy': item[self.__FIELDS_ARCH['Curency_base_amount_2_sell_NBU']]
                }
            except:
                pass
            try:
                out_dict['PB'][tick] = {
                    'sell': item[self.__FIELDS_ARCH['Curency_base_amount_2_buy_PB']],
                    'buy': item[self.__FIELDS_ARCH['Curency_base_amount_2_sell_PB']]
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

    def user_output(self, data):

        data = self.form_data_structure(data=data)

        if isinstance(data[0], str):
            console = Console()
            console.print(data[0], style=self.__styles.get(data[1]))

        elif isinstance(data[0], list):
            self.table(header=data[0][0], rows=data[0][1:], **self.__styles.get(data[1]))
        
        else:
            console = Console()
            console.print(
                f'Got uknown data format {type(data)}', style=self.__styles.get('critical'))
