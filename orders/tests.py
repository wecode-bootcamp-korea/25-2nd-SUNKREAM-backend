import json
import jwt

from django.test     import TestCase, Client
from django.conf     import settings

from users.models    import User
from products.models import Brand, Product, ProductSize, Size, ProductImage
from orders.models   import Order, OrderStatus, Bidding, BiddingPosition, BiddingStatus

class BiddingTest(TestCase):
    def setUp(self):
        global headers
        access_token      = jwt.encode({'user_id':1}, settings.SECRET_KEY, settings.ALGORITHMS)
        headers           = {'HTTP_AUTHORIZATION': access_token}
        user1             = User.objects.create(id =1, email = 'user1@gmail.com', point = 350000)
        brand             = Brand.objects.create(name = 'nike')
        product           = Product.objects.create(id = 1, brand = brand, name = 'product1', model_number = '100', release_price = 100000)
        size              = Size.objects.create(id = 1, size = 300)
        product_size      = ProductSize.objects.create(id = 1, product = product, size = size)
        product_image     = ProductImage.objects.create(id =1, product = product, image_url = 'url1')
        bidding_position1 = BiddingPosition.objects.create(id = 1, position = 'BUY')
        bidding_position2 = BiddingPosition.objects.create(id = 2, position = 'SELL')
        bidding_status1   = BiddingStatus.objects.create(id = 1, status = 'ON_BIDDING')
        bidding_status2   = BiddingStatus.objects.create(id = 2, status = 'CONTRACTED')
        bidding1          = Bidding.objects.create(
                            id               = 1,
                            user             = user1, 
                            product_size     = product_size,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 300000)
        bidding2          = Bidding.objects.create(
                            id               = 2,
                            user             = user1, 
                            product_size     = product_size,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position2, 
                            price            = 400000)
    
    def tearDown(self):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Product.objects.all().delete()
        Size.objects.all().delete()
        ProductSize.objects.all().delete()
        BiddingPosition.objects.all().delete()
        BiddingStatus.objects.all().delete()
        Bidding.objects.all().delete()
    
    def test_bidding_post_success(self):
        client = Client()
        data   = {
            "price"   : 200000
        }

        response = client.post('/orders/bidding/1/1', json.dumps(data), content_type = 'application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "message" : "SUCCESS"
            }
        )
    
    def test_bidding_post_unauthorized(self):
        client = Client()
        data   = {
            "price"   : 200000
        }

        response = client.post('/orders/bidding/1/1', json.dumps(data), content_type = 'application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )
    
    def test_bidding_post_product_size_does_not_exist(self):
        client = Client()
        data   = {
            "price"   : 200000
        }

        response = client.post('/orders/bidding/5/1', json.dumps(data), content_type = 'application/json', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : 'PRODUCT_SIZE_DOES_NOT_EXIST'
            }
        )

    def test_bidding_post_invalid_bidding_position(self):
        client = Client()
        data   = {
            "price"   : 200000
        }

        response = client.post('/orders/bidding/1/3', json.dumps(data), content_type = 'application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_BIDDING_POSITION"
            }
        )
    
    def test_bidding_post_key_error(self):
        client = Client()
        data   = {
            "pricee"   : 200000
        }

        response = client.post('/orders/bidding/1/1', json.dumps(data), content_type = 'application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "KEY_ERROR"
            }
        )
    
    def test_bidding_post_jsondecode_error(self):
        client = Client()

        response = client.post('/orders/bidding/1/1', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "JSON_DECODE_ERROR"
            }
        )

    def test_bidding_get_success(self):
        client = Client()

        response = client.get('/orders/bidding/1/1', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {            
                "data": {
                            "product_image_url"    : 'url1',
                            "product_name"         : "product1",
                            "product_brand"        : "nike",
                            "product_model_number" : "100",
                            "size"                 : 300,
                            "sell_price"           : 300000,
                            "buy_price"            : 400000,
                            "user_point"           : 350000,
                            "bidding_id"           : 1,
                            "bidding_price"        : 300000
                        }
            }
        )

    def test_bidding_get_product_size_does_not_exist(self):
        client = Client()
    
        response = client.get('/orders/bidding/2/1', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : 'PRODUCT_SIZE_DOES_NOT_EXIST'
            }
        )

    def test_bidding_get_invalid_bidding_position(self):
        client = Client()
  
        response = client.get('/orders/bidding/1/3', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_BIDDING_POSITION"
            }
        )

