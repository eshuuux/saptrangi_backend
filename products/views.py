import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import Carousel, Product, Banner
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse , redirect

# Create your views here.

@csrf_exempt
def carousel(request):
    if request.method=="POST":
        try:
            body=json.loads(request.body)
            c=Carousel.objects.create(
                name=body.get('name'),
                desktop_image=body.get('desktop_img'),
                mobile_image=body.get('mobile_img')
            )
            return JsonResponse({"message":"Added !", "id":c.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error":"use post method"}, status=400)

def get_carousel(request):
    data=list(Carousel.objects.values())
    return JsonResponse(data, safe=False)

@csrf_exempt
def product(request):
    if request.method=="POST":
        try:
            body=json.loads(request.body)
            images = body.get('product_images',[])
            p=Product.objects.create(
            name=body.get('name'),
            mrp=body.get('mrp'),
            price=body.get('price'),
            rating=body.get('rating'),
            discount=body.get('discount'),
            product_images=images,
            category=body.get('category'),
            top_picks=body.get('top_picks'),
            )
            return JsonResponse({"message":"product added", "id":p.id},status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)},status=400)
    else:
        return JsonResponse({"error":"use post method"}, status=400)

def get_product(request):
    data=list(Product.objects.values())
    return JsonResponse(data, safe=False)

@csrf_exempt
def banner(request):
    if request.method=="POST":
        try:
            body=json.loads(request.body)
            b=Banner.objects.create(
                name=body.get('name'),
                banner_image=body.get('banner_img'),
            )
            return JsonResponse({"message":"Added", "id":b.id})
        except Exception as e :
            return JsonResponse({"error": str(e)},status=400)
    else:
        return JsonResponse({"error":"use post method"},status=400)

def get_banner(request):
    data=list(Banner.objects.values())
    return JsonResponse(data, safe=False)
            
