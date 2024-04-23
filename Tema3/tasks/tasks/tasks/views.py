import gspread
from oauth2client.service_account import ServiceAccountCredentials
from rest_framework import viewsets, status
from rest_framework.response import Response
from google.cloud import storage
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # Remove the permission_classes attribute or set it to an empty list
    permission_classes = []

    def perform_create(self, serializer):
        task = serializer.save()

        # Upload attachment to Cloud Storage
        if 'attachment' in self.request.FILES:
            file = self.request.FILES['attachment']
            storage_client = storage.Client(credentials=service_account.Credentials.from_service_account_file('key.json'))
            bucket = storage_client.bucket('my_first_bucket02')
            blob = bucket.blob('attachments/' + file.name)
        
            with file.file.open('rb') as f:
                blob.upload_from_file(f, content_type=file.content_type)
        
            # Set attachment_path to the public URL of the uploaded file
            task.attachment_path = blob.public_url
            task.save()  # Save the task object after updating attachment_path

        # Publish message to Cloud Pub/Sub for real-time updates
        publisher = pubsub_v1.PublisherClient(credentials=service_account.Credentials.from_service_account_file('key.json'))
        topic_path = publisher.topic_path('emerald-folio-419810', 'my_first_topic')
        data = {'action': 'create', 'task_id': task.id}
        message_future = publisher.publish(topic_path, data=str(data).encode('utf-8'))
        message_future.result()

        # Add task to Google Sheet
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(credentials)
        sheet = client.open('CloudHW').sheet1
        sheet.append_row([task.id, task.title, task.description, task.due_date]) 


    def perform_update(self, serializer):
        task = serializer.save()

        # Publish message to Cloud Pub/Sub for real-time updates
        publisher = pubsub_v1.PublisherClient(credentials=service_account.Credentials.from_service_account_file('key.json'))
        topic_path = publisher.topic_path('emerald-folio-419810', 'my_first_topic')
        data = {'action': 'update', 'task_id': task.id}
        message_future = publisher.publish(topic_path, data=str(data).encode('utf-8'))
        message_future.result()

    def perform_destroy(self, instance):
        # Delete the task instance
        instance.delete()
        # Publish message to Cloud Pub/Sub for real-time updates
        publisher = pubsub_v1.PublisherClient(credentials=service_account.Credentials.from_service_account_file('key.json'))
        topic_path = publisher.topic_path('emerald-folio-419810', 'my_first_topic')
        data = {'action': 'delete', 'task_id': instance.id}
        message_future = publisher.publish(topic_path, data=str(data).encode('utf-8'))
        message_future.result()
        return Response(status=status.HTTP_204_NO_CONTENT)

