import re
import uuid

def get_random_link_alias(short_code_lenght: int = 6):
    '''
        Принимает длину алиаса и создает случайный алиас для сокращенной ссылки при помощи функции uuid4.
        Аргументы:
            short_code_lenght (int): длина алиаса, по умолчанию 6.
    '''

    alias = str(uuid.uuid4())[:short_code_lenght]

    return alias


# Регулярка для валидации исходных ссылок 
valid_url_regexp = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)