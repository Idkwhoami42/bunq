from typing import List, Dict, Any
from models.task import Pot
from models.misc import State
from models.misc import ChatRequest
import json
from pathlib import Path
from models.bunq import MonetaryAccount, Alias, MonetaryValue
import random
PRE_POT_CREATION_PROMPT = """
You are SoberBuddy, a financial planner helping a group of friends plan their budget for an upcoming event.

You are in the initial planning phase where you need to:
1. Help the group define their shared savings for the event
2. Help each participant define their individual savings

Here are the participants: {participants}

The default currency is EUR, unless otherwise specified. 

Please be casual, fun, and extremely concise. Make this flow in a conversation. In your response refer with "you" and names of the participants.
"""

POT_CAN_BE_CREATED_PROMPT = """
You are SoberBuddy, a financial planner helping a group of friends plan their budget for an upcoming event.

The group has now provided enough information about their savings. You should create the shared pot.

Here are the participants: {participants}

The default currency is EUR, unless otherwise specified. 
"""

POT_CREATED_PROMPT = """
You are SoberBuddy, a c planner helping a group of friends plan their budget for an upcoming event.

The shared pot has been created. You should:
1. Help track contributions to shared and individual savings
2. Provide updates on progress towards savings.
3. Help manage any changes or adjustments to the savings
4. Encourage and motivate participants to stay on track

Here are the participants: {participants}
This is the current pot: {pot}

The default currency is EUR, unless otherwise specified. 

Please be casual, fun, and extremely concise. Make this flow in a conversation. In your response refer with "you" and names of the participants.
"""

EVENT_STARTED_PROMPT = """
The event is now in progress. You should:
1. Help find things to do in the area (use the tool search_web)
2. Try to keep track of the pot and the individual savings
3. Help manage any changes or adjustments to the savings
4. Encourage and motivate participants to stay on track

Here are the participants: {participants}
This is the current pot: {pot}
Here are the participants' bunq accounts: {accounts}
Here are the participants' transaction history: {transactions}

The default currency is EUR, unless otherwise specified. 

Please be casual, fun, and extremely concise. Make this flow in a conversation. In your response refer with "you" and names of the participants.

Be extremely concise.
"""

CHECK_FINANCIAL_DECISIONS_PROMPT = """
You are SoberBuddy, a financial planner helping a group of friends plan their budget for an upcoming event.

The event has been planned, and the pot has been created, you need to make sure that the people are on track to pay for the event. You should:
1. Check everyone's current contributions to the pot. 
2. Check everyone's current balance in their bunq accounts.
3. Check everyone's transaction history and report any unusually expensive transactions.
4. 

Here are the participants: {participants}
This is the current pot: {pot}
Here are the participants' bunq accounts: {accounts}
Here are the participants' transaction history: {transactions}

The default currency is EUR, unless otherwise specified. 

Please be casual, fun, and extremely concise. Make this flow in a conversation. In your response refer with "you" and names of the participants.
"""

TRIVIA_PROMPT = """
You are SoberBuddy, a financial planner helping a group of friends plan their budget for an upcoming event.

The event has been planned, and the pot has been created, you need to make sure that the people are excited for the event. You should:
1. Check the transaction history of the participants for what they like to do. 
2. Keep in mind the location of the trip and the weather of the location.
3. Create a trivia question based on the information above.

Here are the participants: {participants}
This is the current pot: {pot}
Here are the participants' bunq accounts: {accounts}
Here are the participants' transaction history: {transactions}

The default currency is EUR, unless otherwise specified. 

Please be casual, fun, and extremely concise. Make this flow in a conversation. In your response refer with "you" and names of the participants.
"""


