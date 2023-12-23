import base64
import email

def get_messages(service, user_id, query):
  try:
    return service.users().messages().list(userId=user_id, q=query).execute()
  except Exception as error:
    print('An error occurred: %s' % error)

def get_message(service, user_id, msg_id):
  try:
    return service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
  except Exception as error:
    print('An error occurred: %s' % error)

def get_mime_message(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()
    print('Message snippet: %s' % message['snippet'])
    msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
    mime_msg = email.message_from_string(msg_str)
    return mime_msg
  except Exception as error:
    print('An error occurred: %s' % error)
