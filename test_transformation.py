from services.firestore_service import firestore_service

print('Testing conversion function')

# Create test data with preparation as a list (explicitly using a list)
test_data = {
    'days': [
        {
            'breakfast': {
                'dishes': [
                    {
                        'name': 'Test Dish',
                        'preparation': ['Step 1', 'Step 2']  # This is a list of strings
                    }
                ]
            }
        }
    ]
}

# Print original type before transformation
print('Original preparation type (before):', type(test_data['days'][0]['breakfast']['dishes'][0]['preparation']))
print('Original preparation value (before):', test_data['days'][0]['breakfast']['dishes'][0]['preparation'])

# Transform the data
result = firestore_service._transform_meal_plan_data(test_data)

# Check the result
print('Transformed preparation type:', type(result['days'][0]['breakfast']['dishes'][0]['preparation']))
print('Transformed preparation value:', result['days'][0]['breakfast']['dishes'][0]['preparation'])

# Now test with a string input to make sure it stays a string
test_data2 = {
    'days': [
        {
            'breakfast': {
                'dishes': [
                    {
                        'name': 'Test Dish 2',
                        'preparation': 'Already a string'  # This is already a string
                    }
                ]
            }
        }
    ]
}

# Transform the second test data
result2 = firestore_service._transform_meal_plan_data(test_data2)

# Check the second result
print('\nTest with string input:')
print('Original preparation type (string):', type(test_data2['days'][0]['breakfast']['dishes'][0]['preparation']))
print('Original preparation value (string):', test_data2['days'][0]['breakfast']['dishes'][0]['preparation'])
print('Transformed preparation type (string):', type(result2['days'][0]['breakfast']['dishes'][0]['preparation']))
print('Transformed preparation value (string):', result2['days'][0]['breakfast']['dishes'][0]['preparation']) 