import requests
from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_USER = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VIRTUAL_HOST')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')

class Rabbit:

  def __init__(self):
    self.auth = (RABBITMQ_USER, RABBITMQ_PASSWORD)
    self.vhost = None
  
  def get_queue_url(self, queue_name: str) -> str:
    queue_url = f"{RABBITMQ_HOST}{RABBITMQ_VHOST}"
    if self.vhost is not None:
      queue_url = f"{RABBITMQ_HOST}{self.vhost}"
    if queue_name is not None:
      queue_url = f"{queue_url}/{queue_name}"
    return queue_url

  def get_queue_estatus(self, queue_name: str=None, without_messages: bool = False, vhost:str = None) -> list:
    self.vhost = vhost
    queue_url = self.get_queue_url(queue_name)

    print(queue_url)
    response = requests.get(queue_url, auth=self.auth)
    queues = []
    if response.status_code == 200:
      queues_data = response.json()
      if not isinstance(queues_data, list):
        queues_data = [queues_data]

      for queue in queues_data:
        queues.append(
          {
            'queue_name': queue['name'],
            'messages_count':  queue['messages']
          }
        )
        print(without_messages, queue_name)
        if not without_messages and queue_name is None:
          print(f"Getting messages from queue: {queue_name}")
          queues = list(filter(lambda x: x['messages_count'] > 0, queues))
      return queues
    else:
      print(f"Error: {response.status_code} - {response.text}")
      return None

  def get_queue_messages(self, queue_name: str, limit: int = 10, vhost: str = None) -> list:
    self.vhost = vhost
    params = {'count': limit, 'ackmode': 'ack_requeue_true', 'encoding': 'auto'}
    queue_url = f"{self.get_queue_url(queue_name)}/get"
    response = requests.post(queue_url, auth=self.auth, json=params)

    messages = []
    if response.status_code == 200:
      messages_data = response.json()
      for message in messages_data:
        message_body = message['payload']
        messages.append(message_body)
      return messages
    else:
      print(f"Error: {response.status_code} - {response.text}")
      return None
