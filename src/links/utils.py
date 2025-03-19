import uuid

def get_random_link_alias(short_code_lenght: int =6):
    '''
        Принимает длину алиаса и создает случайный алиас для сокращенной ссылки при помощи функции uuid4.
        Аргументы:
            short_code_lenght (int): длина алиаса, по умолчанию 6.
    '''

    alias = str(uuid.uuid4())[:short_code_lenght]

    return alias