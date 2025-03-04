# from django.shortcuts import render
# from pathlib import Path
# import os
# import environ
# from datetime import timedelta
# BASE_DIR = Path(__file__).resolve().parent.parent
# env = environ.Env(DEBUG=(bool, False))
# environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# # Create your views here.
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import ChatbotInputSerializer
# from openai import OpenAI
# import time
# import json
# from product.models import Product
# from rest_framework.permissions import AllowAny 
# from bill.models import tbldelivery_details, tbldeliveryhistory
# from product.models import Product
# from django.db import transaction
# from user.models import Customer
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Q

# client = OpenAI()



# class ChatbotView(APIView):

#     authentication_classes = []
    
#     # Set permission classes to AllowAny
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):

#         # def create_thread():
#         #     return client.beta.threads.create()
#         @transaction.atomic
#         def order(name, address, phone_no, email, itemlist):
#             try:

#                 try:
#                     customer = Customer.objects.get(Q(contact_number=phone_no) | Q(email=email))
#                 except ObjectDoesNotExist:
#                     customer = Customer.objects.create(name=name, address=address, contact_number=phone_no, email=email)
#                 delivery = tbldeliveryhistory.objects.create(customer=customer)
#                 for order_item in itemlist:
#                     product_id = int(order_item['productId'])
#                     product = Product.objects.get(id = product_id)
#                     quantity = order_item['quantity']
#                     delivery_details = tbldelivery_details.objects.create(deliveryHistoryid = delivery, product = product, quantity=quantity)
                    
#                 return "Delivery added successfully"

#             except Exception as e:
#                 # If any exception occurs, rollback the transaction

#                 transaction.set_rollback(True)

#                 client.beta.threads.runs.cancel(
#                     thread_id=empty_thread,
#                     run_id=run.id
#                     )  
#                 return Response({"error": "Condition Failed"},status=status.HTTP_400_BAD_REQUEST)

        
#         def add_message_to_thread(thread_id, role, message):
#             return client.beta.threads.messages.create(
#             thread_id,
#             role=role,
#             content=message,
#             )
        
#         def run_assistant(thread_id, assistant_id):
#             return client.beta.threads.runs.create(thread_id= empty_thread, assistant_id = assistant_id)

#         def give_products():
#             productss = Product.objects.active().filter(is_billing_item=True)

#             products = []
#             for product in productss:
#                 product_in = {
#                     "id" : product.id, 
#                     "title" : product.title, 
#                     "price" : product.price,
#                     "group" : product.group
#                 }
#                 products.append(product_in)

#             # products_json_str = json.dumps(products)
#             products_json_str = str(products)
            
#             # # Escape newline characters if necessary
#             # products_json_str = products_json_str.replace('\n', '')

#             return products_json_str

#         def run_steps():
#             run_steps = client.beta.threads.runs.steps.list(
#                 thread_id=empty_thread,
#                 run_id=run.id
#             )
#             # print(run_steps)
#             return run_steps
        
#         def get_run_status():
#             run_status = client.beta.threads.runs.retrieve(
#                 thread_id=empty_thread,
#                 run_id=run.id
#             )
            
#             return run_status
        

#         def handle_run_and_check(thread_messages):
#             # print("from handle_and_check",thread_messages)
#             # data = thread_messages.data[0].content[0].text.value
#             # data = thread_messages.data
#             datas = thread_messages.data
#             to_send_data = []

#             for data in datas:

#                 for content in data.content:
#                     message = {
#                         "role" : data.role,
#                         "value": content.text.value
#                     }
                
#                     to_send_data.append(message)

#             to_send_data.reverse()
#             return Response({"response": to_send_data}, status=status.HTTP_200_OK) 

#         serializer = ChatbotInputSerializer(data=request.data)

