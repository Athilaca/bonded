import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import CustomUser, Message
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        
        # Get the user_id from the URL (passed from the routing)
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']

        # Create a group name for the user, you can customize this
        self.room_name = f'chat_{self.receiver_id}'  # Unique group name for each user
        self.room_group_name = f'chat_{self.room_name}'

        # Join the WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json.get('sender_id')
        receiver_id = self.receiver_id

        try:
            
            
           

            # Send the message to WebSocket group
            await self.channel_layer.group_send(
                self.room_group_name,  # Send to the specific user's group
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender':sender_id,
                    'receiver':receiver_id
                }
            )

        except Exception as e:
            # Log the error
            logger.error(f"Error while processing the message: {e}")
            await self.send(text_data=json.dumps({'error': 'Error while processing the message.'}))

    async def chat_message(self, event):
        # Extract the message from the event
        message = event['message']
        sender_id = event['sender']
        receiver_id = event['receiver']

        try:
            # Fetch sender and receiver users from the database
            sender = await self.get_sender_user(sender_id)
            receiver = await self.get_receiver_user(receiver_id)

            # Save the message to the database
            new_message = await self.save_message(sender, receiver, message)

            # Log the saved message
            logger.info(f"Message saved from {sender.username} to {receiver.username}: {message}")

        except Exception as e:
            logger.error(f"Error saving message during broadcast: {e}")

        # Send the message to WebSocket (this sends to the connected user)
        await self.send(text_data=json.dumps({
            'message': message,
        }))
        

    # Fetch the sender user from the CustomUser model
    async def get_sender_user(self, sender_id):
        try:
            sender = await sync_to_async(CustomUser.objects.get)(id=sender_id)
            logger.debug(f"Sender found: {sender}")
            return sender
        except CustomUser.DoesNotExist:
            logger.error(f"Sender with ID {sender_id} not found")
            raise ValueError(f"Sender with ID {sender_id} not found")

    # Fetch the receiver user from the CustomUser model
    async def get_receiver_user(self, receiver_id):
        try:
            receiver = await sync_to_async(CustomUser.objects.get)(id=receiver_id)
            logger.debug(f"Receiver found: {receiver}")
            return receiver
        except CustomUser.DoesNotExist:
            logger.error(f"Receiver with ID {receiver_id} not found")
            raise ValueError(f"Receiver with ID {receiver_id} not found")

    # Save the message to the database
    async def save_message(self, sender, receiver, message):
        try:
            timestamp = timezone.now()
            # Create a new message instance and save it to the database
            new_message = await sync_to_async(Message.objects.create)(
                sender=sender,
                receiver=receiver,
                content=message,
                status='sent',
                created_at=timestamp, 
            )
            logger.debug(f"Message saved: {new_message}")
            return new_message
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise ValueError(f"Error saving message: {e}")


