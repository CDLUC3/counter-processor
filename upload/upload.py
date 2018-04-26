import config
import requests
from urllib.parse import urljoin
import io
import json
from urllib.request import pathname2url
#import ipdb; ipdb.set_trace()

class UploadException(Exception):
    pass

# save response to a file so can look at it if needed
def save_response(response):
    file = open("tmp/datacite_response_body.txt","w")
    file.write(f'{str(response.status_code)}\n')
    file.write(f'{response.headers}\n')
    file.write(f'{(response.headers["content-type"])}\n')
    parsed = json.loads(response.text)
    file.write(json.dumps(parsed, indent=4, sort_keys=True))
    file.close()

def send_to_datacite():
    if config.output_format == 'json':
        ct = 'application/json; charset=UTF-8'
    else:
        ct = 'text/tab-separated-values; charset=UTF-8'
    headers = {'content-type': ct, 'Authorization': f'Bearer {config.hub_api_token}'}

    # TODO: if we need to test, use this below because still not accepting grids
    # with io.open('good_test.json', 'r', encoding='utf-8') as myfile:
    #    data = myfile.read()


    with io.open(f'{config.output_file}.{config.output_format}', 'r', encoding='utf-8') as myfile:
        data = myfile.read()

    # post or put the information
    my_id = config.current_id()
    if my_id is None:
        my_url = urljoin(config.hub_base_url, 'reports')
        response = requests.post(my_url, data=data.encode("utf-8"), headers=headers)
        import ipdb; ipdb.set_trace()
        json_data = json.loads(response.text)
        config.write_id(json_data['report']['id'])
    else:
        my_url = urljoin(config.hub_base_url, f'reports/{pathname2url(my_id)}')
        response = requests.put(my_url, data=data.encode("utf-8"), headers=headers)

    save_response(response)

    if response.status_code < 200 or response.status_code > 299:
        raise UploadException("Expected to get 200 range status code when sending the report to the hub")

    print('submitted')