#         # def requires_action():
#         #     check=True
#         #     get_run_step  = run_steps()
#         #     # print(get_run_step)
#         #     # print(run)
#         #     if get_run_step.data != []:
#         #         for data in get_run_step.data:
#         #             # print(f"tool_calls {data}")
#         #             for tool in data.step_details.tool_calls:
#         #                 if tool['function']['name'] == "give_products":
#         #                     tool_id = tool['id']
#         #                     output = give_products()
#         #                 elif tool['function']['name'] == "order":
#         #                     tool_id = tool['id']
#         #                     arguments = tool['function']['arguments']
#         #                     arguments_dict = json.loads(arguments)

#         #                     # Access individual fields
#         #                     # id = arguments_dict['id']
#         #                     # title = arguments_dict['title']
#         #                     # price = arguments_dict['price']
#         #                     name = arguments_dict['name']
#         #                     address = arguments_dict['address']
#         #                     phone = arguments_dict['phonenumber']
#         #                     itemlist = arguments_dict['itemlist']


#         #                     output = order(name, address, phone,  itemlist)
     

#         #                 # else:
#         #                 #     pass

#         #                 # print(output)

#         #                 run_requires = client.beta.threads.runs.submit_tool_outputs(
#         #                 thread_id=empty_thread,
#         #                 run_id=run.id,
                                            
#         #                 tool_outputs=[
#         #                     {
#         #                         "tool_call_id":tool_id,
#         #                         "output": output
#         #                     }
#         #                 ]
#         #                 )
#         #                 while True:
#         #                     inside_condition = get_run_status()
#         #                     if inside_condition.status == "requires_action":
#         #                         requires_action()

#         #                     if inside_condition.status == "completed":
#         #                         thread_messages = client.beta.threads.messages.list(empty_thread)
                                               
#         #                         break

#         #                     time.sleep(2)

#         if serializer.is_valid():
#             message = serializer.validated_data['message']
            
#             # Here, you can process the message or return a response.
#             # For now, let's just echo back the received message.


#             empty_thread = serializer.validated_data['thread_id']

#             thread_message = add_message_to_thread(empty_thread,"user",message)
#             run = run_assistant(empty_thread, env('ASSISTANT_ID'))
#             print(run)
#             # print(run)
#             # run = client.beta.threads.runs.create(thread_id= empty_thread, assistant_id = env('ASSISTANT_ID'))
          
#             def run_and_check():
#                 check = False
#                 while (check != True):
#                     condition = get_run_status()
#                     print(condition)


#                     if condition.status == "completed":
#                         check=True
#                         thread_messages = client.beta.threads.messages.list(empty_thread)

#                         break  # Exit the loop if status is True
#                     time.sleep(2)

#                     if condition.status == "requires_action":
#                             # check=True
#                             get_run_step  = run_steps()
#                             # print(get_run_step)
#                             # print(run)
#                             if get_run_step.data != []:
#                                 for data in get_run_step.data:
#                                     # print(f"tool_calls {data}")
#                                     if data.status == "in_progress":
#                                         for tool in data.step_details.tool_calls:
#                                             if tool['function']['name'] == "give_products":
#                                                 tool_id = tool['id']
#                                                 output = give_products()
#                                             elif tool['function']['name'] == "order":
#                                                 tool_id = tool['id']
#                                                 arguments = tool['function']['arguments']
#                                                 arguments_dict = json.loads(arguments)

#                                                 # Access individual fields
#                                                 # id = arguments_dict['id']
#                                                 # title = arguments_dict['title']
#                                                 # price = arguments_dict['price']
#                                                 name = arguments_dict['name']
#                                                 address = arguments_dict['address']
#                                                 phone = arguments_dict['phonenumber']
#                                                 email = arguments_dict['email']
#                                                 itemlist = arguments_dict['itemlist']


#                                                 output = order(name, address, phone, email,  itemlist)
        

#                                             # else:
#                                             #     pass

#                                             # print(output)

#                                             run_requires = client.beta.threads.runs.submit_tool_outputs(
#                                             thread_id=empty_thread,
#                                             run_id=run.id,
                                                