class OrderTest(TestCase):
    def setUp(self):
        global headers, headers2
        access_token      = jwt.encode({'user_id':1}, settings.SECRET_KEY, settings.ALGORITHMS)
        access_token2     = jwt.encode({'user_id':2}, settings.SECRET_KEY, settings.ALGORITHMS)
        headers           = {'HTTP_AUTHORIZATION': access_token}
        headers2          = {'HTTP_AUTHORIZATION': access_token2}
        user1             = User.objects.create(id =1, email = 'user1@gmail.com', point = 500000)
        user2             = User.objects.create(id =2, email = 'user2@gmail.com', point = 200000)
        brand             = Brand.objects.create(name = 'nike')
        product           = Product.objects.create(id = 1, brand = brand, name = 'product1', model_number = '100', release_price = 100000)
        size              = Size.objects.create(id = 1, size = 300)
        product_size1     = ProductSize.objects.create(id = 1, product = product, size = size)
        product_image     = ProductImage.objects.create(id =1, product = product, image_url = 'url1')
        bidding_position1 = BiddingPosition.objects.create(id = 1, position = 'BUY')
        bidding_position2 = BiddingPosition.objects.create(id = 2, position = 'SELL')
        bidding_status1   = BiddingStatus.objects.create(id = 1, status = 'ON_BIDDING')
        bidding_status2   = BiddingStatus.objects.create(id = 2, status = 'CONTRACTED')
        order_status1     = OrderStatus.objects.create(id = 1, status = '검수중')
        order_status2     = OrderStatus.objects.create(id = 2, status = '배송중')
        order_status3     = OrderStatus.objects.create(id = 3, status = '배송완료')
        bidding1          = Bidding.objects.create(
                            id               = 1,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position2, 
                            price            = 300000)
        bidding2          = Bidding.objects.create(
                            id               = 2,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position2, 
                            price            = 600000)
        bidding3          = Bidding.objects.create(
                            id               = 3,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status2,
                            bidding_position = bidding_position2, 
                            price            = 300000)
        bidding4          = Bidding.objects.create(
                            id               = 4,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 300000)
        bidding5          = Bidding.objects.create(
                            id               = 5,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 600000)
        bidding6          = Bidding.objects.create(
                            id               = 6,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 300000)
        order1            = Order.objects.create(
                            id               = 1,
                            buyer            = user2,
                            seller           = user1,
                            bidding          = bidding4,
                            order_status     = order_status1)
        order2            = Order.objects.create(
                            id               = 2,
                            buyer            = user1,
                            seller           = user2,
                            bidding          = bidding1,
                            order_status     = order_status2)
    
    def tearDown(self):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Product.objects.all().delete()
        Size.objects.all().delete()
        ProductSize.objects.all().delete()
        BiddingPosition.objects.all().delete()
        BiddingStatus.objects.all().delete()
        OrderStatus.objects.all().delete()
        Bidding.objects.all().delete()
    
    def test_order_post_success(self):
        client = Client()

        response = client.post('/orders/1', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "message" : "SUCCESS"
            }
        )
    
    def test_order_post_unauthorized(self):
        client = Client()

        response = client.post('/orders/1')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )
    
    def test_order_post_insufficient_point(self):
        client = Client()

        response = client.post('/orders/2', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INSUFFICIENT_POINT"
            }
        )
    
    def test_order_post_invalid_bidding_id(self):
        client = Client()

        response = client.post('/orders/10', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : "BIDDING_DOES_NOT_EXIST"
            }
        )
    
    def test_order_post_invalid_bidding_status(self):
        client = Client()

        response = client.post('/orders/3', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_BIDDING_ID"
            }
        )
    
    def test_orderlist_get_success(self):
        client = Client()

        response = client.get('/orders', **headers2)

        data = {
            'user_point'            : 200000,
            'buy_order_count'       : 1,
            'buy_order_list'        : [{
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300,
                'order_status'      : '검수중',
            }],
            "sell_order_count"      : 1,
            'sell_order_list'       : [{
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300,
                'order_status'      : '배송중',
            }],
            'buy_on_bidding_count'  : 3,
            'buy_bidding_list'      : [{
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300
            },
            {
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300
            },
            {
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300
            }],
            'sell_on_bidding_count' : 2,
            'sell_bidding_list'     : [{
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300
            },
            {
                'product_id'        : 1,
                'product_image_url' : 'url1',
                'product_name'      : 'product1',
                'product_brand'     : 'nike',
                'size'              : 300
            }]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
               'data' : data
            }
        )
    
    def test_orderlist_get_unauthorized(self):
        client = Client()

        response = client.get('/orders')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )

