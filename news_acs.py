from bs4 import BeautifulSoup
import requests

source = requests.get('https://acs.pub.ro').text
soup = BeautifulSoup(source, 'lxml')

news = soup.find_all('li', class_ = 'recent-post-item')
for recent_post in news:
    print(recent_post.find('p', class_ = 'post-date').text + ': ', end = '')
    print(recent_post.a.text + ' (' + recent_post.a['href'] + ')')

input("Press any key to exit...")