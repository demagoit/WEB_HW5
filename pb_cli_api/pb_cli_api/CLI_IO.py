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
        
    __PROMPTS = {'command_prompt': 'Please enter your command: ',

               'search_prompt_pattern': 'Enter a pattern to search: ',
               'search_prompt_scope': 'Enter field to search (or enter to search everywhere): ',

               'user_name_prompt': 'Enter contact name: ',
               'user_del_prompt': 'Enter contact name to delete: ',

               'phone_prompt': 'Enter phone number: ',
               'phone_del_prompt': 'Enter phone to delete: ',
               'old_phone_prompt': 'Enter old phone number: ',
               'new_phone_prompt': 'Enter new phone number: ',

               'birthday_prompt': 'Enter birthday(yyyy-mm-dd): ',
               'birthday_search_prompt': 'Enter quantity of days: ',

               'email_prompt': 'Enter email: ',
               'email_del_prompt': 'Enter e-mail to delete: ',
               'old_email_prompt': 'Enter old e-mail: ',
               'new_email_prompt': 'Enter new e-mail: ',

               'address_prompt': 'Enter address: ',
               'address_del_prompt': 'Enter address to delete: ',
               'old_address_prompt': 'Enter old address: ',
               'new_address_prompt': 'Enter new address: ',

               'memo_prompt': 'Enter memo: ',
               'memo_del_prompt': 'Enter memo to delete: ',
               'old_memo_prompt': 'Enter old memo: ',
               'new_memo_prompt': 'Enter new memo: '
               }

    def __init__(self, my_book):
        self.__book = my_book
        self.__NAME_COMMANDS = {

        'help': self.__help,
        'hello': self.__hello,
        'close': self.__exit,
        'exit': self.__exit,

        'today': self.__add_addr,
        'past': self.__delete_addr,
    }

    def __hello(self):
        return ('How can I help you?', 'normal')

    def __help(self):
        help_list = [
            ['Command', 'Description'], #header
            ['help', 'command description'],
            ['hello', 'greets the user'],
            ['close | exit', 'for exit'],


            ['today', 'fetch current exchange rates'],
            ['past', 'fetch echange rates for past <days>'],
        ]
        return (help_list, 'table')

    def __exit(self):
        return ('Good bye!', 'normal')

        
    def get_input(self):
        try:
            user_input = prompt(self.__PROMPTS.get('command_prompt'), completer=WordCompleter(
                self.__NAME_COMMANDS.keys(), ignore_case=True))

            return_data = self.__NAME_COMMANDS[user_input]()

        except KeyboardInterrupt:
            # user_input_list = ('\nCommand input interrupted. Exiting...',)
            exit()
        except KeyError:
            return_data = ('Wrong command, try again', 'critical')

        return return_data

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

    def user_output(self, data):

        if isinstance(data[0], str):
            console = Console()
            console.print(data[0], style=self.__styles.get(data[1]))

        elif isinstance(data[0], list):
            self.table(header=data[0][0], rows=data[0][1:], **self.__styles.get(data[1]))
        
        else:
            console = Console()
            console.print(
                f'Got uknown data format {type(data)}', style=self.__styles.get('critical'))
