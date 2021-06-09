import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from insta.items import InstaItem

class Insta1Spider(scrapy.Spider):
    # атрибуты класса
    name = 'insta_1'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_graphql_link = 'https://www.instagram.com/graphql/query/?'
    insta_login = 'oda148052021'
    insta_pass = '****'
    insta_queryParams = '{}'
    insta_optIntoOneTap = 'false'
    insta_stopDeletionNonce = ''
    parse_user = 'ai_machine_learning'   #Пользователь, у которого собираем посты. Можно указать список
    post_hash = '02e14f6a7812a876f7d133c9555b1151'  #hash для получения данных по постах с главной страницы
    post_hash_in_post = '3eb224d64759a46f7083d3322a2458bd'  #hash для получения данных о пользователях оставивших комментарии


    def parse(self, response):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.insta_login_link, method='POST', callback=self.login,
                                 formdata={'username': self.insta_login, 'enc_password': self.insta_pass,
                                           'queryParams': self.insta_queryParams, 'optIntoOneTap': self.insta_optIntoOneTap,
                                           'stopDeletionNonce': self.insta_stopDeletionNonce},
                                 headers={'X-CSRFToken': csrf})


    def login(self, response:HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            yield response.follow(f'/{self.parse_user}', callback=self.user_parse, cb_kwargs={'username':self.parse_user})


    def user_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,'first': 12}

        url_posts = f'{self.insta_graphql_link}query_hash={self.post_hash}&{urlencode(variables)}'

        yield response.follow(url_posts, callback=self.user_posts_parse, cb_kwargs={'username': username,
                                                                                    'user_id': user_id,
                                                                                    'variables': deepcopy(variables)})




    def user_posts_parse(self, response:HtmlResponse, username, user_id, variables):
        i = 0
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page') and i != 2:
            variables['after'] = page_info.get('end_cursor')

            url_posts = f'{self.insta_graphql_link}query_hash={self.post_hash}&{urlencode(variables)}'
            i += 1

            yield response.follow(url_posts, callback=self.user_posts_parse, cb_kwargs={'username': username,
                                                                                        'user_id': user_id,
                                                                                        'variables': deepcopy(variables)})



        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            short_code = post['node']['shortcode']
            variables_in_post = {'shortcode': short_code, 'child_comment_count': 3,'fetch_comment_count': 40, 'parent_comment_count': 24, 'has_threaded_comments': True}
            url_in_posts = f'{self.insta_graphql_link}query_hash={self.post_hash_in_post}&{urlencode(variables_in_post)}'

            yield response.follow(url_in_posts, callback=self.parse_in_post, cb_kwargs={'username': username,
                                                                                        'user_id': user_id,
                                                                                        'shortcode': short_code,
                                                                                        'variables': deepcopy(variables_in_post)})



    def parse_in_post(self, response:HtmlResponse, username, user_id, shortcode, variables):

        j_data_in_post = response.json()
        posts_in = j_data_in_post.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('edges')

        for post in posts_in:
            link = post['node']['owner']['username']
            item = InstaItem(
                parent_user_id=user_id,
                parent_user_name=username,
                profile_photo=post['node']['owner']['profile_pic_url'],
                user_name=post['node']['owner']['username'],
                user_id=post['node']['owner']['id'],
                short_code=shortcode,
                user_link=f'https://www.instagram.com/{link}/',
                all=post['node']
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')