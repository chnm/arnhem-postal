from django.contrib.gis.geos import Point
from django.test import TestCase

from postcards.models import Object, Postmark


class ObjectModelTest(TestCase):
    def setUp(self):
        self.object = Object.objects.create(name="Test Object")

    def test_object_creation(self):
        self.assertEqual(Object.objects.count(), 1)
        self.assertEqual(self.object.name, "Test Object")


class PostmarkModelTest(TestCase):
    def setUp(self):
        self.object = Object.objects.create(name="Test Object")
        self.postmark = Postmark.objects.create(
            object=self.object, location=Point(5, 5)
        )

    def test_postmark_creation(self):
        self.assertEqual(Postmark.objects.count(), 1)
        self.assertEqual(self.postmark.object.name, "Test Object")
        self.assertEqual(self.postmark.location.x, 5)
        self.assertEqual(self.postmark.location.y, 5)
