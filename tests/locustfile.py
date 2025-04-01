from faker import Faker
from random import choice
from uuid import uuid4
from locust import HttpUser, task, constant_throughput



class TestUser(HttpUser):
    wait_time = constant_throughput(5)
    
    source_url_list = ['https://www.google.com', 'https://ru.wikipedia.org', 
                       'https://www.reddit.com', 'https://dzen.ru', 'https://ya.ru',
                       'https://ru.pinterest.com', 'https://vk.com', 'https://mail.ru',
                       'https://pikabu.ru']
    short_codes_list = ['6b7a62',]

    def on_start(self):
        # регистрируемся и логинимся
        fake = Faker()
        username = f'{fake.user_name()}@mail.ru'
        password = str(uuid4())[:8]
        data = {'grant_type': 'password', 'username': username, 'password': password}
        self.client.post('/auth/signup', data=data)
        self.client.post('/auth/login', data=data)

    def on_stop(self):
        # разлогиниваемся
        self.client.post('/auth/logout')

    @task(1)
    def get_index_test(self):
        self.client.get('/')

    @task(5)
    def post_links_shorten(self):
        source_url = choice(self.source_url_list)
        response = self.client.post('/links/shorten', json={"source_url": source_url}, name='post_link')
        short_code = response.json().get('short_link')
        short_code = short_code[short_code.rfind('/') + 1:]
        self.short_codes_list.append(short_code)

    @task(2)
    def get_links_search(self):
        original_url = choice(self.source_url_list)
        self.client.get(f'/links/search?original_url={original_url}', name='get_links_search')

    @task(2)
    def get_links_stats(self):
        short_code = choice(self.short_codes_list)
        self.client.get(f'/links/{short_code}/stats', name='get_short_code_stats')

    @task(2)
    def get_all_my_links(self):
        self.client.get('/links/all_my_links')

    @task(2)
    def delete_short_code(self):
        short_code = choice(self.short_codes_list)
        self.short_codes_list.remove(short_code)
        self.client.delete(f'/links/{short_code}')

    @task(2)
    def put_short_code(self):
        short_code = choice(self.short_codes_list)
        response = self.client.put(f'/links/{short_code}')
        new_short_code = response.json().get('short_link')
        new_short_code = short_code[short_code.rfind('/') + 1:]
        self.short_codes_list.append(short_code)
        self.short_codes_list.remove(new_short_code)

    @task(20)
    def get_links_short_code(self):
        short_code = choice(self.short_codes_list)
        self.client.get(f'/links/{short_code}', name='get_short_code')

    @task(2)
    def get_current_user(self):
        self.client.get('/auth/current-user')

