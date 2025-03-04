# views.py
from rest_framework import viewsets, status
from bill.models import tbldeliveryhistory, tbldelivery_details
from api.serializers.delivery import DeliveryHistorySerializer, DeliveryDetailsSerializer, DeliveryDetailsSerializer_combine, DeliveryHistorySerializerNoCus


class DeliveryHistoryViewSet(viewsets.ModelViewSet):
    queryset = tbldeliveryhistory.objects.all()
    serializer_class = DeliveryHistorySerializerNoCus

# class DeliveryDetailsViewSet(viewsets.ModelViewSet):
#     queryset = tbldelivery_details.objects.all()
#     serializer_class = DeliveryDetailsSerializer

from rest_framework.response import Response

class DeliveryDetailsViewSet(viewsets.ModelViewSet):
    queryset = tbldelivery_details.objects.all()
    serializer_class = DeliveryDetailsSerializer

    def create(self, request, *args, **kwargs):
        # Check if the data is a list (many=True)
        is_many = isinstance(request.data, list)

        # If it's a list, iterate through each item and validate
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        # Save each instance in the list
        if is_many:
            self.perform_create(serializer)
        else:
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        


from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
import jwt

# class DeliveryHistoryAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Filter instances with Current_state 'Ordered'
#         queryset = tbldeliveryhistory.objects.filter(Current_state='Ordered')

#         # Organize data by delivery_option and date in descending order
#         ordered_data = {}
#         delivery_options = tbldeliveryhistory.objects.values('delivery_option').distinct()

#         for option in delivery_options:
#             delivery_option = option['delivery_option']
#             delivery_data = queryset.filter(delivery_option=delivery_option).order_by('-date')

#             if delivery_option not in ordered_data:
#                 ordered_data[delivery_option] = []

#             for data in delivery_data:
#                 serializer = DeliveryHistorySerializer(data)
#                 delivery_details = tbldelivery_details.objects.filter(deliveryHistoryid=data.id)
#                 details_serializer = DeliveryDetailsSerializer(delivery_details, many=True)

#                 serialized_data = serializer.data
#                 serialized_data['delivery_details'] = details_serializer.data

#                 ordered_data[delivery_option].append(serialized_data)

#         return Response(ordered_data)

class DeliveryHistoryAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    def get(self, request, *args, **kwargs):
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        jwt_token = jwt_token.split()[1]
        try:
            token_data = jwt.decode(jwt_token, options={"verify_signature": False})
            user_id = token_data.get("user_id")
            branch = token_data.get("branch")
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
        except jwt.DecodeError:
            print("Token is invalid.")

        # Filter instances with Current_state 'Ordered'
        queryset = tbldeliveryhistory.objects.filter(Current_state='Ordered', is_deleted=False)

        # Organize data by delivery_option and date in descending order
        ordered_data = {}
        delivery_options = set()


        for data in queryset.order_by('-created_at'):
            delivery_option = data.delivery_option

            if delivery_option not in delivery_options:
                delivery_options.add(delivery_option)

        for option in delivery_options:
            delivery_option = option
            delivery_data = queryset.filter(delivery_option=delivery_option, is_deleted=False).order_by('id')

            if delivery_option not in ordered_data:
                ordered_data[delivery_option] = []

            for data in delivery_data:
                serializer = DeliveryHistorySerializer(data)
                delivery_details = tbldelivery_details.objects.filter(deliveryHistoryid=data.id, is_deleted=False)
                details_serializer = DeliveryDetailsSerializer_combine(
                    delivery_details, many=True, context={"branch": branch}
                )

                serialized_data = serializer.data
                serialized_data['delivery_details'] = details_serializer.data

                ordered_data[delivery_option].append(serialized_data)

        return Response(ordered_data)

from rest_framework.views import APIView
from datetime import datetime

class DeliveryHistoryDateAPIView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        jwt_token = jwt_token.split()[1]
        try:
            token_data = jwt.decode(jwt_token, options={"verify_signature": False})
            user_id = token_data.get("user_id")
            branch = token_data.get("branch")
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
            return Response({"detail": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            print("Token is invalid.")
            return Response({"detail": "Token is invalid."}, status=status.HTTP_401_UNAUTHORIZED)

        date_param = self.kwargs.get('date')  # Assuming the date is passed as a parameter in the URL

        # Convert the date parameter to a datetime object
        try:
            date = datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter instances with Current_state 'Ordered' and the specified date
        queryset = tbldeliveryhistory.objects.filter(Current_state='Ordered', date=date, is_deleted=False)

        # Organize data by delivery_option and date in descending order
        ordered_data = {}
        delivery_options = set()

        for data in queryset.order_by('-created_at'):
            delivery_option = data.delivery_option

            if delivery_option not in delivery_options:
                delivery_options.add(delivery_option)

        for option in delivery_options:
            delivery_option = option
            delivery_data = queryset.filter(delivery_option=delivery_option).order_by('id')

            if delivery_option not in ordered_data:
                ordered_data[delivery_option] = []

            for data in delivery_data:
                serializer = DeliveryHistorySerializer(data)
                delivery_details = tbldelivery_details.objects.filter(deliveryHistoryid=data.id, is_deleted=False)
                details_serializer = DeliveryDetailsSerializer_combine(
                    delivery_details, many=True, context={"branch": branch}
                )

                serialized_data = serializer.data
                serialized_data['delivery_details'] = details_serializer.data

                ordered_data[delivery_option].append(serialized_data)

        return Response(ordered_data)
        
class DeleteDeliveryHistory(APIView):
    def patch(self, request, delivery_id):
        try:
            delivery_history = tbldeliveryhistory.objects.get(pk=delivery_id)
            delivery_details = tbldelivery_details.objects.filter(deliveryHistoryid=delivery_id)
            
            if delivery_history.is_deleted == True:
                return Response({"error": "Delivery history is already deleted"}, status=status.HTTP_400_BAD_REQUEST)    
    
            # Soft delete: Set is_deleted to True
            delivery_history.is_deleted = True
            delivery_history.save()

            for detail in delivery_details:
                detail.is_deleted = True
                detail.save()

            return Response({"message": "Delivery history and details deleted successfully"}, status=status.HTTP_200_OK)


        except tbldeliveryhistory.DoesNotExist:
            return Response({"error": "Delivery history not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
