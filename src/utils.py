from enum import Enum, auto
import uuid
from datetime import datetime, time, timedelta
import hashlib
import heapq
import json
import os
import random
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


### Day 1
class AccountFrozenError(Exception):
    """Raised when an operation is attempted on a frozen account."""
    pass

class AccountClosedError(Exception):
    """Raised when an operation is attempted on a closed account."""
    pass

class InvalidOperationError(Exception):
    """Raised when an operation itself is structurally invalid (e.g., negative amounts)."""
    pass

class InsufficientFundsError(Exception):
    """Raised when a withdrawal amount exceeds the available balance."""
    pass

class AccountStatus(Enum):
    ACTIVE = auto()
    FROZEN = auto()
    CLOSED = auto()

class Currency(Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    KZT = "KZT"
    CNY = "CNY"

class AbstractAccount():
    
    def __init__(self, name: str, balance: float = 0.0, account_id: str = None):
        self._account_id = account_id if account_id else self._generate_uuid()
        self.name = name
        self._balance = float(balance)
        self._status = AccountStatus.ACTIVE

    def account_id(self) -> str:
        return self._account_id

    def balance(self) -> float:
        return self._balance

    def status(self) -> AccountStatus:
        return self._status

    def deposit(self, amount: float) -> None:
        pass

    def withdraw(self, amount: float) -> None:
        pass

    def get_account_info(self) -> dict:
        pass

    def _generate_uuid(self) -> str:
        return uuid.uuid4().hex[:8].upper()


class BankAccount(AbstractAccount):

    def __init__(self, name: str, balance: float = 0.0, 
                 currency: str = "RUB", account_id: str = None):
        
        try:
            self.currency = Currency[currency.upper()]
        except KeyError:
            raise InvalidOperationError(f"Unsupported currency: {currency}. Supported: {[c.name for c in Currency]}")
        
        if balance < 0:
            raise InvalidOperationError("Initial balance cannot be negative.")
            
        if not name.strip():
            raise InvalidOperationError("Owner name cannot be empty.")

        super().__init__(name=name, balance=balance, account_id=account_id)

    def _check_account_lifecycle_status(self) -> None:
        if self._status == AccountStatus.FROZEN:
            raise AccountFrozenError(f"Operation rejected. Account {self._account_id} is FROZEN.")
        if self._status == AccountStatus.CLOSED:
            raise AccountClosedError(f"Operation rejected. Account {self._account_id} is CLOSED.")

    def deposit(self, amount: float) -> None:
        self._check_account_lifecycle_status()
        
        if amount <= 0:
            raise InvalidOperationError("Deposit amount must be strictly positive.")
            
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        self._check_account_lifecycle_status()
        
        if amount <= 0:
            raise InvalidOperationError("Withdrawal amount must be strictly positive.")
            
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Requested: {amount} {self.currency.value}, Available: {self._balance} {self.currency.value}"
            )
            
        self._balance -= float(amount)

    def freeze_account(self) -> None:
        self._status = AccountStatus.FROZEN

    def unfreeze_account(self) -> None:
        if self._status == AccountStatus.CLOSED:
            raise AccountClosedError("Cannot unfreeze a permanently closed account.")
        self._status = AccountStatus.ACTIVE

    def close_account(self) -> None:
        self._status = AccountStatus.CLOSED

    def get_account_info(self) -> dict:
        return {
            "account_id": self._account_id,
            "name": self.name,
            "balance": self._balance,
            "currency": self.currency.value,
            "status": self._status.name
        }

    def __str__(self) -> str:
        masked_id = f"****{self._account_id[-4:]}" if len(self._account_id) >= 4 else self._account_id
        return (f"[{self.__class__.__name__}] Holder: {self.name} | "
                f"Acc No: {masked_id} | Status: {self._status.name} | "
                f"Balance: {self._balance:.2f} {self.currency.value}")


### Day 2

class SavingsAccount(BankAccount):
    """
    Savings account with a minimum balance requirement
    and monthly interest.
    """

    def __init__(
        self,
        name: str,
        balance: float = 0.0,
        currency: str = "RUB",
        account_id: str = None,
        min_balance: float = 0.0,
        monthly_interest_rate: float = 0.01
    ):
        if min_balance < 0:
            raise InvalidOperationError("Minimum balance cannot be negative.")

        if balance < min_balance:
            raise InvalidOperationError(
                "Initial balance cannot be lower than the minimum balance."
            )

        if monthly_interest_rate < 0:
            raise InvalidOperationError(
                "Monthly interest rate cannot be negative."
            )

        self.min_balance = float(min_balance)
        self.monthly_interest_rate = float(monthly_interest_rate)

        super().__init__(
            name=name,
            balance=balance,
            currency=currency,
            account_id=account_id
        )

    def withdraw(self, amount: float) -> None:
        self._check_account_lifecycle_status()

        if amount <= 0:
            raise InvalidOperationError(
                "Withdrawal amount must be strictly positive."
            )

        if self._balance - amount < self.min_balance:
            raise InsufficientFundsError(
                f"Withdrawal rejected. Minimum balance of "
                f"{self.min_balance:.2f} {self.currency.value} "
                f"must be maintained."
            )

        self._balance -= float(amount)

    def apply_monthly_interest(self) -> float:
        """
        Applies monthly interest to the current balance.

        Returns:
            The amount of interest added to the account.
        """
        self._check_account_lifecycle_status()

        interest = self._balance * self.monthly_interest_rate
        self._balance += interest

        return interest

    def get_account_info(self) -> dict:
        info = super().get_account_info()

        info.update({
            "account_type": "SavingsAccount",
            "min_balance": self.min_balance,
            "monthly_interest_rate": self.monthly_interest_rate
        })

        return info

    def __str__(self) -> str:
        masked_id = f"****{self._account_id[-4:]}"

        return (
            f"[SavingsAccount] Holder: {self.name} | "
            f"Acc No: {masked_id} | "
            f"Status: {self._status.name} | "
            f"Balance: {self._balance:.2f} {self.currency.value} | "
            f"Min Balance: {self.min_balance:.2f} | "
            f"Monthly Rate: {self.monthly_interest_rate:.2%}"
        )


