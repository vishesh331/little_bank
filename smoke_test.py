from bank import BankingSystem
from movie_tickets import _ensure_cinema_account, CINEMA_ACCOUNT
import pathlib

bs = BankingSystem()
# Ensure cinema account exists
try:
    _ensure_cinema_account()
except Exception as e:
    print('Cinema bootstrap error:', e)

# Create test account
acct = bs.create_account('Smoke Tester', 'safepass', initial_balance=500.0)
print('Created account:', acct)

# Deposit
bal = bs.deposit(acct['account_number'], 100.0)
print('After deposit:', bal)

# Withdraw
bal2 = bs.withdraw(acct['account_number'], 'safepass', 50.0)
print('After withdraw:', bal2)

# Transfer to cinema
receipt = bs.transfer(from_account=acct['account_number'], password='safepass', to_account=CINEMA_ACCOUNT, amount=200.0)
print('Transfer receipt:', receipt)

# Show accounts.json
print('\n--- accounts.json ---')
print(pathlib.Path('accounts.json').read_text(encoding='utf-8'))
