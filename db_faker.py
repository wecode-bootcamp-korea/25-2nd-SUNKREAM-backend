import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE","sunkream.settings")

import django
django.setup()


from products.models import *

import random

from django.db import transaction
from faker import Faker

fake = Faker('ko_KR') #한글로 넣어줌

#category_list = ['한국소설', '영미소설'] #지정가능
#메뉴/카테고리/작가/출판사/썸네일

with transaction.atomic() :

 

    # product_list = [Product(name='jordan', model_number=fake.random_number(), brand_id = 1 , release_price=100000) for i in range(29,300)]
    # Product.objects.bulk_create(product_list)

    # image_list = [ProductImage(image_url='https://thumbnail10.coupangcdn.com/thumbnails/remote/700x700ex/image/vendor_inventory/a9aa/a15c6027a474458123378512d26726ce048f273491268df4666779373f1d.jpg', product_id = i) for i in range(19,300)]
    # ProductImage.objects.bulk_create(image_list)

    product_size_list = [ProductSize(product_id = i , size_id=1) for i in range(1,300)]
    ProductSize.objects.bulk_create(product_size_list)

    #기용님꺼

    # Menu(
    #     name='소설'
    # ).save()

    # for i in category_list :
    #     Category(
    #         menu_id = 1,
    #         name = i
    #     ).save()

    # publisher_list = [Publisher(name = fake.company()+' 출판사') for i in range(5)]
    # Publisher.objects.bulk_create(publisher_list)

    # thumbnail_list = [Thumbnail(image_url=fake.image_url()) for i in range(30)]
    # Thumbnail.objects.bulk_create(thumbnail_list)

