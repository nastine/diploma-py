import requests
import json
import time
from pprint import pprint
from urllib.parse import urlencode
from pymongo import MongoClient


access_token = '0639aef390b41e4f1c8eb0aca689bc93e7289edb19ab158d99fa4e2c5c241780269cf666d76a566bbb454'

def api_request(URL, params):
    try:
        repeat = True
        while repeat:
            response = requests.get(URL, params=params).json()
            if 'error' in response and 'error_code' in response['error'] and response['error']['error_code'] == 6:
                time.sleep(1)
            else:
                repeat = False
        return response
    except requests.exceptions.ReadTimeout:
        n = 1
        while n < 3:
            print('\n Reconnecting to server. \n')
            try:
                return requests.get(URL, params=params).json()
            except requests.exceptions.ReadTimeout:
                print('\n Reconnecting to server. \n')
            n+=1     
        else:
            print('Failed, please check your Internet connection.')

def get_token():
    app_id = 7412922
    oauth_url = 'https://oauth.vk.com/authorize'
    oauth_params = {
        'client_id': app_id,
        'display': 'page',
        'scope': 'friends, groups, stats, offline',
        'response_type': 'token',
        'v': '5.52'
    }
    print('?'.join((oauth_url, urlencode(oauth_params))))


def welcome():
    with open('welcome.txt') as welcome:
        print(welcome.read())


def get_people(access_token, sex, age_from, age_to, city_id, country_id):
    URL = 'https://api.vk.com/method/users.search'
    params = {
        'v': '5.89',
        'access_token': access_token,
        'sex': sex,
        'age_from': age_from,
        'age_to': age_to,
        'status': 6,
        'has_photo': 1,
        'city': city_id,
        'country': country_id,
        'is_closed': False

    }
    result = api_request(URL, params)
    return result


def get_country_id(country):
    URL = 'https://api.vk.com/method/database.getCountries'
    params = {'v': '5.80', 'access_token': access_token, 'code': country}
    result = api_request(URL, params)
    return result['response']['items'][0]['id']
    


def get_city_id(city, country_id):
    URL = 'https://api.vk.com/method/database.getCities'
    params = {'v': '5.80', 'access_token': access_token, 'country_id': country_id, 'q': city}
    result = api_request(URL, params)
    return result['response']['items'][0]['id']


def find_photos(owner_id):
    URL = 'https://api.vk.com/method/photos.get'
    params = {'v': '5.80', 'access_token': access_token, 'owner_id': owner_id, 'album_id': 'profile', 'extended': 1, 'count': 1000}
    result = api_request(URL, params)

    photos = {}
    for items in result['response']['items']:
        for size in items['sizes']:
            if size['type'] == 'x':
                photos[size['url']] = items['likes']['count']

    return sorted(photos.items(), key=lambda kv: kv[1], reverse=True)[0:3]


def write_json(ten_users):
    people_list = []
    for user in ten_users:
        user_dict = {}
        user_dict['photos'] = find_photos(user['id'])
        user_dict['first name'] = user['first_name']
        user_dict['second name'] = user['last_name']
        user_dict['link'] = f"https://vk.com/id{user['id']}"
        people_list.append(user_dict)

    with open('people.json', 'w') as people_file:
        json.dump(people_list, people_file, ensure_ascii=False, indent=4)


def write_result(people):
    client = MongoClient()
    vk_db = client['VK']
    users = vk_db['users']
    for each in people['response']['items']:
        users.insert_one(each)
    return list(users.find())


def get_ten_users(people_db, n1, n2):
    ten_users = people_db[n1:n2]
    write_json(ten_users)
    print('Результаты поиска записаны в json-файл.')

    if input('Найти следующих 10 человек? (да/нет): ') == "да":
        n1 += 10
        n2 += 10
        get_ten_users(people_db, n1, n2)



def clear_my_db():
    client = MongoClient()
    vk_db = client['VK']
    users = vk_db['users']
    vk_db.users.drop()
    return list(users.find())


if __name__ == "__main__":
    welcome()

    access_token = input('Введите токен для ВК (если у Вас нет токена,\nнапечатайте "нет" и пройдите по ссылке): ')
    if access_token == "нет":
        get_token()
        access_token = input('Введите полученный токен для ВК: ')
    
    country_id = get_country_id(input('Введите код желаемой страны для поиска (RU, UA, BY и т.д.): ').capitalize())
    city_id = get_city_id(input('Введите желаемый город для поиска: ').capitalize(), country_id)
    sex = input('Введите пол (1 - жен., 2 - муж., 0 - любой): ')
    age = input('Введите диапазон возраста в формате "18-35": ')
    age_from = age[:2]
    age_to = age[-2:]
    print('Поиск в процессе...')
    people = get_people(access_token, sex, age_from, age_to, city_id, country_id)
    people_db = write_result(people)
    n1, n2 = 0, 10
    get_ten_users(people_db, n1, n2)

    # print(clear_my_db())