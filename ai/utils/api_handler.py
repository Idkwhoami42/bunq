import json
from typing import Dict, Any, List
from pathlib import Path
from bunq.sdk.model.generated import endpoint
from bunq.sdk.context.bunq_context import BunqContext
from models.bunq import MonetaryAccount, Alias, MonetaryValue

def inspect_user_attributes(limit: int = 1) -> Dict[str, Any]:
    """
    Fetches a user and returns all available attributes and their values.
    
    Args:
        limit: Number of users to inspect (default 1)
    
    Returns:
        Dictionary containing attribute names and their values
    """
    try:
        # Get a user to inspect
        payments = endpoint.PaymentApiObject.list().value
        if not payments:
            print("No payments found")
            return {}
            
        payment = payments[0]
        
        # Get the UserPerson object
        user_person = payment
        
        # Get all attributes and their values from UserPerson
        attributes = {}
        for attr_name in dir(user_person):
            # Skip private attributes (starting with _)
            if not attr_name.startswith('_'):
                try:
                    value = getattr(user_person, attr_name)
                    # Convert to string if it's not a basic type
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        value = str(value)
                    attributes[attr_name] = value
                except Exception:
                    continue
                    
        return attributes
        
    except Exception as e:
        print(f"Error inspecting user attributes: {str(e)}")
        raise

def read_existing_data(output_path: Path) -> List[Dict[str, Any]]:
    """
    Reads existing data from a JSON file if it exists.
    Handles empty files and invalid JSON gracefully.
    
    Args:
        output_path: Path to the JSON file
    
    Returns:
        List of existing data or empty list if file doesn't exist or is empty/invalid
    """
    try:
        if output_path.exists() and output_path.stat().st_size > 0:
            with open(output_path, 'r') as f:
                content = f.read().strip()
                if content:  # Check if file is not empty
                    return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read existing data from {output_path}: {str(e)}")
    return []

