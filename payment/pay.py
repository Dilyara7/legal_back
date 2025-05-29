from django.shortcuts import render ,redirect
import uuid
import json
from yookassa import Configuration, Payment
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User
from store_app.models import ShoppingCart
Configuration.account_id = 508553
Configuration.secret_key = 'test_*gsyeb3AGNmMI3juBTqQXLsiwkyL7cJWRfnFG7tfHa9s4'


class OrderPaymentPageView(TemplateView):
    template_name = 'shop/orders.html'

    def post(self,request, *args, **kwargs):

        amount = 0
        
        orders = ShoppingCart.objects.filter(user = self.request.user)
        
        for i in orders:
            amount += i.product.price * i.count
        if amount <= 0:
            return redirect('/ru/products/')
        payment = Payment.create({
            "amount": {
                "value": f"{amount}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "localhost:8000"
            },
            "capture": True,
            "description": f"Tanda одежда на выбор"
        }, uuid.uuid4())
        
        return redirect(payment.confirmation.confirmation_url)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    
   
@require_POST
@csrf_exempt
def yookassa_notification(request):
    try:
        data = json.loads(request.body)
        payment_id = data.get('object', {}).get('id')
        status = data.get('object', {}).get('status')
        event = data.get('event')
        
        if(event == 'payment.succeeded'):

            return HttpResponse(status=200)
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=400)