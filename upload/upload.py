import config
import requests
from urllib.parse import urljoin
import io
#import ipdb; ipdb.set_trace()

class UploadException(Exception):
    pass

def send_to_datacite():
    if config.output_format == 'json':
        ct = 'application/json; charset=UTF-8'
    else:
        ct = 'text/tab-separated-values; charset=UTF-8'
    headers = {'content-type': ct, 'Authorization': f'Bearer {config.hub_api_token}'}
    with io.open(f'{config.output_file}.{config.output_format}', 'r', encoding='utf-8') as myfile:
        data = myfile.read()

    # this is how you do a direct post of the information.

    # my_url = urljoin(config.hub_base_url, 'reports')
    # response = requests.post(my_url, data=data.encode("utf-8"), headers=headers)

    #  this is the bad one -- my_url = urljoin(config.hub_base_url, 'reports/2018-04-CDL')
    # my_url = urljoin(config.hub_base_url, 'reports/2018-4-Dash')
    # response = requests.put(my_url, data=data.encode("utf-8"), headers=headers)

    file = open("tmp/datacite_response_body.txt","w")
    file.write(f'{str(response.status_code)}\n')
    file.write(f'{response.headers}\n')
    # this errors, not sure why -- file.write(f'{(response.headers['content-type'])}\n')
    file.write(response.text)
    file.close()


    import ipdb; ipdb.set_trace()
    print('')
    print('Sending report to the hub')
    print(f'Response was: {response}')
    if response.status_code != 201:
        raise UploadException("Expected to get 201 status code when posting the report to the hub")
