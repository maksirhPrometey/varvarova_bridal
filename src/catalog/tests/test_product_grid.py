from django.test import SimpleTestCase

from src.catalog.product_grid import pick_grid_columns
from src.catalog.selectors import gallery_rows


class PickGridColumnsTests(SimpleTestCase):
    def test_empty(self):
        self.assertEqual(pick_grid_columns(0), 2)

    def test_one_or_two_use_three(self):
        self.assertEqual(pick_grid_columns(1), 3)
        self.assertEqual(pick_grid_columns(2), 3)

    def test_known_counts(self):
        self.assertEqual(pick_grid_columns(5), 5)
        self.assertEqual(pick_grid_columns(6), 3)
        self.assertEqual(pick_grid_columns(7), 4)
        self.assertEqual(pick_grid_columns(8), 4)
        self.assertEqual(pick_grid_columns(9), 3)
        self.assertEqual(pick_grid_columns(10), 5)
        self.assertEqual(pick_grid_columns(11), 4)


class GalleryRowsTests(SimpleTestCase):
    def test_empty(self):
        self.assertEqual(gallery_rows([]), [])

    def test_one_image_is_full(self):
        rows = gallery_rows(['a'])
        self.assertEqual(rows, [{'kind': 'full', 'images': ['a']}])

    def test_two_images_are_pair(self):
        rows = gallery_rows(['a', 'b'])
        self.assertEqual(rows, [{'kind': 'pair', 'images': ['a', 'b']}])

    def test_masonry_pattern(self):
        rows = gallery_rows(['a', 'b', 'c', 'd'])
        self.assertEqual(rows[0]['kind'], 'full')
        self.assertEqual(rows[1]['kind'], 'pair')
        self.assertEqual(rows[2]['kind'], 'full')