#                                             tool_outputs=[
#                                                 {
#                                                     "tool_call_id":tool_id,
#                                                     "output": output
#                                                 }
#                                             ]
#                                             )
#                                         # while True:
#                                         #     inside_condition = get_run_status()
#                                         #     if inside_condition.status == "completed":
#                                         #         thread_messages = client.beta.threads.messages.list(empty_thread)
                                               
#                                         #         break
#                                         #     time.sleep(2)



                    
#                     time.sleep(2)

#                     if condition.status == "failed" or condition.status == "cancelled" or condition.status == "expired":
#                         break
#                 if check == True:
#                     # print("Status is True. Exiting loop.")

#                     return handle_run_and_check(thread_messages)   
#                 else:
#                     # client.beta.threads.runs.cancel(
#                     # thread_id=empty_thread,
#                     # run_id=run.id
#                     # )
                    
#                     return Response({"error" : "Condition Failed"}, status=status.HTTP_400_BAD_REQUEST)                         

#             run_condition = run_and_check()

#             return run_condition
        

# class ChatbotSameThreadView(APIView):
#     authentication_classes = []
    
#     # Set permission classes to AllowAny
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):

#         def create_thread():
#             return client.beta.threads.create()
#         empty_thread = create_thread()
#         return Response({"response": empty_thread.id}, status.HTTP_200_OK)
            

# new code

from django.shortcuts import render
from pathlib import Path
import os
import environ
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatbotInputSerializer
from openai import OpenAI
import time
import json
from product.models import Product
from rest_framework.permissions import AllowAny 
from bill.models import tbldelivery_details, tbldeliveryhistory
from product.models import Product
from django.db import transaction
from user.models import Customer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from product.models import BranchStock
from django.db.models import OuterRef, Subquery, Sum
from organization.models import Branch
client = OpenAI()