class PremiumAccount(BankAccount):
    """
    Premium account with an overdraft facility and fixed fee.
    """

    def __init__(
        self,
        name: str,
        balance: float = 0.0,
        currency: str = "RUB",
        account_id: str = None,
        overdraft_limit: float = 10000.0,
        transaction_limit: float = 100000.0,
        fixed_fee: float = 100.0
    ):
        if balance < 0:
            raise InvalidOperationError(
                "Initial balance cannot be negative."
            )

        if overdraft_limit < 0:
            raise InvalidOperationError(
                "Overdraft limit cannot be negative."
            )

        if transaction_limit <= 0:
            raise InvalidOperationError(
                "Transaction limit must be positive."
            )

        if fixed_fee < 0:
            raise InvalidOperationError(
                "Fixed fee cannot be negative."
            )

        self.overdraft_limit = float(overdraft_limit)
        self.transaction_limit = float(transaction_limit)
        self.fixed_fee = float(fixed_fee)

        super().__init__(
            name=name,
            balance=balance,
            currency=currency,
            account_id=account_id
        )

    def deposit(self, amount: float) -> None:
        self._check_account_lifecycle_status()

        if amount <= 0:
            raise InvalidOperationError(
                "Deposit amount must be strictly positive."
            )

        if amount > self.transaction_limit:
            raise InvalidOperationError(
                f"Deposit exceeds premium account limit of "
                f"{self.transaction_limit:.2f} {self.currency.value}."
            )

        self._balance += float(amount)

    def withdraw(self, amount: float) -> None:
        self._check_account_lifecycle_status()

        if amount <= 0:
            raise InvalidOperationError(
                "Withdrawal amount must be strictly positive."
            )

        if amount > self.transaction_limit:
            raise InvalidOperationError(
                f"Withdrawal exceeds premium account limit of "
                f"{self.transaction_limit:.2f} {self.currency.value}."
            )

        if self._balance - amount < -self.overdraft_limit:
            raise InsufficientFundsError(
                f"Overdraft limit exceeded. Maximum allowed overdraft: "
                f"{self.overdraft_limit:.2f} {self.currency.value}."
            )

        self._balance -= float(amount)

    def charge_fixed_fee(self) -> None:
        """
        Charges the fixed account fee.

        The fee itself cannot cause the balance to exceed
        the allowed overdraft limit.
        """
        self._check_account_lifecycle_status()

        if self._balance - self.fixed_fee < -self.overdraft_limit:
            raise InsufficientFundsError(
                "Insufficient funds to charge the fixed fee "
                "within the overdraft limit."
            )

        self._balance -= self.fixed_fee

    def get_account_info(self) -> dict:
        info = super().get_account_info()

        info.update({
            "account_type": "PremiumAccount",
            "overdraft_limit": self.overdraft_limit,
            "transaction_limit": self.transaction_limit,
            "fixed_fee": self.fixed_fee
        })

        return info

    def __str__(self) -> str:
        masked_id = f"****{self._account_id[-4:]}"

        return (
            f"[PremiumAccount] Holder: {self.name} | "
            f"Acc No: {masked_id} | "
            f"Status: {self._status.name} | "
            f"Balance: {self._balance:.2f} {self.currency.value} | "
            f"Overdraft: {self.overdraft_limit:.2f} | "
            f"Fixed Fee: {self.fixed_fee:.2f}"
        )


class InvestmentAccount(BankAccount):
    """
    Simplified educational investment account.

    The portfolio stores amounts allocated to virtual asset types:
    stocks, bonds and etf.
    """

    ALLOWED_ASSETS = {"stocks", "bonds", "etf"}

    def __init__(
        self,
        name: str,
        balance: float = 0.0,
        currency: str = "RUB",
        account_id: str = None
    ):
        super().__init__(
            name=name,
            balance=balance,
            currency=currency,
            account_id=account_id
        )

        self.portfolio = {
            "stocks": 0.0,
            "bonds": 0.0,
            "etf": 0.0
        }

    def invest(self, asset_type: str, amount: float) -> None:
        """
        Allocates money from the account balance to an asset type.
        """
        self._check_account_lifecycle_status()

        if not isinstance(asset_type, str):
            raise InvalidOperationError(
                "Asset type must be a string."
            )

        asset_type = asset_type.lower()

        if asset_type not in self.ALLOWED_ASSETS:
            raise InvalidOperationError(
                f"Unsupported asset type: {asset_type}. "
                f"Allowed types: {sorted(self.ALLOWED_ASSETS)}"
            )

        if amount <= 0:
            raise InvalidOperationError(
                "Investment amount must be strictly positive."
            )

        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: "
                f"{self._balance:.2f} {self.currency.value}."
            )

        self._balance -= float(amount)
        self.portfolio[asset_type] += float(amount)

    def withdraw(self, amount: float) -> None:
        """
        Withdraws money only from the available cash balance.
        Invested funds are not automatically sold.
        """
        self._check_account_lifecycle_status()

        if amount <= 0:
            raise InvalidOperationError(
                "Withdrawal amount must be strictly positive."
            )

        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient available cash. "
                f"Requested: {amount:.2f}, "
                f"Available: {self._balance:.2f} "
                f"{self.currency.value}."
            )

        self._balance -= float(amount)

    def project_yearly_growth(self, growth_rates: dict) -> float:
        """
        Calculates expected yearly growth of the portfolio.

        growth_rates example:
        {
            "stocks": 0.10,
            "bonds": 0.04,
            "etf": 0.07
        }
        """
        if not isinstance(growth_rates, dict):
            raise InvalidOperationError(
                "growth_rates must be a dictionary."
            )

        total_growth = 0.0

        for asset_type, amount in self.portfolio.items():
            if asset_type not in growth_rates:
                raise InvalidOperationError(
                    f"Growth rate for '{asset_type}' is missing."
                )

            rate = growth_rates[asset_type]

            if rate < 0:
                raise InvalidOperationError(
                    f"Growth rate for '{asset_type}' cannot be negative."
                )

            total_growth += amount * rate

        return total_growth

    def get_account_info(self) -> dict:
        info = super().get_account_info()

        info.update({
            "account_type": "InvestmentAccount",
            "portfolio": self.portfolio.copy(),
            "portfolio_total": sum(self.portfolio.values())
        })

        return info

    def __str__(self) -> str:
        masked_id = f"****{self._account_id[-4:]}"
        portfolio_total = sum(self.portfolio.values())

        return (
            f"[InvestmentAccount] Holder: {self.name} | "
            f"Acc No: {masked_id} | "
            f"Status: {self._status.name} | "
            f"Cash: {self._balance:.2f} {self.currency.value} | "
            f"Portfolio: {portfolio_total:.2f} {self.currency.value}"
        )

### Day 3

