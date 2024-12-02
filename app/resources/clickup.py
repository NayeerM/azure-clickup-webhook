from flask import Blueprint, jsonify, request
from app.utils.throttler import Throttler
import requests
import config

clickup_bp = Blueprint('clickup', __name__)

throttler = Throttler(
        max_rate={'clickup': 1000, 'azure': 100},   # 1000 requests per minute
        window={'clickup': 60, 'azure': 60},       # 60 seconds window
        throttle_stop=False         # wait instead of stopping if limit is reached
    )

@clickup_bp.route('', methods=['POST'])
def handle_clickup_event():
    # Sample user data
    request_data = request.get_json()
    print(request_data)
    task_id = request_data.get('task_id')
    # switch case
    match request_data['event']:
        case 'taskCreated':
            create_azure_ticket(task_id)
        case _:
            return jsonify({'status': 'error', 'message': 'Invalid request type'}, 400)
    return jsonify({'status': 'success'})

def create_azure_ticket(task_id: str):
    """Create a task in Azure DevOps"""

    # Fetch task from ClickUp
    request = lambda: requests.get(f'{config.clickup_endpoint}task/{task_id}', headers=config.clickup_headers)
    response = throttler.request('clickup', request)
    if not response.ok:
        print(f'Failed to fetch ClickUp tasks: {response.status_code} - {response.content}')
        return None
    
    response = response.json()
    task_title = response.get('name', '')
    task_description = f"""
    <p>ClickUp Link: <a href="">{response.get('url', '')}</a></p>
    """
    # Update Field "Work Item ID" in ClickUp
    work_item_id = next((field['id'] for field in response["custom_fields"] if field['name'] == "Work Item ID"), None)

    if not work_item_id:
        print('Failed to find Work Item ID')
        return None

    data = [
        {"op": "add", "path": "/fields/System.Title", "value": f"{task_id}-{task_title}"},
        {"op": "add", "path": "/fields/System.Description", "value": task_description}
    ]

    # Create issue in Azure Devops Board
    request = lambda: requests.post(config.azure_endpoint, json=data, headers=config.azure_headers)
    response = throttler.request('azure', request)
    if not response.ok:
        print(f"Failed to create Azure DevOps issue: {response.status_code} - {response.content}")
        return None
    print(f"Successfully created Azure DevOps issue: {response.status_code} - {response.content}")
    
    
def update_clickup_custom_field(task_id, custom_field_id, value):
    """Update a custom field in a ClickUp task"""
    url = f'{config.clickup_endpoint}task/{task_id}/field/{custom_field_id}'
    payload = {'value': str(value)}
    request = lambda: requests.post(url, json=payload, headers=config.clickup_headers)
    response = throttler.request('clickup', request)
    if not response.ok:
        print(f'Failed to update ClickUp custom field: {response.status_code} - {response.content}')
    return None