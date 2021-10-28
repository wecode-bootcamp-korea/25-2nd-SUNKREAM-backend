import json
import jwt

from django.test import TestCase, Client, client

from .models      import Product, Wishlist, Brand, ProductImage
from users.models import User
from my_settings  import SECRET_KEY, ALGORITHMS

client = Client()

class WishListTest(TestCase):
    def setUp(self):
        Brand.objects.create(id=1, name='나이키')
        Product.objects.create(id=1, brand_id=1, name='조단1', model_number=1234, release_price=100000)
        Product.objects.create(id=2, brand_id=1, name='조단2', model_number=4321, release_price=200000)
        ProductImage.objects.create(id=1, image_url='예쁜조단', product_id=1)
        User.objects.create(id=1, email='abcdefg1@google.com')
        Wishlist.objects.create(id=1, user_id=1, product_id=1)

        global wish_count1, wish_count2, headers
        wish_count1 = Wishlist.objects.filter(product_id=1).count()
        wish_count2 = Wishlist.objects.filter(product_id=2).count()
        access_token = jwt.encode({'user_id' : 1}, SECRET_KEY, ALGORITHMS)
        headers      = {'HTTP_AUTHORIZATION': access_token}

    def tearDown(self):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Product.objects.all().delete()
        Wishlist.objects.all().delete()
        ProductImage.objects.all().delete()

    def test_wishlist_delete_success(self):
        response = client.post('/products/wishlist?product_id=1', content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'WISH_DELETE_SUCCESS', 'wish_count' : wish_count1})

    def test_wishlist_create_success(self):
        response = client.post('/products/wishlist?product_id=2', content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message': 'WISH_CREATE_SUCCESS', 'wish_count' : wish_count2})

    def test_wishlist_create_fail(self):
        response = client.post('/products/wishlist?product_id=10', content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message:' : 'INVALID_PRODUCT_ID'})

    def test_wishlist_get_success(self):
        response = client.get('/products/wishlist', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'results' : [{
                    'brand' : '나이키', 
                    'name'  : '조단1',
                    'price' : 100000,
                    'image' : [{'thumbnail': '예쁜조단'}],
                }],
            }
        )

    def test_wishlist_get_fail(self):
        response = client.get('/products/wishlist', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'results' : [{
                    'brand' : '나이키', 
                    'name'  : '조단1',
                    'price' : 100000,
                    'image' : [{'thumbnail': '예쁜조단'}],
                }],
            }
        )

class WishFlag(TestCase):
    def setUp(self):
        Brand.objects.create(id=1, name='나이키')
        Product.objects.create(id=1, brand_id=1, name='조단1', model_number=1234, release_price=100000)
        Product.objects.create(id=2, brand_id=1, name='조단2', model_number=4321, release_price=200000)
        ProductImage.objects.create(id=1, image_url='예쁜조단', product_id=1)
        User.objects.create(id=1, email='abcdefg1@google.com')
        User.objects.create(id=2, email='abcdefg2@google.com')
        User.objects.create(id=3, email='abcdefg3@google.com')
        User.objects.create(id=4, email='abcdefg4@google.com')
        User.objects.create(id=5, email='abcdefg5@google.com')
        Wishlist.objects.create(id=1, user_id=1, product_id=1)
        Wishlist.objects.create(id=2, user_id=2, product_id=1)
        Wishlist.objects.create(id=3, user_id=3, product_id=1)
        Wishlist.objects.create(id=4, user_id=4, product_id=1)
        Wishlist.objects.create(id=5, user_id=5, product_id=1)

        global wish_count, headers
        wish_count   = Wishlist.objects.filter(product_id=1).count()
        access_token = jwt.encode({'user_id' : 2}, SECRET_KEY, ALGORITHMS)
        headers      = {'HTTP_AUTHORIZATION': access_token}

    def tearDown(self):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Product.objects.all().delete()
        Wishlist.objects.all().delete()
        ProductImage.objects.all().delete()

    def test_wishflag_get_success(self):
        response = client.get('/products/wishflag?product_id=1', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
                'results' : {
                    'wish_count' : wish_count,
                    'check_my_wish' : True,
                }
            }
        )

    def test_wishflag_get_fail(self):
        response = client.get('/products/wishflag?product_id=10', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message:' : 'INVALID_PRODUCT_ID'})