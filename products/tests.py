import json
import jwt

from django.test import TestCase, Client, client


from products.models import Brand, Product, ProductSize, Size, ProductImage, Wishlist
from orders.models import Bidding, BiddingPosition, BiddingStatus
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

class ProductTest(TestCase):
    maxDiff = None

    def setUp(self):
        user1             = User.objects.create(id =1, email = 'user1@gmail.com')
        user2             = User.objects.create(id =2, email = 'user2@gmail.com')
        brand1            = Brand.objects.create(id = 1, name = 'nike')
        brand2            = Brand.objects.create(id = 2, name = 'converse')
        brand3            = Brand.objects.create(id = 3, name = 'vans')  
        product1          = Product.objects.create(id = 1, brand = brand1, name = 'product1', model_number = '100', release_price = 100000)
        product2          = Product.objects.create(id = 2, brand = brand1, name = 'product2', model_number = '200', release_price = 150000)
        product_image     = ProductImage.objects.create(id = 1, product = product1, image_url = '1')
        product_image2    = ProductImage.objects.create(id = 2, product = product2, image_url = '2')
        size1             = Size.objects.create(id = 1, size = 300)
        size2             = Size.objects.create(id = 2, size = 310)
        product_size1     = ProductSize.objects.create(id = 1, product = product1, size = size1)
        product_size2     = ProductSize.objects.create(id = 2, product = product1, size = size2)
        product_size3     = ProductSize.objects.create(id = 3, product = product2, size = size1)
        product_size4     = ProductSize.objects.create(id = 4, product = product2, size = size2)
        bidding_position1 = BiddingPosition.objects.create(id = 1, position = 'BUY')
        bidding_position2 = BiddingPosition.objects.create(id = 2, position = 'SELL')
        bidding_status1   = BiddingStatus.objects.create(id = 1, status = 'ON_BIDDING')
        bidding_status2   = BiddingStatus.objects.create(id = 2, status = 'CONTRACTED')
        bidding1          = Bidding.objects.create(
                            id               = 1,
                            user             = user1, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 300000)
        bidding2          = Bidding.objects.create(
                            id               = 2,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status2,
                            bidding_position = bidding_position2, 
                            price            = 300000)

    def tearDown(self):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Product.objects.all().delete()
        Size.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductSize.objects.all().delete()
        BiddingPosition.objects.all().delete()
        BiddingStatus.objects.all().delete()
        Bidding.objects.all().delete()

    def test_product_get_success(self):
        client = Client()
        
        response = client.get('/products')


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
        {
            "products_list"   :    [
                    {
                            'id'            : 1,
                            'brand'         : 'nike',
                            'name'          : 'product1',
                            'thumbnail_url' : '1',
                            'product_price' : None,
                            'release_price' : 100000,
                    },
                    {
                            'id'            : 2,
                            'brand'         : 'nike',
                            'name'          : 'product2',
                            'thumbnail_url' : '2',
                            'product_price' : None,
                            'release_price' : 150000,
                    }
                ]
        }
        )

    def test_brand_get_success(self):
        client = Client()
        
        response = client.get('/products/brand')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
        {
            "brand_list"   :    [
                    {
                            'brand_id'            : 1,
                            'brand_name'         : 'nike',
                    },
                    {
                            'brand_id'            : 2,
                            'brand_name'         : 'converse',
                    },
                    {
                            'brand_id'            : 3,
                            'brand_name'         : 'vans',
                    }
                ]
        }
        )

    def test_productdetail_get_success(self):
        client = Client()
        
        response = client.get('/products/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
        {
            "product_detail" : {
                'product_id'      : 1,
                'name'            : 'product1',
                'brand_name'      : 'nike',
                'release_price'   : 100000,
                'model_number'    : 100,
                'image_list'      : "1",
                'recent_price'    : 0,
                'buy_price'       : 300000,
                'sell_price'      : 300000,
                'total_wishlist'  : 0,
            }
        }
        )