def write_data(output_path: Path, data: List[Dict[str, Any]]) -> None:
    """
    Writes data to a JSON file.
    
    Args:
        output_path: Path to the JSON file
        data: Data to write
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error writing to {output_path}: {str(e)}")
        raise

def fetch_bunq_users(
    limit: int = 10,
    output_filename: str = "bunq_users.json"
) -> List[Dict[str, Any]]:
    """
    Fetches users from Bunq API up to the specified limit and appends the response to a JSON file.
    
    Args:
        limit: Maximum number of users to fetch
        output_filename: Name of the file to store the response
    
    Returns:
        List of user dictionaries
    """
    try:
        # Get users using Bunq SDK
        users = endpoint.UserApiObject.list().value
        
        # Convert to list of dictionaries
        users_data = []
        for user in users[:limit]:
            user_person = user.UserPerson
            user_dict = {
                "id": user_person.id_,
                "name": user_person.display_name,
                "public_uuid": user_person.public_uuid,
                "status": user_person.status,
                "full_name": user_person.first_name + " " +user_person.middle_name + " " + user_person.last_name,
                "gender": user_person.gender,
                "nationality": user_person.nationality,
            }
            users_data.append(user_dict)
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Define the output path
        output_path = data_dir / output_filename
        
        # Read existing data and append new data
        existing_data = read_existing_data(output_path)
        all_data = existing_data + users_data
        
        # Write the combined data to the JSON file
        write_data(output_path, all_data)
            
        print(f"Fetched {len(users_data)} users and appended to {output_path}")
        return users_data
        
    except Exception as e:
        print(f"Error fetching Bunq users: {str(e)}")
        raise

def fetch_monetary_accounts(
    name: str,
    limit: int = 10,
    output_filename: str = "monetary_accounts.json"
) -> List[Dict[str, Any]]:
    """
    Fetches monetary accounts from Bunq API up to the specified limit and appends the response to a JSON file.
    
    Args:
        limit: Maximum number of accounts to fetch
        output_filename: Name of the file to store the response
    
    Returns:
        List of monetary account dictionaries
    """
    try:
        # Get monetary accounts using Bunq SDK
        accounts = endpoint.MonetaryAccountBankApiObject.list().value
        
        # Convert to list of dictionaries
        accounts_data = []
        for account in accounts[:limit]:
            account_dict = {
                "id": account.id_,
                "description": account.description,
                "owner": account.user_id,
                "owner_name": name,
                "currency": account.currency,
                "balance": {
                    "value": account.balance.value,
                    "currency": account.balance.currency
                },
                "status": account.status,
                "daily_limit": {
                    "value": account.daily_limit.value if account.daily_limit else None,
                    "currency": account.daily_limit.currency if account.daily_limit else None
                },
                "alias": [
                    {
                        "type": alias.type_,
                        "value": alias.value,
                        "name": alias.name
                    } for alias in account.alias
                ] if account.alias else []
            }
            accounts_data.append(account_dict)
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Define the output path
        output_path = data_dir / output_filename
        
        # Read existing data and append new data
        existing_data = read_existing_data(output_path)
        all_data = existing_data + accounts_data
        
        # Write the combined data to the JSON file
        write_data(output_path, all_data)
            
        print(f"Fetched {len(accounts_data)} monetary accounts and appended to {output_path}")
        return accounts_data
        
    except Exception as e:
        print(f"Error fetching monetary accounts: {str(e)}")
        raise

def fetch_payments(
    name: str, 
    monetary_account_id: int,
    limit: int = 10,
    output_filename: str = "payments.json"
) -> List[Dict[str, Any]]:
    """
    Fetches payments from a specific monetary account up to the specified limit and appends the response to a JSON file.
    
    Args:
        monetary_account_id: ID of the monetary account to fetch payments from
        limit: Maximum number of payments to fetch
        output_filename: Name of the file to store the response
    
    Returns:
        List of payment dictionaries
    """
    try:
        # Get payments using Bunq SDK
        payments = endpoint.PaymentApiObject.list(monetary_account_id).value
        
        # Convert to list of dictionaries
        payments_data = []
        for payment in payments[:limit]:
            payment_dict = {
                "id": payment.id_,
                "sender_name": name,
                "amount": {
                    "value": payment.amount.value,
                    "currency": payment.amount.currency
                },
                "description": payment.description,

                "geolocation": {
                    "latitude": payment.geolocation.latitude,
                    "longitude": payment.geolocation.longitude
                } if payment.geolocation else None,

                "counterparty_name": payment.counterparty_alias.label_monetary_account.display_name if payment.counterparty_alias else None,
                "merchant_reference": payment.merchant_reference
            }
            payments_data.append(payment_dict)
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Define the output path
        output_path = data_dir / output_filename
        
        # Read existing data and append new data
        existing_data = read_existing_data(output_path)
        all_data = existing_data + payments_data
        
        # Write the combined data to the JSON file
        write_data(output_path, all_data)
            
        print(f"Fetched {len(payments_data)} payments and appended to {output_path}")
        return payments_data
        
    except Exception as e:
        print(f"Error fetching payments: {str(e)}")
        raise

def get_user_accounts(user_name: str) -> List[Dict[str, Any]]:
    """
    Finds all accounts associated with a user by their name and formats them according to the Pydantic models.
    
    Args:
        user_name: Name of the user to find accounts for
    
    Returns:
        List of account dictionaries matching the MonetaryAccount model
    """
    try:
        # Read the accounts data
        data_dir = Path("data")
        accounts_path = data_dir / "my_bunq_accounts.json"
        
        if not accounts_path.exists():
            print(f"No accounts data found at {accounts_path}")
            return []
            
        with open(accounts_path, 'r') as f:
            all_accounts = json.load(f)
            
        # Filter accounts by owner name and format them
        user_accounts = []
        for account in all_accounts:
            if account.get('owner_name') == user_name:
                formatted_account = {
                    "currency": account.get('currency'),
                    "description": account.get('description'),
                    "daily_limit": {
                        "value": float(account.get('daily_limit', {}).get('value', 0)),
                        "currency": account.get('daily_limit', {}).get('currency')
                    },
                    "balance": {
                        "value": float(account.get('balance', {}).get('value', 0)),
                        "currency": account.get('balance', {}).get('currency')
                    },
                    "owner_name": account.get('owner_name'),
                    "alias": {
                        "type": account.get('alias', {}).get('type'),
                        "value": account.get('alias', {}).get('value'),
                        "name": account.get('alias', {}).get('name')
                    }
                }
                user_accounts.append(formatted_account)
                
        return user_accounts
        
    except Exception as e:
        print(f"Error getting user accounts: {str(e)}")
        raise 
    