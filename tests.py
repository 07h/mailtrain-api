import unittest

from dotenv import load_dotenv
from os import getenv as env

from mailtrain import Mailtrain

load_dotenv()

LIST_ID = env("MAILTRAIN_LIST_ID")
TEST_EMAIL = env("MAILTRAIN_TEST_EMAIL")


class TestMailtrain(unittest.TestCase):
    def setUp(self):
        self.mt = Mailtrain(env("MAILTRAIN_API_KEY"), env("MAILTRAIN_URL"))

    def test_get_subscribers(self):
        subscribers = self.mt.get_subscribers(LIST_ID)
        self.assertIsInstance(subscribers, list)

    def test_add_subscription(self):
        subscriber = self.mt.add_subscription(TEST_EMAIL, LIST_ID)
        self.assertIsInstance(subscriber, dict)

    def test_unsubscribe(self):
        subscriber = self.mt.unsubscribe(TEST_EMAIL, LIST_ID)
        self.assertIsInstance(subscriber, dict)

    def test_delete_subscription(self):
        subscriber = self.mt.delete_subscription(TEST_EMAIL, LIST_ID)
        self.assertIsInstance(subscriber, dict)

    def test_create_custom_field(self):
        field = self.mt.create_custom_field(LIST_ID, "test", "text")
        self.assertIsInstance(field, dict)

    def test_get_blacklist(self):
        blacklist = self.mt.get_blacklist()
        self.assertIsInstance(blacklist, list)

    def test_add_to_blacklist(self):
        blacklist = self.mt.add_to_blacklist(TEST_EMAIL)
        self.assertIsInstance(blacklist, dict)

    def test_delete_from_blacklist(self):
        blacklist = self.mt.delete_from_blacklist(TEST_EMAIL)
        self.assertIsInstance(blacklist, dict)

    def test_get_lists(self):
        lists = self.mt.get_lists(TEST_EMAIL)
        self.assertIsInstance(lists, list)

    def test_get_lists_by_namespace(self):
        lists = self.mt.get_lists_by_namespace("test")
        self.assertIsInstance(lists, list)

    def test_create_list(self):
        list = self.mt.create_list("test", "test")
        self.assertIsInstance(list, dict)

    def test_delete_list(self):
        list = self.mt.delete_list("test")
        self.assertIsInstance(list, dict)

    def test_fetch_rss(self):
        rss = self.mt.fetch_rss("https://www.reddit.com/.rss")
        self.assertIsInstance(rss, dict)

    def test_send_email_by_template(self):
        email = self.mt.send_email_by_template(TEST_EMAIL)
        self.assertIsInstance(email, dict)