class ChatbotView(APIView):

    authentication_classes = []
    
    # Set permission classes to AllowAny
    permission_classes = [AllowAny]

    def functionality(self, empty_thread, message):

        def add_message_to_thread(thread_id, role, message):
            return client.beta.threads.messages.create(
            thread_id,
            role=role,
            content=message,
            )
        

        def run_assistant(thread_id, assistant_id):
            return client.beta.threads.runs.create(thread_id= empty_thread, assistant_id = assistant_id)

        thread_message = add_message_to_thread(empty_thread,"user",message)
        run = run_assistant(empty_thread, env('ASSISTANT_ID'))

        @transaction.atomic
        def order(name, address, phone_no, email, itemlist):
            try:

                try:
                    customer = Customer.objects.get(Q(contact_number=phone_no) | Q(email=email))
                except ObjectDoesNotExist:
                    customer = Customer.objects.create(name=name, address=address, contact_number=phone_no, email=email)
                delivery = tbldeliveryhistory.objects.create(customer=customer)
                for order_item in itemlist:
                    product_id = int(order_item['productId'])
                    product = Product.objects.get(id = product_id)
                    quantity = order_item['quantity']
                    delivery_details = tbldelivery_details.objects.create(deliveryHistoryid = delivery, product = product, quantity=quantity)
                    
                return "Delivery added successfully"

            except Exception as e:
                # If any exception occurs, rollback the transaction

                transaction.set_rollback(True)

                client.beta.threads.runs.cancel(
                    thread_id=empty_thread,
                    run_id=run.id
                    )  
                return Response({"error": "Condition Failed"},status=status.HTTP_400_BAD_REQUEST)

        def give_products():
            branch = Branch.objects.first()
            print(branch)
            branchstock_quantity_subquery_all = BranchStock.objects.filter(
                product=OuterRef('pk'),
                branch=branch
            ).values('product').annotate(total_quantity=Sum('quantity')).values('total_quantity')[:1]

            all_products = Product.objects.annotate(branchstock_total_quantity=Subquery(branchstock_quantity_subquery_all)).filter(
                is_deleted = False,
                branchstock_total_quantity__gt=0
            )

            products = []
            for product in all_products:
                product_in = {
                    "id" : product.id, 
                    "title" : product.title, 
                    "price" : product.price,
                    "group" : product.group
                }
                products.append(product_in)
            products_json_str = str(products)
            

            return products_json_str

        def run_steps():
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=empty_thread,
                run_id=run.id
            )
            # print(run_steps)
            return run_steps
        
        def get_run_status():
            run_status = client.beta.threads.runs.retrieve(
                thread_id=empty_thread,
                run_id=run.id
            )
            
            return run_status
        

        def handle_run_and_check(thread_messages):
            # print("from handle_and_check",thread_messages)
            # data = thread_messages.data[0].content[0].text.value
            # data = thread_messages.data
            datas = thread_messages.data
            to_send_data = []

            for data in datas:

                for content in data.content:
                    message = {
                        "role" : data.role,
                        "value": content.text.value
                    }
                
                    to_send_data.append(message)

            to_send_data.reverse()
            return Response({"response": to_send_data}, status=status.HTTP_200_OK) 
        
        def run_and_check():
                check = False
                while (check != True):
                    condition = get_run_status()
                    print(condition)


                    if condition.status == "completed":
                        check=True
                        thread_messages = client.beta.threads.messages.list(empty_thread)

                        break  # Exit the loop if status is True
                    time.sleep(2)

                    if condition.status == "requires_action":
                            # check=True
                            get_run_step  = run_steps()
                            # print(get_run_step)
                            # print(run)
                            if get_run_step.data != []:
                                for data in get_run_step.data:
                                    # print(f"tool_calls {data}")
                                    if data.status == "in_progress":
                                        for tool in data.step_details.tool_calls:
                                            if tool['function']['name'] == "give_products":
                                                tool_id = tool['id']
                                                output = give_products()
                                            elif tool['function']['name'] == "order":
                                                tool_id = tool['id']
                                                arguments = tool['function']['arguments']
                                                arguments_dict = json.loads(arguments)

                                                # Access individual fields
                                                # id = arguments_dict['id']
                                                # title = arguments_dict['title']
                                                # price = arguments_dict['price']
                                                name = arguments_dict['name']
                                                address = arguments_dict['address']
                                                phone = arguments_dict['phonenumber']
                                                email = arguments_dict['email']
                                                itemlist = arguments_dict['itemlist']


                                                output = order(name, address, phone, email,  itemlist)
        

                                            # else:
                                            #     pass

                                            # print(output)

                                            run_requires = client.beta.threads.runs.submit_tool_outputs(
                                            thread_id=empty_thread,
                                            run_id=run.id,
                                                
                                            tool_outputs=[
                                                {
                                                    "tool_call_id":tool_id,
                                                    "output": output
                                                }
                                            ]
                                            )
                                        # while True:
                                        #     inside_condition = get_run_status()
                                        #     if inside_condition.status == "completed":
                                        #         thread_messages = client.beta.threads.messages.list(empty_thread)
                                               
                                        #         break
                                        #     time.sleep(2)



                    
                    time.sleep(2)

                    if condition.status == "failed" or condition.status == "cancelled" or condition.status == "expired":
                        break
                if check == True:
                    # print("Status is True. Exiting loop.")

                    return handle_run_and_check(thread_messages)   
                else:
                    # client.beta.threads.runs.cancel(
                    # thread_id=empty_thread,
                    # run_id=run.id
                    # )
                    
                    return Response({"error" : "Condition Failed"}, status=status.HTTP_400_BAD_REQUEST)                         

        run_condition = run_and_check()

        return run_condition



    def post(self, request, *args, **kwargs):

        serializer = ChatbotInputSerializer(data=request.data)

        if serializer.is_valid():
            message = serializer.validated_data['message']
            empty_thread = serializer.validated_data['thread_id']
            

            return self.functionality(empty_thread, message)
        

class ChatbotSameThreadView(ChatbotView):
    authentication_classes = []
    
    # Set permission classes to AllowAny
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        def create_thread():
            return client.beta.threads.create()
        empty_thread = create_thread()
        return Response({"response": empty_thread.id}, status.HTTP_200_OK)
            
        
    


        
    


        
    


    


        
    


        
    

