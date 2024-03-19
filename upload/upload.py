import config
import requests
from urllib.parse import urljoin
import io
import json
from urllib.request import pathname2url
import sys
import time
import gzip
#import ipdb; ipdb.set_trace()

class UploadException(Exception):
    pass

# save response to a file so can look at it if needed
def save_response(response):
    file = open("tmp/datacite_response_body.txt","w")
    file.write(f'{str(response.status_code)}\n')
    file.write(f'{response.headers}\n')
    file.write(f'{(response.headers["content-type"])}\n')
    file.write(response.text)
    # parsed = json.loads(response.text)
    # file.write(json.dumps(parsed, indent=2, sort_keys=True))
    file.close()

# this method is a retry since the datacite api randomly gives many 500 errors
def retry_if_500(method, url, data, headers):
    for attempt in range(60):
        response = getattr(requests, method)(url, data=gzip.compress(data.encode()), headers=headers)
        if response.status_code < 500 or attempt == 59:
            return response
        else:
            print(f'expected to upload, but got code {response.status_code}')
            time.sleep(1)

def send_to_datacite():
    # removing TSV output from upload since it has never been implemented in servers and just clutters code
    # if needed, can find it in the github history.

    # changing content-type to gzip since it is safest for large files and it fails without compression in many cases
    headers = {
        'Content-Type': 'application/gzip',
        'Content-Encoding': 'gzip',
        'Accept': 'application/json',
        'Authorization': f'Bearer {config.Config().hub_api_token}'
    }

    with io.open(f'{config.Config().output_file}.json', 'r', encoding='utf-8') as myfile:
        data = myfile.read()

    # post or put the information
    #
    # Note: the submitting report API has been expanded to return more status codes, according to https://github.com/datacite/sashimi/pull/129
    # The new set of codes are:
    # 200	Report has been updated
    # 201	Report has been CREATED and validated correctly
    # 202	Report has been ACCEPTED and its waiting for validation
    # 404	Report does not exist
    # 422	Report or sub-report has failed validation

    # The validation here is still OK (200-299 is considered OK), retry on 500 errors, others codes log errors for examination.
    # The new 200-level codes will mostly be useful for monitoring DataCite status or re-checking previous submissions which
    # this class doesn't really do and would likely happen in a separate monitoring process since the other 200 codes happen
    # asynchronously to be checked after submission time.

    my_id = config.Config().current_id()
    if my_id is None:
        my_url = urljoin(config.Config().hub_base_url, 'reports')
        # response = requests.post(my_url, data=data.encode("utf-8"), headers=headers)
        response = retry_if_500(method='post', url=my_url, data=data, headers=headers)
        save_response(response)
        json_data = json.loads(response.text)
        if 'report' in json_data:
            config.Config().write_id(json_data['report']['id'])
    else:
        my_url = urljoin(config.Config().hub_base_url, f'reports/{pathname2url(my_id)}')
        # response = requests.put(my_url, data=data.encode("utf-8"), headers=headers)
        response = retry_if_500(method='put', url=my_url, data=data, headers=headers)
        save_response(response)

    if response.status_code < 200 or response.status_code > 299:
        # raise UploadException("Expected to get 200 range status code when sending the report to the hub. Check tmp/datacite_response_body.txt for response.")
        print("Expected to get 200 range status code when sending the report to the hub. Check tmp/datacite_response_body.txt for response.")
        sys.exit(1)
    else:
        print('submitted')
