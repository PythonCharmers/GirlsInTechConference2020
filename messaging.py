"""
Tools for working with the Telstra Messaging API

To use it, sign up for a free API key from https://dev.telstra.com
and enter your client key and client secret here:
"""

client_key = '...'    # enter your API client key here
client_secret = '...' # enter your API client secret here


class UsageError(Exception):
    """
    Usage help
    """

usage_help = """The Telstra API did not return an access token.

To send messages, sign up for an API key first at https://dev.telstra.com and
add your client_key and client_secret at the top of messaging.py."""

# For Ed's live talk: look up Ed's saved credentials:
if client_key == '...':
    try:
        import keyring
        from getpass import getuser
        client_key = keyring.get_password('telstra_messaging_api_key', getuser())
        client_secret = keyring.get_password('telstra_messaging_api_secret', getuser())
    except:
        raise UsageError(usage_help)


import base64
import getpass

import requests
import IPython
import filetype


user = getpass.getuser()


def sms(phone_number, message):
    """
    Send an SMS with the given message to the given phone number.

    Pass phone_number as a string with the country code, like '+61412345678'
    """
    token = auth()
    provision(token)
    send_sms(phone_number, message, token)


def auth(proxies={}):
    """
    Authenticate with the Telstra Messaging API.

    Return a valid oAuth token.
    """

    params = {'client_id': client_key,
              'client_secret': client_secret,
              'grant_type': 'client_credentials'}

    auth_url = 'https://tapi.telstra.com/v2/oauth/token'

    auth_response = requests.post(auth_url, params, proxies=proxies)

    try:
        token = auth_response.json()['access_token']
    except KeyError:
        raise UsageError(usage_help)
    return token


def provision(token, proxies={}):
    """
    Provision a phone number with the Telstra Messaging API
    """
    provision_url = 'https://tapi.telstra.com/v2/messages/provisioning/subscriptions'

    headers = {'authorization': f'Bearer {token}'}
    params = {}
    provision_response = requests.post(provision_url, headers=headers, json=params, proxies=proxies)
    result = provision_response.json()
    return result


def send_sms(phone_number, message, token, proxies={}):
    sms_url = 'https://tapi.telstra.com/v2/messages/sms'
    headers = {'authorization': f'Bearer {token}'}
    params = {'to': phone_number,
              'body': message}
    requests.post(sms_url, headers=headers, json=params, proxies=proxies)


def send_mms(phone_number: str, image_bytes: bytes, subject: str, token: str, mimetype: str = 'image/jpeg', filename: str = 'image.jpg', proxies: dict = {}):
    """Send an MMS with the given image.
    """
    image_encoded = base64.b64encode(image_bytes).decode()
    mms_url = 'https://tapi.telstra.com/v2/messages/mms'
    headers = {'authorization': f'Bearer {token}'}
    params = {'to': phone_number,
              'MMSContent': [{'type': mimetype,
                             'filename': filename,
                             'payload': image_encoded}]
             }
    if subject:
        params['subject'] = subject
    response = requests.post(mms_url, headers=headers, json=params, proxies=proxies)
    return response.text


def mms(phone_number: str, image, subject=None):
    """
    Simple wrapper: Send an MMS of the given image.

    Parameters
    ----------
    image: an IPython.core.display.Image object or a byte-string

    We infer the MIME type and usual extension using the `filetype` package.
    """
    if isinstance(image, IPython.core.display.Image):
        image_data = image.data
    elif isinstance(image, bytes):
        image_data = image

    kind = filetype.guess(image_data)
    mimetype = kind.mime
    extension = kind.extension

    token = auth()
    provision(token)
    send_mms(phone_number, image_data, subject, token, mimetype=mimetype, filename=f'image.{extension}')