class PriceTest(TestCase):
    def setUp(self):
        global headers, order1, order2, order3, order4, order5, order6
        access_token      = jwt.encode({'user_id':1}, settings.SECRET_KEY, settings.ALGORITHMS)
        headers           = {'HTTP_AUTHORIZATION': access_token}
        user1             = User.objects.create(id =1, email = 'user1@gmail.com', point = 500000)
        user2             = User.objects.create(id =2, email = 'user2@gmail.com', point = 200000)
        brand             = Brand.objects.create(name = 'nike')
        product           = Product.objects.create(id = 1, brand = brand, name = 'product1', model_number = '100', release_price = 100000)
        size1             = Size.objects.create(id = 1, size = 300)
        size2             = Size.objects.create(id = 2, size = 310)
        product_size1     = ProductSize.objects.create(id = 1, product = product, size = size1)
        product_size2     = ProductSize.objects.create(id = 2, product = product, size = size2)
        product_image     = ProductImage.objects.create(id =1, product = product, image_url = 'url1')
        bidding_position1 = BiddingPosition.objects.create(id = 1, position = 'BUY')
        bidding_position2 = BiddingPosition.objects.create(id = 2, position = 'SELL')
        bidding_status1   = BiddingStatus.objects.create(id = 1, status = 'ON_BIDDING')
        bidding_status2   = BiddingStatus.objects.create(id = 2, status = 'CONTRACTED')
        order_status1     = OrderStatus.objects.create(id = 1, status = '검수중')
        order_status2     = OrderStatus.objects.create(id = 2, status = '배송중')
        order_status3     = OrderStatus.objects.create(id = 3, status = '배송완료')
        buy_bidding1      = Bidding.objects.create(
                            id               = 1,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 300000)
        buy_bidding2      = Bidding.objects.create(
                            id               = 2,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 600000)
        buy_bidding3      = Bidding.objects.create(
                            id               = 3,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position1, 
                            price            = 500000)
        sell_bidding1     = Bidding.objects.create(
                            id               = 4,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position2, 
                            price            = 300000)
        sell_bidding2     = Bidding.objects.create(
                            id               = 5,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position2, 
                            price            = 300000)
        sell_bidding3     = Bidding.objects.create(
                            id               = 6,
                            user             = user2, 
                            product_size     = product_size1,
                            bidding_status   = bidding_status1,
                            bidding_position = bidding_position2, 
                            price            = 500000)
        order1            = Order.objects.create(
                            id               = 1,
                            order_status     = order_status1,
                            bidding          = buy_bidding1,
                            buyer            = user1,
                            seller           = user2)
        order2            = Order.objects.create(
                            id               = 2,
                            order_status     = order_status1,
                            bidding          = buy_bidding2,
                            buyer            = user1,
                            seller           = user2)
        order3            = Order.objects.create(
                            id               = 3,
                            order_status     = order_status1,
                            bidding          = buy_bidding3,
                            buyer            = user1,
                            seller           = user2)
        order4            = Order.objects.create(
                            id               = 4,
                            order_status     = order_status1,
                            bidding          = sell_bidding1,
                            buyer            = user2,
                            seller           = user1)
        order5            = Order.objects.create(
                            id               = 5,
                            order_status     = order_status1,
                            bidding          = sell_bidding2,
                            buyer            = user2,
                            seller           = user1)
        order6            = Order.objects.create(
                            id               = 6,
                            order_status     = order_status1,
                            bidding          = sell_bidding3,
                            buyer            = user2,
                            seller           = user1)

    def tearDown(self):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Product.objects.all().delete()
        Size.objects.all().delete()
        ProductSize.objects.all().delete()
        BiddingPosition.objects.all().delete()
        BiddingStatus.objects.all().delete()
        OrderStatus.objects.all().delete()
        Bidding.objects.all().delete()

    def test_sizeprice_get_success(self):
        client = Client()
        response = client.get('/orders/size-price/1/1', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "product_info" : {
                'product_image_url'    : 'url1',
                'product_name'         : 'product1',
                'product_brand'        : 'nike',
                'product_model_number' : '100',
                },

                "size_price_list" : [
                    {
                        "productsize_id" : 1,
                        "size"           : 300,
                        "bidding_id"     : 2,
                        "bidding_price"  : 600000
                    },
                    {
                        "productsize_id" : 2,
                        "size"           : 310,
                        "bidding_id"     : None,
                        "bidding_price"  : None
                    }
                ]       
            }
        )
    
    def test_sizeprice_get_product_does_not_exist(self):
        client   = Client()
        response = client.get('/orders/size-price/2/2', **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : "PRODUCT_DOES_NOT_EXIST"
            }
        )
    
    def test_sizeprice_get_invalid_bidding_position(self):
        client   = Client()
        response = client.get('/orders/size-price/1/3', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_BIDDING_POSITION"
            }
        )
    
    def test_pricehistory_get_success(self):
        client   = Client()
        response = client.get('/orders/price/1')

        data = {            
            'order_graph_data' : [
                {
                    "id"         : 1,
                    "price"      : 300000,
                    "created_at" : order1.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 2,
                    "price"      : 600000,
                    "created_at" : order2.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 3,
                    "price"      : 500000,
                    "created_at" : order3.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 4,
                    "price"      : 300000,
                    "created_at" : order4.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 5,
                    "price"      : 300000,
                    "created_at" : order5.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 6,
                    "price"      : 500000,
                    "created_at" : order6.created_at.strftime('%Y-%m-%d')
                }
            ],
            'order_list' : [
                {
                    "id"         : 6,
                    "price"      : 500000,
                    "size"       : 300,
                    "created_at" : order6.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 5,
                    "price"      : 300000,
                    "size"       : 300,
                    "created_at" : order5.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 4,
                    "price"      : 300000,
                    "size"       : 300,
                    "created_at" : order4.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 3,
                    "price"      : 500000,
                    "size"       : 300,
                    "created_at" : order4.created_at.strftime('%Y-%m-%d')
                },
                {
                    "id"         : 2,
                    "price"      : 600000,
                    "size"       : 300,
                    "created_at" : order4.created_at.strftime('%Y-%m-%d')
                }
            ],
            'sell_bidding_list' : [
                {
                    "price" : 300000,
                    "size"  : 300,
                    "count" : 2
                },
                {
                    "price" : 500000,
                    "size"  : 300,
                    "count" : 1
                }
            ],
            'buy_bidding_list' : [
                {
                    "price" : 600000,
                    "size"  : 300,
                    "count" : 1
                },
                {
                    "price" : 500000,
                    "size"  : 300,
                    "count" : 1
                },
                {
                    "price" : 300000,
                    "size"  : 300,
                    "count" : 1
                },
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
               'data' : data
            }
        )
    
    def test_pricehistory_get_product_does_not_exist(self):
        client   = Client()
        response = client.get('/orders/price/2')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), 
            {
                "message"  : "PRODUCT_DOES_NOT_EXIST"
            }
        )

    def test_pricehistory_get_product_size_does_not_exist(self):
        client   = Client()
        response = client.get('/orders/price/1?size=400')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), 
            {
                "message"  : "PRODUCT_SIZE_DOES_NOT_EXIST"
            }
        )


