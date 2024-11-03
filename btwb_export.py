import requests
from bs4 import BeautifulSoup
import re

def login(username, password):
    login_url = 'https://beyondthewhiteboard.com/signin'
    session = requests.Session()
    login_page = session.get(login_url)
    login_soup = BeautifulSoup(login_page.content, 'html.parser')
    authenticity_token = login_soup.find('input', {'name': 'authenticity_token'})['value']

    payload = {
        'user[email]': username,
        'user[password]': password,
        'authenticity_token': authenticity_token
    }

    response = session.post(login_url, data=payload)
    return session, response.url

def extract_member_id(url):
    match = re.search(r'/members/(\d+)/', url)
    if match:
        return match.group(1)
    return None

def get_workout_results(session, member_id):
    results_url = f'https://beyondthewhiteboard.com/members/{member_id}/workout_sessions'
    response = session.get(results_url)
    return response.content

def parse_workout_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    workout_sessions = soup.find_all('li', class_='workout_session')
    results = []

    for session in workout_sessions:
        title = session.find('div', class_='item_title').get_text(strip=True)
        description = session.find('div', class_='workout-description').get_text(strip=True)
        results.append({'title': title, 'description': description})

    return results

def save_results_to_file(results, filename):
    with open(filename, 'w') as file:
        for result in results:
            file.write(f"Title: {result['title']}\n")
            file.write(f"Description: {result['description']}\n\n")

if __name__ == '__main__':
    username = input('Enter your email: ')
    password = input('Enter your password: ')

    session, login_url = login(username, password)
    member_id = extract_member_id(login_url)

    if member_id:
        html_content = get_workout_results(session, member_id)
        results = parse_workout_results(html_content)
        save_results_to_file(results, 'workout_results.txt')
        print('Workout results saved to workout_results.txt')
    else:
        print('Failed to extract member ID from login URL')
