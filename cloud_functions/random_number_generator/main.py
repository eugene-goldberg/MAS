# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functions_framework
import random
import json
from datetime import datetime
from typing import Dict, Any

@functions_framework.http
def generate_random_number(request):
    """
    HTTP Cloud Function that generates random numbers.
    
    Args:
        request (flask.Request): The request object.
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
    """
    
    # Set CORS headers for the response
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    try:
        # Parse request parameters
        request_json = request.get_json(silent=True)
        request_args = request.args
        
        # Get parameters from either JSON body or query parameters
        min_value = 1
        max_value = 100
        count = 1
        decimal_places = 0
        
        if request_json:
            min_value = request_json.get('min', min_value)
            max_value = request_json.get('max', max_value)
            count = request_json.get('count', count)
            decimal_places = request_json.get('decimal_places', decimal_places)
        elif request_args:
            min_value = int(request_args.get('min', min_value))
            max_value = int(request_args.get('max', max_value))
            count = int(request_args.get('count', count))
            decimal_places = int(request_args.get('decimal_places', decimal_places))
        
        # Validate parameters
        if min_value >= max_value:
            return json.dumps({
                'error': 'min must be less than max',
                'status': 'error'
            }), 400, headers
        
        if count < 1 or count > 100:
            return json.dumps({
                'error': 'count must be between 1 and 100',
                'status': 'error'
            }), 400, headers
        
        if decimal_places < 0 or decimal_places > 10:
            return json.dumps({
                'error': 'decimal_places must be between 0 and 10',
                'status': 'error'
            }), 400, headers
        
        # Generate random numbers
        numbers = []
        for _ in range(count):
            if decimal_places == 0:
                # Generate integer
                number = random.randint(min_value, max_value)
            else:
                # Generate float with specified decimal places
                number = random.uniform(min_value, max_value)
                number = round(number, decimal_places)
            numbers.append(number)
        
        # Prepare response
        response_data = {
            'status': 'success',
            'numbers': numbers if count > 1 else numbers[0],
            'parameters': {
                'min': min_value,
                'max': max_value,
                'count': count,
                'decimal_places': decimal_places
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return json.dumps(response_data), 200, headers
        
    except Exception as e:
        error_response = {
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        return json.dumps(error_response), 500, headers


@functions_framework.http
def generate_random_choice(request):
    """
    HTTP Cloud Function that randomly selects from provided choices.
    
    Args:
        request (flask.Request): The request object.
        
    Returns:
        A random choice from the provided options.
    """
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or 'choices' not in request_json:
            return json.dumps({
                'error': 'choices array is required in request body',
                'status': 'error'
            }), 400, headers
        
        choices = request_json['choices']
        
        if not isinstance(choices, list) or len(choices) == 0:
            return json.dumps({
                'error': 'choices must be a non-empty array',
                'status': 'error'
            }), 400, headers
        
        # Make random choice
        selected = random.choice(choices)
        
        response_data = {
            'status': 'success',
            'selected': selected,
            'from_choices': choices,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return json.dumps(response_data), 200, headers
        
    except Exception as e:
        error_response = {
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        return json.dumps(error_response), 500, headers