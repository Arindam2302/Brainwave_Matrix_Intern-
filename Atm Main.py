import getpass
from datetime import datetime

users = {
    '230902': {'pin': '2309', 'balance': 1000, 'transactions': [], 'failed_attempts': 0, 'fraud_flag': False},
    '654321': {'pin': '4321', 'balance': 500, 'transactions': [], 'failed_attempts': 0, 'fraud_flag': False}
}

def display_menu():
    print("\nATM Menu:")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transaction History")
    print("5. Change PIN")
    print("6. Exit")

def log_transaction(user_id, action, amount=0):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if action == 'Login Attempt':
        users[user_id]['transactions'].append(f"{timestamp} - {action}: {'Successful' if amount == 0 else 'Failed - Incorrect PIN'}")
    elif action == 'Withdrawal Attempt' and amount == 0:
        users[user_id]['transactions'].append(f"{timestamp} - {action}: Invalid PIN")
    elif action == 'Withdrawal Attempt':
        users[user_id]['transactions'].append(f"{timestamp} - {action}: Insufficient Funds")
    else:
        users[user_id]['transactions'].append(f"{timestamp} - {action}: ৳{amount}")

def check_balance(user_id):
    print(f"Your current balance is: ৳{users[user_id]['balance']}")

def deposit(user_id):
    try:
        amount = float(input("Enter amount to deposit: ৳"))
        if amount > 0:
            users[user_id]['balance'] += amount
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_transaction(user_id, 'Deposit', amount)
            print(f"{timestamp} - Deposited ৳{amount}. New balance: ৳{users[user_id]['balance']}")
        else:
            print("Invalid amount. Please enter a positive number.")
    except ValueError:
        print("Invalid input. Please enter a numerical value.")

def withdraw(user_id):
    if users[user_id]['fraud_flag']:
        print("Your account is temporarily blocked due to suspicious activity.")
        return

    try:
        amount = float(input("Enter amount to withdraw: ৳"))
        if 0 < amount <= users[user_id]['balance']:
            users[user_id]['balance'] -= amount
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_transaction(user_id, 'Withdraw', amount)
            print(f"{timestamp} - Withdrew ৳{amount}. New balance: ৳{users[user_id]['balance']}")
        elif amount > users[user_id]['balance']:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_transaction(user_id, 'Withdrawal Attempt', amount)
            print("Insufficient funds.")
        else:
            print("Invalid amount. Please enter a positive number.")
    except ValueError:
        print("Invalid input. Please enter a numerical value.")

def transaction_history(user_id):
    print("\nTransaction History:")
    if users[user_id]['transactions']:
        for transaction in users[user_id]['transactions']:
            print(transaction)
    else:
        print("No transactions found.")

def change_pin(user_id):
    new_pin = getpass.getpass("Enter your new PIN: ")
    confirm_pin = getpass.getpass("Confirm new PIN: ")
    if new_pin == confirm_pin:
        users[user_id]['pin'] = new_pin
        print("PIN changed successfully.")
    else:
        print("PINs do not match. Please try again.")

def atm_interface():
    print("Welcome to the ATM")

    while True:
        card_id = input("Please insert your card (Enter card ID): ").strip()

        if card_id not in users:
            print("Invalid card ID.")
            continue

        pin = getpass.getpass("Enter PIN: ")
        log_transaction(card_id, 'Login Attempt', 1)

        if pin != users[card_id]['pin']:
            users[card_id]['failed_attempts'] += 1
            if users[card_id]['failed_attempts'] >= 3:
                print("Your card has been blocked due to multiple incorrect PIN attempts.")
                users[card_id]['fraud_flag'] = True
                break
            print("Invalid PIN. Please try again.")
            continue

        users[card_id]['failed_attempts'] = 0
        log_transaction(card_id, 'Login Attempt', 0)

        while True:
            display_menu()
            choice = input("Select an option (1-6): ")

            if choice == '1':
                check_balance(card_id)
            elif choice == '2':
                deposit(card_id)
            elif choice == '3':
                withdraw(card_id)
            elif choice == '4':
                transaction_history(card_id)
            elif choice == '5':
                change_pin(card_id)
            elif choice == '6':
                print("Thank you for using the ATM. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option.")

atm_interface()
