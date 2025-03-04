from datetime import date

from django.forms.models import model_to_dict
from rest_framework.response import Response
from api.serializers.product import (
    CustomerProductDetailSerializer,
    CustomerProductSerializer,
    ProductSerializer,
    ProductCategorySerializer,
    ProductReconcileSerializer,
    BulkItemReconcilationApiItemSerializer
)
from rest_framework.views import APIView

from rest_framework.generics import ListAPIView, RetrieveAPIView

from product.models import CustomerProduct, Product,ProductMultiprice, BranchStockTracking, BranchStock, ItemReconcilationApiItem
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import json
from django.shortcuts import get_object_or_404
from organization.models import Branch

class ProductMultipriceapi(ListAPIView):
    def get(self, request):
        try:
            products_list = Product.objects.all().values(
        "id",
        "title",
        "slug",
        "description",
        "image",
        "price",
        "is_taxable",
        "product_id",
        "unit",
        "category",
        "barcode"
        )
            temp_data = products_list
            for index,item in enumerate(products_list):
                print(item["id"])
                queryset = ProductMultiprice.objects.filter(product_id=item["id"]).values()
                temp_data[index]["multiprice"]=queryset
            return Response(temp_data,200)

        except Exception as error:
            return Response({"message":str(error)})


class ProductTypeListView(ListAPIView):
    serializer_class = ProductCategorySerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
       
        products = Product.objects.active()

        item_type ={
            "FOOD":{
                "title":"FOOD",
                "group": []
            },
            "BEVERAGE":{
                "title":"BEVERAGE",
                "group": []
            },
            "OTHERS": {
                "title":"OTHERS",
                "group": []
            }
        }
        type_group = {"FOOD": [],"BEVERAGE": [],"OTHERS": []}

        product_list = []

        for product in products:
            product_dict =  model_to_dict(product)
            del product_dict['image']
            product_dict['type'] = product.type.title
            product_list.append(product_dict)


        for product in product_list:
            if  product['group'] not in type_group[product['type']]:
                type_group[product['type']].append(product['group'])
                item_type[product['type']]['group'].append({"title":product['group'], "items":[]})
        
        for product in product_list:
            group_list = item_type[product['type']]['group']
            for i in group_list:
                if i['title'] == product['group']:
                    i['items'].append(product)



            
        return Response(item_type)

        


class ProductList(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = None

    def get_queryset(self):
        return Product.objects.active().filter(is_billing_item=True)
    
    


class ProductDetail(RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Product.objects.active()


class CustomerProductAPI(ModelViewSet):
    serializer_class = CustomerProductSerializer
    queryset = CustomerProduct.objects.active()

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        is_added = CustomerProduct.objects.filter(
            is_deleted=False,
            status=True,
            customer=request.data["customer"],
            product=request.data["product"],
        )

        if not is_added:
            return super().create(request, *args, **kwargs)
        else:
            return Response(
                {"message": "This product is already added to the customer"},
            )

    def get_queryset(self, *args, **kwargs):
        customer_id = self.request.query_params.get("customerId")
        if customer_id:
            queryset = CustomerProduct.objects.filter(
                is_deleted=False, status=True, customer=customer_id
            )

            return queryset
        else:
            return super().get_queryset()

    def get_serializer_class(self):
        detail_actions = ["retrieve", "list"]
        if self.action in detail_actions:
            return CustomerProductDetailSerializer
        return super().get_serializer_class()




class BranchStockTrackingView(APIView):
    """
    Useless view
    """
    def post(self, request):
        serializer = ProductReconcileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        products = serializer.validated_data.get('products', [])

        for p in products:
            date = p.get('date')
            branch = p.get('branch')
            product = p.get('product')
            wastage = p.get('wastage', 0)
            returned = p.get('returned', 0)
            physical = p.get('physical', 0)
            latest_entry = BranchStockTracking.objects.filter(branch=branch, product=product, date__lt=date).order_by('-date').first()
            if latest_entry:
                """ Goes everytime in if ** INCOMPLETE ** """
                new_opening = latest_entry.physical

                try:
                    branch_stock = BranchStockTracking.objects.get(branch=branch, product=product, date=date)
                    closing = new_opening-wastage-returned-branch_stock.sold+branch_stock.received
                    discrepancy = physical - closing
                    branch_stock.opening = new_opening
                    branch_stock.wastage =  wastage
                    branch_stock.returned = returned
                    branch_stock.physical = physical
                    branch_stock.closing = closing
                    branch_stock.discrepancy = discrepancy
                    branch_stock.save()
                except BranchStockTracking.DoesNotExist:
                    closing = new_opening-wastage
                    discrepancy = physical - closing
                    BranchStockTracking.objects.create(
                        branch=branch, product=product,
                        opening=new_opening, date=date,
                        wastage=wastage, returned=returned,
                        physical=physical, closing=closing, discrepancy=discrepancy
                    )
                
        return Response({'details':'success'}, 201)



from organization.models import EndDayRecord, EndDayDailyReport
class ApiItemReconcilationView(APIView):

    def post(self, request):
        serializer = BulkItemReconcilationApiItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        EndDayRecord.objects.create(branch_id = serializer.validated_data.get('branch'),
                                     terminal=serializer.validated_data.get('terminal'),
                                     date = serializer.validated_data.get('date')
                                     )
        report_total = serializer.validated_data.get("report_total")
        new_data = {'branch_id':serializer.validated_data.get('branch'),'terminal':serializer.validated_data.get('terminal'), **report_total}
        try:
            EndDayDailyReport.objects.create(**new_data)
        except Exception as e:
            print(e)
        return Response({'details':'success'}, 201)

# from organization.models import Terminal
class CheckAllowReconcilationView(APIView):

    def get(self, request):
        today_date = date.today()
        branch_id = request.GET.get('branch_id', None)
        # terminal = request.GET.get('terminal', None)
        if not branch_id:
            return Response({'detail':'Please provide branch_id in url params'}, 400)
        # if not terminal:
        #     return Response({'detail':'Please provide terminal in url params'}, 400)
        branch = get_object_or_404(Branch, pk=branch_id)
        
        # terminal_obj = Terminal.objects.get(branch=branch, terminal_no=terminal)
        
        
        if ItemReconcilationApiItem.objects.filter(date=today_date, branch = branch).exists():
        # if ItemReconcilationApiItem.objects.filter(date=today_date, branch = branch, terminal=terminal_obj).exists():

            return Response({'detail':'Items already reconciled for today!! Please Contact Admin'}, 400)
        return Response({'details':'ok'}, 200)


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_product_requisition(request):
    data = request.data.get('data', None)
    if data:
        data = json.loads(data)
        for d in data:
            quantity = int(d['quantity'])
            BranchStock.objects.create(branch_id=d['branch_id'], product_id=d['product_id'], quantity=quantity)
        return Response({'detail':'ok'}, 201)
    return Response({'detail':'Invalid data'}, 400)
