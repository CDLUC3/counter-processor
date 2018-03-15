import config
import requests
from urllib.parse import urljoin
import io
#import ipdb; ipdb.set_trace()

class UploadException(Exception):
    pass

def send_to_datacite():
    my_url = urljoin(config.hub_base_url, 'reports')
    if config.output_format == 'json':
        ct = 'application/json; charset=UTF-8'
    else:
        ct = 'text/tab-separated-values; charset=UTF-8'
    headers = {'content-type': ct, 'Authorization': f'Bearer {config.hub_api_token}'}
    with io.open(f'{config.output_file}.{config.output_format}', 'r', encoding='utf-8') as myfile:
        data = myfile.read()

    # this is how you do a direct post of the information.
    # For a multipart encoded file, see http://docs.python-requests.org/en/master/user/quickstart/
    # It's not clear to me which way: as multi-part encoded file or as a direct POST of the json/tsv data
    response = requests.post(my_url, data=data.encode("utf-8"), headers=headers)
    print('')
    print('Sending report to the hub')
    print(f'Response was: {response}')
    if response.status_code != 201:
        raise UploadException("Expected to get 201 status code when posting the report to the hub")
