from seleniumbase import BaseCase

class MyTestClass(BaseCase):

    def test_extract_links(self):
        # URL of the webpage containing the table
        url = 'https://finviz.com/quote.ashx?t=QQQ&ty=c&ta=1&p=d'

        # Open the webpage with SeleniumBase
        self.open(url)

        # Find all 'a' tags with class 'tab-link' within the first 'div'
        links = self.find('div').find_all('a', class_='tab-link')

        # Extract and print the text of each link
        for link in links:
            print(link.text)

if __name__ == "__main__":
    MyTestClass().test_extract_links()