class Client:
    """
    Represents a bank client.

    Stores personal information, contact details,
    account IDs and authentication/security state.
    """

    def __init__(
        self,
        full_name: str,
        client_id: str,
        age: int,
        contacts: dict,
        password: str
    ):
        if not isinstance(full_name, str) or not full_name.strip():
            raise InvalidOperationError(
                "Client full name cannot be empty."
            )

        if not isinstance(client_id, str) or not client_id.strip():
            raise InvalidOperationError(
                "Client ID cannot be empty."
            )

        if age < 18:
            raise InvalidOperationError(
                "Client must be at least 18 years old."
            )

        if not isinstance(contacts, dict):
            raise InvalidOperationError(
                "Contacts must be provided as a dictionary."
            )

        if not isinstance(password, str) or len(password) < 4:
            raise InvalidOperationError(
                "Password must contain at least 4 characters."
            )

        self.full_name = full_name
        self.client_id = client_id
        self.age = age
        self.contacts = contacts

        # Account IDs belonging to this client.
        self.account_ids = []

        # Client status.
        self.status = "ACTIVE"

        # Authentication data.
        self._password_hash = self._hash_password(password)
        self.failed_login_attempts = 0
        self.is_blocked = False

        # Security/audit-related information.
        self.suspicious_actions = []

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        """
        Checks whether the supplied password is correct.
        """
        password_hash = self._hash_password(password)
        return password_hash == self._password_hash

    def add_account(self, account_id: str) -> None:
        if account_id not in self.account_ids:
            self.account_ids.append(account_id)

    def remove_account(self, account_id: str) -> None:
        if account_id in self.account_ids:
            self.account_ids.remove(account_id)

    def mark_suspicious(self, action: str) -> None:
        self.suspicious_actions.append({
            "action": action,
            "timestamp": datetime.now()
        })

    def __str__(self) -> str:
        return (
            f"Client: {self.full_name} | "
            f"ID: {self.client_id} | "
            f"Status: {self.status} | "
            f"Accounts: {len(self.account_ids)}"
        )


class Bank:
    """
    Central management class for clients and bank accounts.
    """

    MAX_LOGIN_ATTEMPTS = 3

    def __init__(self, name: str):
        if not isinstance(name, str) or not name.strip():
            raise InvalidOperationError(
                "Bank name cannot be empty."
            )

        self.name = name

        # In-memory storage.
        self.clients = {}
        self.accounts = {}

    # ==========================================================
    # SECURITY / TIME RESTRICTIONS
    # ==========================================================

    @staticmethod
    def _is_night_time(current_time=None) -> bool:
        """
        Returns True between 00:00 and 05:00.

        current_time can be supplied for testing.
        """
        if current_time is None:
            current_time = datetime.now().time()

        return current_time.hour < 5

    def _check_operation_time(self, current_time=None) -> None:
        """
        Bank operations are prohibited from 00:00 to 05:00.
        """
        if self._is_night_time(current_time):
            raise InvalidOperationError(
                "Bank operations are prohibited from 00:00 to 05:00."
            )

    # ==========================================================
    # CLIENT MANAGEMENT
    # ==========================================================

    def add_client(self, client: Client) -> None:
        self._check_operation_time()

        if not isinstance(client, Client):
            raise InvalidOperationError(
                "Only Client objects can be added."
            )

        if client.client_id in self.clients:
            raise InvalidOperationError(
                f"Client with ID {client.client_id} already exists."
            )

        self.clients[client.client_id] = client

    def get_client(self, client_id: str) -> Client:
        if client_id not in self.clients:
            raise InvalidOperationError(
                f"Client {client_id} not found."
            )

        return self.clients[client_id]

    # ==========================================================
    # ACCOUNT MANAGEMENT
    # ==========================================================

    def open_account(
        self,
        client_id: str,
        account_type=BankAccount,
        **kwargs
    ):
        """
        Opens an account for an existing client.

        account_type can be:
        - BankAccount
        - SavingsAccount
        - PremiumAccount
        - InvestmentAccount
        """
        self._check_operation_time()

        client = self.get_client(client_id)

        if client.status != "ACTIVE":
            raise InvalidOperationError(
                "Inactive client cannot open an account."
            )

        account = account_type(
            name=client.full_name,
            **kwargs
        )

        self.accounts[account.account_id()] = account
        client.add_account(account.account_id())

        return account

    def close_account(self, account_id: str) -> None:
        self._check_operation_time()

        account = self._get_account(account_id)

        account.close_account()

    def freeze_account(self, account_id: str) -> None:
        self._check_operation_time()

        account = self._get_account(account_id)

        account.freeze_account()

    def unfreeze_account(self, account_id: str) -> None:
        self._check_operation_time()

        account = self._get_account(account_id)

        account.unfreeze_account()

    def _get_account(self, account_id: str):
        if account_id not in self.accounts:
            raise InvalidOperationError(
                f"Account {account_id} not found."
            )

        return self.accounts[account_id]

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    def authenticate_client(
        self,
        client_id: str,
        password: str
    ) -> bool:
        """
        Authenticates a client.

        After 3 failed attempts, the client is blocked.
        """
        self._check_operation_time()

        client = self.get_client(client_id)

        if client.is_blocked:
            client.mark_suspicious(
                "Authentication attempt on blocked account"
            )

            raise InvalidOperationError(
                "Client is blocked because of too many failed "
                "authentication attempts."
            )

        if client.verify_password(password):
            client.failed_login_attempts = 0
            return True

        # Wrong password.
        client.failed_login_attempts += 1

        client.mark_suspicious(
            f"Failed authentication attempt "
            f"#{client.failed_login_attempts}"
        )

        if (
            client.failed_login_attempts
            >= self.MAX_LOGIN_ATTEMPTS
        ):
            client.is_blocked = True
            client.status = "BLOCKED"

            client.mark_suspicious(
                "Client automatically blocked after "
                "three failed login attempts"
            )

            raise InvalidOperationError(
                "Client has been blocked after 3 failed "
                "authentication attempts."
            )

        raise InvalidOperationError(
            f"Invalid password. Attempt "
            f"{client.failed_login_attempts}/"
            f"{self.MAX_LOGIN_ATTEMPTS}."
        )

    # ==========================================================
    # ACCOUNT SEARCH
    # ==========================================================

    def search_accounts(
        self,
        client_id: str = None,
        status: AccountStatus = None,
        currency: str = None
    ) -> list:
        """
        Searches accounts using optional filters.
        """
        results = list(self.accounts.values())

        if client_id is not None:
            client = self.get_client(client_id)

            results = [
                account
                for account in results
                if account.account_id() in client.account_ids
            ]

        if status is not None:
            results = [
                account
                for account in results
                if account.status() == status
            ]

        if currency is not None:
            currency_code = currency.upper()

            results = [
                account
                for account in results
                if account.currency.value == currency_code
            ]

        return results

    # ==========================================================
    # REPORTING / ANALYTICS
    # ==========================================================

    def get_total_balance(self) -> float:
        """
        Returns the total balance of all accounts.

        For this educational model, balances are summed directly.
        No currency conversion is performed.
        """
        return sum(
            account.balance()
            for account in self.accounts.values()
        )

    def get_clients_ranking(self) -> list:
        """
        Returns clients ranked by the total balance
        of their accounts.

        Result:
        [
            {
                "client_id": ...,
                "name": ...,
                "total_balance": ...
            },
            ...
        ]
        """
        ranking = []

        for client in self.clients.values():
            total_balance = sum(
                self.accounts[account_id].balance()
                for account_id in client.account_ids
                if account_id in self.accounts
            )

            ranking.append({
                "client_id": client.client_id,
                "name": client.full_name,
                "total_balance": total_balance
            })

        ranking.sort(
            key=lambda item: item["total_balance"],
            reverse=True
        )

        return ranking

    def __str__(self) -> str:
        return (
            f"Bank: {self.name} | "
            f"Clients: {len(self.clients)} | "
            f"Accounts: {len(self.accounts)}"
        )

