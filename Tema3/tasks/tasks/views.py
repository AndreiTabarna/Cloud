# tasks/views.py
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from google.cloud import storage, pubsub_v1, firestore
from google.oauth2 import service_account
from .models import Task
from .serializers import TaskSerializer

# Initialize Firestore client with service account credentials and specifying project ID and database ID
db = firestore.Client.from_service_account_json('key.json', project='emerald-folio-419810', database='cloudhw1')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # Remove the permission_classes attribute or set it to an empty list
    permission_classes = []

    def perform_create(self, serializer):
        task = serializer.save()

        # Check if the request time is before May 9, 2024
        if datetime.now() < datetime(2024, 5, 9):
            # Upload attachment to Cloud Storage
            if 'attachment' in self.request.FILES:
                file = self.request.FILES['attachment']
                storage_client = storage.Client(credentials=service_account.Credentials.from_service_account_file('key.json'))
                bucket = storage_client.bucket('my_first_bucket02')
                blob = bucket.blob('attachments/' + file.name)
                blob.upload_from_file(file.file, content_type=file.content_type)
                task.attachment_path = blob.public_url
                task.save()

            # Publish message to Cloud Pub/Sub for real-time updates
            publisher = pubsub_v1.PublisherClient(credentials=service_account.Credentials.from_service_account_file('key.json'))
            topic_path = publisher.topic_path('emerald-folio-419810', 'my_first_topic')
            data = {'action': 'create', 'task_id': task.id}
            message_future = publisher.publish(topic_path, data=str(data).encode('utf-8'))
            message_future.result()

            # Store data in Firestore
            task_data = serializer.data
            db.collection('tasks').document(str(task.id)).set(task_data)
        else:
            # If the request time is after May 9, 2024, deny the operation
            return Response({"error": "Operation not allowed after May 9, 2024"}, status=status.HTTP_403_FORBIDDEN)

    # Other methods perform_update and perform_destroy need similar modifications