def get_prompt(participants: List[str], pot: Pot = None, state: State = State.PRE_POT_CREATION, request: ChatRequest = None):
    """Get the prompt for the given state"""
    if state == State.PRE_POT_CREATION:
        return PRE_POT_CREATION_PROMPT.format(participants=participants)
    elif state == State.POT_CAN_BE_CREATED:
        return POT_CAN_BE_CREATED_PROMPT.format(participants=participants)
    elif state == State.POT_CREATED:
        return determine_task(request, pot)
    elif state == State.EVENT_STARTED:
        return EVENT_STARTED_PROMPT.format(participants=participants, pot=pot, accounts=[get_accounts_for_users(participant) for participant in participants], transactions=[get_transactions_for_users(participant) for participant in participants])
    else:
        return PRE_POT_CREATION_PROMPT.format(participants=participants)

def determine_task(request: ChatRequest, new_pot: Pot = None):
    if new_pot != request.pot:
        return POT_CREATED_PROMPT.format(participants=request.participants, pot=new_pot)
    elif random.random() < 0:
        return CHECK_FINANCIAL_DECISIONS_PROMPT.format(participants=request.participants, pot=new_pot, accounts=[get_accounts_for_users(participant) for participant in request.participants], transactions=[get_transactions_for_users(participant) for participant in request.participants])
    else:
        return TRIVIA_PROMPT.format(participants=request.participants, pot=new_pot, accounts=[get_accounts_for_users(participant) for participant in request.participants], transactions=[get_transactions_for_users(participant) for participant in request.participants])


def get_transactions_for_users(participant: str) -> List[Dict[str, Any]]:
    """
    Get the transactions for the given participant from the stored JSON files.
    
    Args:
        participant: Name of the participant to find transactions for
    
    Returns:
        List of transaction dictionaries containing payment details
    """
    try:
        # Read the payments data
        data_dir = Path("data")
        payments_path = data_dir / "my_bunq_payments.json"
        
        if not payments_path.exists():
            print(f"No payments data found at {payments_path}")
            return []
            
        with open(payments_path, 'r') as f:
            all_payments = json.load(f)
            
        # Filter payments by sender or receiver name and format them
        user_transactions = []
        for payment in all_payments:
            if payment.get('sender_name') == participant or payment.get('counterparty_name') == participant:
                formatted_transaction = {
                    "sender_name": payment.get('sender_name'),
                    "counterparty_name": payment.get('counterparty_name'),
                    "amount": {
                        "value": float(payment.get('amount', {}).get('value', 0)),
                        "currency": payment.get('amount', {}).get('currency')
                    },
                    "description": payment.get('description'),
                    "location": {
                        "latitude": float(payment.get('geolocation', {}).get('latitude', 0)),
                        "longitude": float(payment.get('geolocation', {}).get('longitude', 0))
                    } if payment.get('geolocation') else None,
                    "merchant_reference": payment.get('merchant_reference')
                }
                user_transactions.append(formatted_transaction)
                
        return user_transactions
        
    except Exception as e:
        print(f"Error getting user transactions: {str(e)}")
        raise

def get_accounts_for_users(participant: str) -> List[Dict[str, Any]]:
    """
    Get the accounts for the given participant from the stored JSON files.
    
    Args:
        participant: Name of the participant to find accounts for
    
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
            if account.get('owner_name') == participant:
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
                }
                user_accounts.append(formatted_account)
        return user_accounts
        
    except Exception as e:
        print(f"Error getting user accounts: {str(e)}")
        raise

def prompt_to_determine_state(request: ChatRequest):
    """Prompt to determine the state of the conversation"""
    
    prompt = ""
    
    if request.pot is None:
        prompt = """
        1. PRE_POT_CREATION: If the users have not provided enough information about their savings (individual AND shared).
        2. POT_CAN_BE_CREATED: If the users have provided enough information about their savings and have EXPLICITLY stated they have no more savings.
        """
    else:
        prompt = """
        POT_CREATED: If the pot has been created, and the users have NOT communicated that they have started the event.
        EVENT_STARTED: If the pot has been created, and the users have communicated that they have started the event.
        """
        
    return prompt
