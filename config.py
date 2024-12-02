import base64
import os

clickup_api_key = os.environ.get('CLICKUP_API_KEY')
clickup_list_id = os.environ.get('CLICKUP_LIST_ID')
azure_organization = os.environ.get('AZURE_ORGANIZATION')
azure_project = os.environ.get('AZURE_PROJECT')
azure_personal_access_token = os.environ.get('AZURE_PERSONAL_ACCESS_TOKEN')
azure_personal_access_token_encoded = base64.b64encode(f':{azure_personal_access_token}'.encode()).decode()
azure_endpoint = f'https://dev.azure.com/{azure_organization}/{azure_project}/_apis/wit/workitems/$Issue?api-version=6.0'
clickup_endpoint = 'https://api.clickup.com/api/v2/'

# Headers for API Requests
azure_headers = {
    'Authorization': f'Basic {azure_personal_access_token_encoded}',
    'Content-Type': 'application/json-patch+json'
}

clickup_headers = {
    'Authorization': clickup_api_key,
    'Content-Type': 'application/json'
}