#### Day 4


# ==============================================================
# TRANSACTION ENUMS
# ==============================================================

class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    INTERNAL_TRANSFER = auto()
    EXTERNAL_TRANSFER = auto()


class TransactionStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


# ==============================================================
# TRANSACTION
# ==============================================================

class Transaction:
    """
    Represents a single financial operation.

    The class stores transaction metadata but does not itself
    execute the operation.
    """

    def __init__(
        self,
        transaction_type: TransactionType,
        amount: float,
        currency: str,
        sender=None,
        receiver=None,
        fee: float = 0.0,
        priority: int = 5,
        scheduled_at=None
    ):
        if not isinstance(transaction_type, TransactionType):
            raise InvalidOperationError(
                "Invalid transaction type."
            )

        if amount <= 0:
            raise InvalidOperationError(
                "Transaction amount must be strictly positive."
            )

        if fee < 0:
            raise InvalidOperationError(
                "Transaction fee cannot be negative."
            )

        try:
            self.currency = Currency[currency.upper()]
        except KeyError:
            raise InvalidOperationError(
                f"Unsupported currency: {currency}."
            )

        if not isinstance(priority, int) or priority < 0:
            raise InvalidOperationError(
                "Priority must be a non-negative integer."
            )

        self.transaction_id = uuid.uuid4().hex[:12].upper()

        self.transaction_type = transaction_type
        self.amount = float(amount)
        self.fee = float(fee)

        self.sender = sender
        self.receiver = receiver

        self.status = TransactionStatus.PENDING
        self.failure_reason = None

        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None

        self.priority = priority

        self.scheduled_at = (
            scheduled_at
            if scheduled_at is not None
            else self.created_at
        )

        self.retry_count = 0
        self.error_log = []

    def mark_processing(self) -> None:
        self.status = TransactionStatus.PROCESSING
        self.started_at = datetime.now()

    def mark_completed(self) -> None:
        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.now()

    def mark_failed(self, reason: str) -> None:
        self.status = TransactionStatus.FAILED
        self.failure_reason = reason
        self.error_log.append({
            "timestamp": datetime.now(),
            "error": reason
        })

    def cancel(self) -> None:
        if self.status in (
            TransactionStatus.COMPLETED,
            TransactionStatus.CANCELLED
        ):
            raise InvalidOperationError(
                "Completed or already cancelled transaction "
                "cannot be cancelled."
            )

        self.status = TransactionStatus.CANCELLED

    def __str__(self) -> str:
        return (
            f"[Transaction {self.transaction_id}] "
            f"{self.transaction_type.name} | "
            f"{self.amount:.2f} {self.currency.value} | "
            f"Status: {self.status.name} | "
            f"Priority: {self.priority}"
        )


# ==============================================================
# TRANSACTION QUEUE
# ==============================================================

