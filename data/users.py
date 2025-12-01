from models import User, Role
from pydantic import ValidationError

raw_users = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "role": "admin"
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "age": 25,
        "role": "user"
    },
    {
        "id": 3,
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "age": 35,
        "role": "user"
    },
    {
        "id": 4,
        "name": "Alice Brown",
        "email": "alice.brown@example.com",
        "age": 28,
        "role": "moderator"
    },
    {   "id": -5,
        "name": "Charlie Davis",
        "email": "",
        "age": 22,
        "role": "winner"
    }
]

valid_users = []
for raw_user in raw_users:
    try:
        # This converts the dict into a User object
        user = User(**raw_user)
        valid_users.append(user)
        print(f"Validated user: {user.name}")

    except ValidationError as e:
        print(f"Validation error for user {raw_user.get('name')} :")
        print(e)

print(f"\nTotal valid users: {len(valid_users)}")

# Convert valid User objects back to dictionaries for easier data handling
users_data = [user.model_dump() for user in valid_users]


# You can now access the data using list and dictionary indexing:
# print(users_data[0]['name']) 
# Output: John Doe