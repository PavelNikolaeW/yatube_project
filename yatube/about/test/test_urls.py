from django.test import TestCase, Client


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_guest_client(self):
        urls = [
            '/about/tech/',
            '/about/author/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
