import unittest
from selenium import webdriver
import csv

HOST = 'localhost'


class HTTPStressTest(unittest.TestCase):
    def test_stress(self):
        browser = webdriver.Chrome('./chromedriver')

        with open('pageviews.csv', newline='') as pages:
            reader = csv.reader(pages, delimiter=',')
            for row in reader:
                url = 'http://{}:40001/{}'.format(HOST, row[0])
                browser.get(url)
        browser.close()


if __name__ == '__main__':
    unittest.main()
