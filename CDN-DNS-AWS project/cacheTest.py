import unittest
from httpserver import CacheLFU, fetch
from os import path
import shutil


class MyTestCase(unittest.TestCase):
    def test_cache_put(self):
        content1, code1 = fetch("/Aaron_Hernandez")
        content2, code2 = fetch("/Main_Page")
        cache = CacheLFU(len(content1 + content2))
        cache.get("/Aaron_Hernandez")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez'})
        cache.get("/Main_Page")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez', '/Main_Page'})
        cache.get("/Aaron_Hernandez")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez', '/Main_Page'})

    def test_cache_get(self):
        content1, code1 = fetch("/Aaron_Hernandez")
        cache = CacheLFU(len(content1))
        self.assertEqual(len(cache.mem_cache_key), 0)
        cache.get("/Aaron_Hernandez")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez'})
        cache.get("/Aaron_Hernandez")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez'})

    def test_cache_evict(self):
        content1, code1 = fetch("/Aaron_Hernandez")
        content2, code2 = fetch("/Main_Page")
        content3, code3 = fetch("/-")
        print(len(content1), code1, len(content2), code2, len(content3), code3)
        memo_size = len(content1) + len(content3)
        cache = CacheLFU(memo_size)
        cache.get("/Aaron_Hernandez")
        cache.get("/Main_Page")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez', '/Main_Page'})
        cache.get("/-")
        self.assertEqual(cache.mem_cache_key.keys(), {'/-', '/Main_Page'})
        cache.get("/Aaron_Hernandez")
        self.assertEqual(cache.mem_cache_key.keys(), {'/Aaron_Hernandez', '/Main_Page'})

    def test_fetch_disk(self):
        if path.exists('cache'):
            shutil.rmtree('cache')
        self.assertFalse(path.exists('cache/-'))
        fetch('/-')
        self.assertTrue(path.exists('cache/-'))

    def test_evict_remove_file_from_disk(self):
        if path.exists('cache'):
            shutil.rmtree('cache')
        cache = CacheLFU(81222)
        self.assertFalse(path.exists('cache/Main_Page'))
        cache.get('/Main_Page')
        self.assertTrue(path.exists('cache/Main_Page'))
        cache.get('/Aaron_Hernandez')
        self.assertFalse(path.exists('cache/Main_Page'))
        self.assertTrue(path.exists('cache/Aaron_Hernandez'))


if __name__ == '__main__':
    unittest.main()
