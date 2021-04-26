import bs4
from http_helper import *
import sys
from collections import deque

root = 'http://cs5700.ccs.neu.edu'

visited = set()
url_queue = deque()

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]

# USERNAME = 's'
# PASSWORD = 's'

http_request = HttpHelper()

# if login failed, exit the program with the error message of "login failed"
if not http_request.login(USERNAME, PASSWORD):
    exit("login failed")
url_queue.append(root)

while url_queue:
    curr_url = url_queue.popleft()
    visited.add(curr_url)
    html = http_request.get(curr_url)
    if html:
        soup = bs4.BeautifulSoup(html, 'html.parser')
        flags = soup.find_all('h2', {'class': 'secret_flag'})
        for flag in flags:
            print(flag.text)
        for tag in soup.find_all('a', href=True):
            link = tag['href']
            if root + link in visited:
                continue
            if link.startswith('/') or link.startswith(root):
                url_queue.append(root + link)

