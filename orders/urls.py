from django.urls  import path

from orders.views import BiddingView, SizePriceView, OrderView, PriceHistoryView, OrderListView

urlpatterns = [
    path('/bidding/<int:productsize_id>/<int:position_id>', BiddingView.as_view()),
    path('/size-price/<int:product_id>/<int:position_id>', SizePriceView.as_view()),
    path('/<int:bidding_id>', OrderView.as_view()),
    path('/price/<int:product_id>', PriceHistoryView.as_view()),
    path('', OrderListView.as_view()),
]
