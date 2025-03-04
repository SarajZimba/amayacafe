from rest_framework import serializers

class ChatbotInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)  # Assuming the message will be a string with a max length of 500 characters
    thread_id = serializers.CharField(max_length=100)