class TransactionQueue:
    """
    Priority queue for transactions.

    Lower priority number = higher priority.

    Example:
        priority=1 -> processed before priority=5
    """

    def __init__(self):
        self._queue = []
        self._counter = 0
        self._transactions = {}

    def add(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError(
                "Only Transaction objects can be added."
            )

        if transaction.status != TransactionStatus.PENDING:
            raise InvalidOperationError(
                "Only pending transactions can be added to the queue."
            )

        heapq.heappush(
            self._queue,
            (
                transaction.scheduled_at,
                transaction.priority,
                self._counter,
                transaction.transaction_id
            )
        )

        self._counter += 1

        self._transactions[
            transaction.transaction_id
        ] = transaction

    def cancel(self, transaction_id: str) -> None:
        if transaction_id not in self._transactions:
            raise InvalidOperationError(
                f"Transaction {transaction_id} not found."
            )

        transaction = self._transactions[transaction_id]

        transaction.cancel()

    def get_next(self, current_time=None):
        """
        Returns the next executable transaction.

        Delayed transactions are skipped until their scheduled time.
        """
        if current_time is None:
            current_time = datetime.now()

        while self._queue:
            (
                scheduled_at,
                priority,
                counter,
                transaction_id
            ) = heapq.heappop(self._queue)

            transaction = self._transactions[transaction_id]

            if transaction.status == TransactionStatus.CANCELLED:
                continue

            if scheduled_at > current_time:
                heapq.heappush(
                    self._queue,
                    (
                        scheduled_at,
                        priority,
                        counter,
                        transaction_id
                    )
                )

                return None

            return transaction

        return None

    def __len__(self):
        return sum(
            1
            for transaction in self._transactions.values()
            if transaction.status == TransactionStatus.PENDING
        )


# ==============================================================
# TRANSACTION PROCESSOR
# ==============================================================

class TransactionProcessor:
    """
    Executes transactions from a TransactionQueue.

    Supports:
    - fees
    - currency conversion
    - retries
    - error logging
    """

    def __init__(
        self,
        bank: Bank,
        exchange_rates=None,
        external_transfer_fee: float = 0.02,
        max_retries: int = 2
    ):
        self.bank = bank

        self.exchange_rates = exchange_rates or {}

        self.external_transfer_fee = external_transfer_fee

        self.max_retries = max_retries

        self.processed_transactions = []
        self.error_log = []

    # ----------------------------------------------------------
    # ACCOUNT HELPERS
    # ----------------------------------------------------------

    def _get_account(self, account_id):
        return self.bank._get_account(account_id)

    def _check_account_available(self, account):
        if account.status() == AccountStatus.FROZEN:
            raise AccountFrozenError(
                f"Account {account.account_id()} is frozen."
            )

        if account.status() == AccountStatus.CLOSED:
            raise AccountClosedError(
                f"Account {account.account_id()} is closed."
            )

    # ----------------------------------------------------------
    # CURRENCY CONVERSION
    # ----------------------------------------------------------

    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> float:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return amount

        key = (from_currency, to_currency)

        if key not in self.exchange_rates:
            raise InvalidOperationError(
                f"No exchange rate available for "
                f"{from_currency} -> {to_currency}."
            )

        return amount * self.exchange_rates[key]

    # ----------------------------------------------------------
    # FEE CALCULATION
    # ----------------------------------------------------------

    def calculate_fee(
        self,
        transaction: Transaction
    ) -> float:
        """
        External transfers receive a percentage fee.
        Internal transfers have no fee in this model.
        """
        if (
            transaction.transaction_type
            == TransactionType.EXTERNAL_TRANSFER
        ):
            return (
                transaction.amount
                * self.external_transfer_fee
            )

        return 0.0

    # ----------------------------------------------------------
    # TRANSFER PROCESSING
    # ----------------------------------------------------------

    def _process_transfer(
        self,
        transaction: Transaction
    ) -> None:

        if transaction.sender is None:
            raise InvalidOperationError(
                "Transfer must have a sender."
            )

        if transaction.receiver is None:
            raise InvalidOperationError(
                "Transfer must have a receiver."
            )

        sender = self._get_account(
            transaction.sender
        )

        receiver = self._get_account(
            transaction.receiver
        )

        self._check_account_available(sender)
        self._check_account_available(receiver)

        # ------------------------------------------------------
        # Negative balance rule
        # ------------------------------------------------------

        if (
            transaction.transaction_type
            != TransactionType.EXTERNAL_TRANSFER
        ):
            # PremiumAccount is allowed to use its overdraft.
            if not isinstance(sender, PremiumAccount):
                if sender.balance() < transaction.amount:
                    raise InsufficientFundsError(
                        "Negative balance is not allowed for "
                        "this account type."
                    )

        # ------------------------------------------------------
        # Calculate fee
        # ------------------------------------------------------

        fee = self.calculate_fee(transaction)

        transaction.fee = fee

        total_required = transaction.amount + fee

        # ------------------------------------------------------
        # Withdraw from sender
        # ------------------------------------------------------

        sender.withdraw(total_required)

        # ------------------------------------------------------
        # Currency conversion
        # ------------------------------------------------------

        receiver_amount = self.convert_currency(
            transaction.amount,
            transaction.currency.value,
            receiver.currency.value
        )

        receiver.deposit(receiver_amount)

    # ----------------------------------------------------------
    # SINGLE TRANSACTION PROCESSING
    # ----------------------------------------------------------

    def process_transaction(
        self,
        transaction: Transaction
    ) -> bool:

        if transaction.status == TransactionStatus.CANCELLED:
            return False

        transaction.mark_processing()

        try:

            if transaction.transaction_type in (
                TransactionType.INTERNAL_TRANSFER,
                TransactionType.EXTERNAL_TRANSFER
            ):
                self._process_transfer(transaction)

            else:
                raise InvalidOperationError(
                    "Only transfer transactions are supported "
                    "by this processor."
                )

            transaction.mark_completed()

            self.processed_transactions.append(
                transaction
            )

            return True

        except Exception as error:

            transaction.mark_failed(
                str(error)
            )

            self.error_log.append({
                "transaction_id": transaction.transaction_id,
                "timestamp": datetime.now(),
                "error": str(error)
            })

            return False

    # ----------------------------------------------------------
    # RETRY PROCESSING
    # ----------------------------------------------------------

    def process_with_retry(
        self,
        transaction: Transaction
    ) -> bool:

        while (
            transaction.retry_count
            <= self.max_retries
        ):

            success = self.process_transaction(
                transaction
            )

            if success:
                return True

            if transaction.retry_count >= self.max_retries:
                return False

            transaction.retry_count += 1

            # Restore status so it can be retried.
            transaction.status = (
                TransactionStatus.PENDING
            )

        return False

    # ----------------------------------------------------------
    # QUEUE PROCESSING
    # ----------------------------------------------------------

    def process_queue(
        self,
        queue: TransactionQueue
    ) -> list:

        results = []

        while True:

            transaction = queue.get_next()

            if transaction is None:
                break

            success = self.process_with_retry(
                transaction
            )

            results.append({
                "transaction_id":
                    transaction.transaction_id,
                "success": success,
                "status":
                    transaction.status.name
            })

        return results

### Day 5

# ==============================================================
# AUDIT / RISK ENUMS
# ==============================================================

class AuditLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class RiskLevel(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


# ==============================================================
# AUDIT LOG
# ==============================================================

class AuditLog:
    """
    Stores audit events in memory and optionally in a file.

    Each event contains:
    - timestamp
    - importance level
    - event type
    - message
    - optional client/transaction IDs
    """

    def __init__(self, file_path: str = "audit.log"):
        project_dir = Path(__file__).resolve().parent  # use .parent.parent if needed
        path = project_dir / file_path
        self.file_path = path
        self.entries = []

    def log(
        self,
        level: AuditLevel,
        event_type: str,
        message: str,
        client_id: str = None,
        transaction_id: str = None
    ) -> dict:

        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.name,
            "event_type": event_type,
            "message": message,
            "client_id": client_id,
            "transaction_id": transaction_id
        }

        self.entries.append(entry)

        self._save_to_file(entry)

        return entry

    def _save_to_file(self, entry: dict) -> None:
        """
        Appends one JSON-formatted audit event to the file.
        """
        try:
            with open(
                self.file_path,
                "a",
                encoding="utf-8"
            ) as file:
                file.write(
                    json.dumps(
                        entry,
                        ensure_ascii=False
                    ) + "\n"
                )

        except OSError as error:
            # File errors should not destroy the in-memory audit log.
            print(
                f"Warning: could not write audit log: {error}"
            )

    def filter(
        self,
        level: AuditLevel = None,
        event_type: str = None,
        client_id: str = None,
        transaction_id: str = None
    ) -> list:

        result = self.entries

        if level is not None:
            result = [
                entry
                for entry in result
                if entry["level"] == level.name
            ]

        if event_type is not None:
            result = [
                entry
                for entry in result
                if entry["event_type"] == event_type
            ]

        if client_id is not None:
            result = [
                entry
                for entry in result
                if entry["client_id"] == client_id
            ]

        if transaction_id is not None:
            result = [
                entry
                for entry in result
                if entry["transaction_id"] == transaction_id
            ]

        return result

    def get_errors(self) -> list:
        """
        Returns WARNING, ERROR and CRITICAL events.
        """
        error_levels = {
            AuditLevel.WARNING.name,
            AuditLevel.ERROR.name,
            AuditLevel.CRITICAL.name
        }

        return [
            entry
            for entry in self.entries
            if entry["level"] in error_levels
        ]


# ==============================================================
# RISK ANALYZER
# ==============================================================

class RiskAnalyzer:
    """
    Analyzes transactions and assigns a risk level.

    Risk indicators:
    1. Large transaction amount.
    2. Frequent transactions.
    3. Transfer to a new/unfamiliar account.
    4. Night-time operation.
    """

    def __init__(
        self,
        large_amount_threshold: float = 50000,
        frequent_operations_threshold: int = 5,
        frequent_operations_window_minutes: int = 10
    ):
        self.large_amount_threshold = (
            large_amount_threshold
        )

        self.frequent_operations_threshold = (
            frequent_operations_threshold
        )

        self.frequent_operations_window = timedelta(
            minutes=frequent_operations_window_minutes
        )

        # client_id -> set of known receiver account IDs
        self.known_receivers = {}

        # client_id -> transaction timestamps
        self.client_operations = {}

    # ----------------------------------------------------------
    # LARGE AMOUNT
    # ----------------------------------------------------------

    def _is_large_amount(
        self,
        transaction: Transaction
    ) -> bool:
        return (
            transaction.amount
            >= self.large_amount_threshold
        )

    # ----------------------------------------------------------
    # FREQUENT OPERATIONS
    # ----------------------------------------------------------

    def _is_frequent_operation(
        self,
        transaction: Transaction,
        current_time: datetime
    ) -> bool:

        if transaction.sender is None:
            return False

        sender_account = transaction.sender

        timestamps = self.client_operations.setdefault(
            sender_account,
            []
        )

        window_start = (
            current_time
            - self.frequent_operations_window
        )

        recent_operations = [
            timestamp
            for timestamp in timestamps
            if timestamp >= window_start
        ]

        return (
            len(recent_operations)
            >= self.frequent_operations_threshold
        )

    def _record_operation(
        self,
        transaction: Transaction,
        current_time: datetime
    ) -> None:

        if transaction.sender is None:
            return

        timestamps = self.client_operations.setdefault(
            transaction.sender,
            []
        )

        timestamps.append(current_time)

    # ----------------------------------------------------------
    # NEW RECEIVER
    # ----------------------------------------------------------

    def _is_new_receiver(
        self,
        transaction: Transaction
    ) -> bool:

        if (
            transaction.sender is None
            or transaction.receiver is None
        ):
            return False

        known = self.known_receivers.setdefault(
            transaction.sender,
            set()
        )

        return transaction.receiver not in known

    def _record_receiver(
        self,
        transaction: Transaction
    ) -> None:

        if (
            transaction.sender is None
            or transaction.receiver is None
        ):
            return

        known = self.known_receivers.setdefault(
            transaction.sender,
            set()
        )

        known.add(transaction.receiver)

    # ----------------------------------------------------------
    # NIGHT OPERATION
    # ----------------------------------------------------------

    @staticmethod
    def _is_night_operation(
        timestamp: datetime
    ) -> bool:

        current_time = timestamp.time()

        return (
            current_time >= time(0, 0)
            and current_time < time(5, 0)
        )

    # ----------------------------------------------------------
    # MAIN ANALYSIS
    # ----------------------------------------------------------

    def analyze(
        self,
        transaction: Transaction,
        timestamp: datetime = None
    ) -> dict:

        if timestamp is None:
            timestamp = datetime.now()

        indicators = []

        if self._is_large_amount(transaction):
            indicators.append(
                "large_amount"
            )

        if self._is_frequent_operation(
            transaction,
            timestamp
        ):
            indicators.append(
                "frequent_operations"
            )

        if self._is_new_receiver(transaction):
            indicators.append(
                "new_receiver"
            )

        if self._is_night_operation(timestamp):
            indicators.append(
                "night_operation"
            )

        # ------------------------------------------------------
        # Risk scoring
        # ------------------------------------------------------

        score = len(indicators)

        if score >= 3:
            risk_level = RiskLevel.HIGH

        elif score >= 1:
            risk_level = RiskLevel.MEDIUM

        else:
            risk_level = RiskLevel.LOW

        return {
            "transaction_id":
                transaction.transaction_id,

            "risk_level":
                risk_level,

            "score":
                score,

            "indicators":
                indicators
        }

    # ----------------------------------------------------------
    # RECORD SUCCESSFUL OPERATION
    # ----------------------------------------------------------

    def record_transaction(
        self,
        transaction: Transaction,
        timestamp: datetime = None
    ) -> None:

        if timestamp is None:
            timestamp = datetime.now()

        self._record_operation(
            transaction,
            timestamp
        )

        self._record_receiver(
            transaction
        )


# ==============================================================
# BANK SECURITY CONTROLLER
# ==============================================================

class BankSecurityController:
    """
    Connects the RiskAnalyzer and AuditLog.

    High-risk transactions are blocked.
    """

    def __init__(
        self,
        bank: Bank,
        audit_log: AuditLog,
        risk_analyzer: RiskAnalyzer
    ):
        self.bank = bank
        self.audit_log = audit_log
        self.risk_analyzer = risk_analyzer

        self.blocked_transactions = []

    def _get_client_id_from_transaction(
        self,
        transaction: Transaction
    ) -> str | None:
        """
        Finds the client ID that owns the sender account.
        """

        if transaction.sender is None:
            return None

        sender_account_id = transaction.sender

        for client in self.bank.clients.values():
            if sender_account_id in client.account_ids:
                return client.client_id

        return None

    def check_transaction(
        self,
        transaction: Transaction,
        timestamp: datetime = None
    ) -> dict:

        result = self.risk_analyzer.analyze(
            transaction,
            timestamp=timestamp
        )

        risk_level = result["risk_level"]

        # Find the client who owns the sender account.
        client_id = self._get_client_id_from_transaction(
            transaction
        )

        if risk_level == RiskLevel.HIGH:

            transaction.mark_failed(
                "Transaction blocked by risk analysis."
            )

            self.blocked_transactions.append(
                transaction.transaction_id
            )

            self.audit_log.log(
                level=AuditLevel.CRITICAL,
                event_type="TRANSACTION_BLOCKED",
                message=(
                    "High-risk transaction blocked. "
                    f"Indicators: {result['indicators']}"
                ),
                client_id=client_id,
                transaction_id=transaction.transaction_id
            )

            return {
                **result,
                "blocked": True
            }

        if risk_level == RiskLevel.MEDIUM:

            self.audit_log.log(
                level=AuditLevel.WARNING,
                event_type="SUSPICIOUS_TRANSACTION",
                message=(
                    "Medium-risk transaction detected. "
                    f"Indicators: {result['indicators']}"
                ),
                client_id=client_id,
                transaction_id=transaction.transaction_id
            )

        else:

            self.audit_log.log(
                level=AuditLevel.INFO,
                event_type="NORMAL_TRANSACTION",
                message="Transaction classified as low risk.",
                client_id=client_id,
                transaction_id=transaction.transaction_id
            )

        return {
            **result,
            "blocked": False
        }

    def record_successful_transaction(
        self,
        transaction: Transaction
    ) -> None:

        self.risk_analyzer.record_transaction(
            transaction
        )


# ==============================================================
# AUDIT REPORTER
# ==============================================================

class AuditReporter:
    """
    Generates audit and risk reports.
    """

    def __init__(
        self,
        audit_log: AuditLog,
        risk_analyzer: RiskAnalyzer
    ):
        self.audit_log = audit_log
        self.risk_analyzer = risk_analyzer

    def suspicious_operations_report(self) -> list:
        """
        Returns all warning and critical audit events.
        """
        suspicious_levels = {
            AuditLevel.WARNING.name,
            AuditLevel.CRITICAL.name
        }

        return [
            entry
            for entry in self.audit_log.entries
            if entry["level"] in suspicious_levels
        ]

    def client_risk_profile(
        self,
        client_id: str
    ) -> dict:

        client_entries = self.audit_log.filter(
            client_id=client_id
        )

        warnings = sum(
            1
            for entry in client_entries
            if entry["level"] == AuditLevel.WARNING.name
        )

        critical = sum(
            1
            for entry in client_entries
            if entry["level"] == AuditLevel.CRITICAL.name
        )

        total_suspicious = warnings + critical

        if critical >= 2 or total_suspicious >= 5:
            overall_risk = RiskLevel.HIGH

        elif total_suspicious >= 2:
            overall_risk = RiskLevel.MEDIUM

        else:
            overall_risk = RiskLevel.LOW

        return {
            "client_id": client_id,
            "overall_risk": overall_risk.name,
            "total_audit_events": len(client_entries),
            "warning_events": warnings,
            "critical_events": critical
        }

    def error_statistics(self) -> dict:

        errors = self.audit_log.get_errors()

        statistics = {
            "total_errors": len(errors),
            "warnings": 0,
            "errors": 0,
            "critical": 0
        }

        for entry in errors:

            level = entry["level"]

            if level == AuditLevel.WARNING.name:
                statistics["warnings"] += 1

            elif level == AuditLevel.ERROR.name:
                statistics["errors"] += 1

            elif level == AuditLevel.CRITICAL.name:
                statistics["critical"] += 1

        return statistics

# ==============================================================
# DAY 7 — REPORT BUILDER
# ==============================================================

class ReportBuilder:
    """
    Generates reports and charts for the banking system.

    Supported reports:
    - Client report
    - Bank report
    - Risk report

    Supported formats:
    - Text
    - JSON
    - CSV

    Supported charts:
    - Pie chart
    - Bar chart
    - Balance movement line chart
    """

    def __init__(
        self,
        bank,
        transactions=None,
        audit_log=None,
        risk_analyzer=None,
        output_dir="reports"
    ):
        self.bank = bank
        self.transactions = transactions or []
        self.audit_log = audit_log
        self.risk_analyzer = risk_analyzer
        self.output_dir = output_dir

        project_dir = Path(__file__).resolve().parent  # folder containing this Python file
        output_dir = project_dir / self.output_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        # os.makedirs(
        #     self.output_dir,
        #     exist_ok=True
        # )

    # ==========================================================
    # CLIENT DATA
    # ==========================================================

    def _get_client_accounts(self, client_id):
        """
        Returns all accounts belonging to a client.
        """

        client = self.bank.clients.get(client_id)

        if client is None:
            raise ValueError(
                f"Client {client_id} does not exist."
            )

        account_ids = set(
            client.account_ids
        )

        return [
            account
            for account in self.bank.accounts.values()
            if account.account_id() in account_ids
        ]

    def _get_client_transactions(self, client_id):
        """
        Returns transactions involving a client.
        """

        accounts = self._get_client_accounts(
            client_id
        )

        account_ids = {
            account.account_id()
            for account in accounts
        }

        return [
            transaction
            for transaction in self.transactions
            if (
                transaction.sender in account_ids
                or transaction.receiver in account_ids
            )
        ]

    # ==========================================================
    # CLIENT REPORT
    # ==========================================================

    def build_client_report(
        self,
        client_id
    ):
        """
        Creates a structured client report.
        """

        client = self.bank.clients.get(
            client_id
        )

        if client is None:
            raise ValueError(
                f"Client {client_id} does not exist."
            )

        accounts = self._get_client_accounts(
            client_id
        )

        transactions = self._get_client_transactions(
            client_id
        )

        total_balance = sum(
            account.balance()
            for account in accounts
        )

        transaction_statistics = Counter(
            transaction.status.name
            for transaction in transactions
        )

        return {
            "report_type": "client",
            "generated_at": datetime.now().isoformat(),

            "client": {
                "id": client.client_id,
                "name": client.full_name,
                "status": (
                    client.status.name
                    if hasattr(client.status, "name")
                    else str(client.status)
                )
            },

            "accounts": [
                {
                    "account_id": account.account_id(),
                    "type": account.__class__.__name__,
                    "balance": account.balance(),
                    "currency": account.currency.value,
                    "status": account.status().name
                }
                for account in accounts
            ],

            "total_balance": total_balance,

            "transaction_statistics":
                dict(transaction_statistics),

            "transaction_count":
                len(transactions)
        }

    # ==========================================================
    # BANK REPORT
    # ==========================================================

    def build_bank_report(self):
        """
        Creates a structured report for the entire bank.
        """

        account_list = list(
            self.bank.accounts.values()
        )

        status_statistics = Counter(
            account.status().name
            for account in account_list
        )

        account_type_statistics = Counter(
            account.__class__.__name__
            for account in account_list
        )

        transaction_statistics = Counter(
            transaction.status.name
            for transaction in self.transactions
        )

        currency_statistics = defaultdict(float)

        for account in account_list:
            currency_statistics[
                account.currency.value
            ] += account.balance()

        return {
            "report_type": "bank",
            "generated_at": datetime.now().isoformat(),

            "bank": {
                "name": self.bank.name,
                "client_count": len(
                    self.bank.clients
                ),
                "account_count": len(
                    account_list
                )
            },

            "balances_by_currency":
                dict(currency_statistics),

            "account_statuses":
                dict(status_statistics),

            "account_types":
                dict(account_type_statistics),

            "transaction_statistics":
                dict(transaction_statistics),

            "total_transactions":
                len(self.transactions)
        }

    # ==========================================================
    # RISK REPORT
    # ==========================================================

    def build_risk_report(self):
        """
        Creates a structured risk report.
        """

        risk_statistics = Counter()

        suspicious_operations = []

        if self.audit_log is not None:

            for entry in self.audit_log.entries:

                level = entry["level"]

                if level in {
                    "WARNING",
                    "CRITICAL"
                }:
                    suspicious_operations.append(
                        entry
                    )

        # Analyze all transactions when a RiskAnalyzer exists.
        if self.risk_analyzer is not None:

            for transaction in self.transactions:

                result = self.risk_analyzer.analyze(
                    transaction
                )

                risk_statistics[
                    result["risk_level"].name
                ] += 1

        return {
            "report_type": "risk",
            "generated_at": datetime.now().isoformat(),

            "risk_statistics":
                dict(risk_statistics),

            "suspicious_operations":
                suspicious_operations,

            "blocked_transactions":
                len(
                    [
                        entry
                        for entry in suspicious_operations
                        if entry["event_type"]
                        == "TRANSACTION_BLOCKED"
                    ]
                )
        }

    # ==========================================================
    # TEXT REPORT
    # ==========================================================

    def build_text_report(
        self,
        report
    ):
        """
        Converts any structured report to readable text.
        """

        lines = []

        lines.append(
            "=" * 70
        )

        lines.append(
            f"REPORT TYPE: "
            f"{report.get('report_type', 'UNKNOWN').upper()}"
        )

        lines.append(
            f"Generated: "
            f"{report.get('generated_at', '')}"
        )

        lines.append(
            "=" * 70
        )

        def add_dict(
            data,
            indent=0
        ):

            for key, value in data.items():

                prefix = " " * indent

                if isinstance(value, dict):

                    lines.append(
                        f"{prefix}{key}:"
                    )

                    add_dict(
                        value,
                        indent + 4
                    )

                elif isinstance(value, list):

                    lines.append(
                        f"{prefix}{key}:"
                    )

                    for item in value:

                        if isinstance(
                            item,
                            dict
                        ):
                            add_dict(
                                item,
                                indent + 4
                            )

                        else:
                            lines.append(
                                f"{' ' * (indent + 4)}"
                                f"- {item}"
                            )

                else:

                    lines.append(
                        f"{prefix}{key}: "
                        f"{value}"
                    )

        add_dict(report)

        return "\n".join(lines)

    # ==========================================================
    # JSON EXPORT
    # ==========================================================

    def export_to_json(
        self,
        report,
        filename
    ):
        """
        Saves report as JSON.
        """

        project_dir = Path(__file__).resolve().parent
        path = project_dir / self.output_dir / filename

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                ensure_ascii=False,
                indent=4,
                default=str
            )

        return path

    # ==========================================================
    # CSV EXPORT
    # ==========================================================

    def export_to_csv(
        self,
        report,
        filename
    ):
        """
        Saves a structured report as CSV.

        Nested dictionaries/lists are converted to JSON strings
        so that the CSV remains readable and valid.
        """

        project_dir = Path(__file__).resolve().parent
        path = project_dir / self.output_dir / filename

        rows = []

        for key, value in report.items():

            if isinstance(
                value,
                (dict, list)
            ):
                value = json.dumps(
                    value,
                    ensure_ascii=False,
                    default=str
                )

            rows.append(
                {
                    "field": key,
                    "value": value
                }
            )

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "field",
                    "value"
                ]
            )

            writer.writeheader()

            writer.writerows(rows)

        return path

    # ==========================================================
    # PIE CHART
    # ==========================================================

    def create_pie_chart(
        self,
        data,
        title,
        filename
    ):
        """
        Creates a pie chart from:
            {"category": value}
        """

        labels = list(
            data.keys()
        )

        values = list(
            data.values()
        )

        if not values:
            raise ValueError(
                "Cannot create pie chart from empty data."
            )

        plt.figure(
            figsize=(8, 8)
        )

        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title(title)

        plt.tight_layout()

        project_dir = Path(__file__).resolve().parent
        path = project_dir / self.output_dir / filename

        plt.savefig(
            path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        return path

    # ==========================================================
    # BAR CHART
    # ==========================================================

    def create_bar_chart(
        self,
        data,
        title,
        xlabel,
        ylabel,
        filename
    ):
        """
        Creates a bar chart from:
            {"category": value}
        """

        labels = list(
            data.keys()
        )

        values = list(
            data.values()
        )

        if not values:
            raise ValueError(
                "Cannot create bar chart from empty data."
            )

        plt.figure(
            figsize=(10, 6)
        )

        plt.bar(
            labels,
            values
        )

        plt.title(title)

        plt.xlabel(
            xlabel
        )

        plt.ylabel(
            ylabel
        )

        plt.xticks(
            rotation=30,
            ha="right"
        )

        plt.tight_layout()

        project_dir = Path(__file__).resolve().parent
        path = project_dir / self.output_dir / filename

        plt.savefig(
            path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        return path

    # ==========================================================
    # BALANCE MOVEMENT LINE CHART
    # ==========================================================

    def create_balance_movement_chart(
        self,
        transactions,
        account_id,
        initial_balance,
        filename
    ):
        """
        Shows account balance movement over time.

        Only completed transactions affecting the selected
        account are included.
        """

        balance = initial_balance

        points = [
            {
                "time": datetime.now(),
                "balance": balance
            }
        ]

        sorted_transactions = sorted(
            transactions,
            key=lambda transaction:
                getattr(
                    transaction,
                    "created_at",
                    datetime.now()
                )
        )

        for transaction in sorted_transactions:

            if (
                transaction.status.name
                != "COMPLETED"
            ):
                continue

            timestamp = getattr(
                transaction,
                "created_at",
                datetime.now()
            )

            if transaction.sender == account_id:

                balance -= transaction.amount

            elif transaction.receiver == account_id:

                balance += transaction.amount

            else:

                continue

            points.append(
                {
                    "time": timestamp,
                    "balance": balance
                }
            )

        if len(points) < 2:
            raise ValueError(
                "Not enough transaction data "
                "to create a balance chart."
            )

        dates = [
            point["time"]
            for point in points
        ]

        balances = [
            point["balance"]
            for point in points
        ]

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            dates,
            balances,
            marker="o"
        )

        plt.title(
            f"Balance Movement — "
            f"Account {account_id}"
        )

        plt.xlabel(
            "Time"
        )

        plt.ylabel(
            "Balance"
        )

        plt.grid(
            True,
            alpha=0.3
        )

        plt.xticks(
            rotation=30
        )

        plt.tight_layout()

        project_dir = Path(__file__).resolve().parent
        path = project_dir / self.output_dir / filename

        plt.savefig(
            path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        return path

    # ==========================================================
    # SAVE CHARTS
    # ==========================================================

    def save_charts(
        self,
        bank_report,
        risk_report
    ):
        """
        Generates the main Day 7 charts.
        """

        chart_paths = []

        # ------------------------------------------------------
        # 1. Account type pie chart
        # ------------------------------------------------------

        account_types = (
            bank_report[
                "account_types"
            ]
        )

        if account_types:

            chart_paths.append(
                self.create_pie_chart(
                    data=account_types,
                    title="Accounts by Type",
                    filename="accounts_by_type.png"
                )
            )

        # ------------------------------------------------------
        # 2. Transaction status bar chart
        # ------------------------------------------------------

        transaction_statistics = (
            bank_report[
                "transaction_statistics"
            ]
        )

        if transaction_statistics:

            chart_paths.append(
                self.create_bar_chart(
                    data=transaction_statistics,
                    title="Transactions by Status",
                    xlabel="Status",
                    ylabel="Number of Transactions",
                    filename="transactions_by_status.png"
                )
            )

        # ------------------------------------------------------
        # 3. Risk distribution pie chart
        # ------------------------------------------------------

        risk_statistics = (
            risk_report[
                "risk_statistics"
            ]
        )

        if risk_statistics:

            chart_paths.append(
                self.create_pie_chart(
                    data=risk_statistics,
                    title="Transaction Risk Distribution",
                    filename="risk_distribution.png"
                )
            )

        return chart_paths