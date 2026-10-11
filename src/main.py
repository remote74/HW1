from utils import *

if __name__ == "__main__":
    ##############################
    ### Day 1
    ##############################
    print("STEP 1: Creating Active & Frozen Accounts")
    active_acc = BankAccount(name="John Doe", balance=1500.0, currency="USD")
    frozen_acc = BankAccount(name="Alice Smith", balance=250.0, currency="EUR")
    frozen_acc.freeze_account()

    print(active_acc)
    print(frozen_acc)
    print()

    print("--- STEP 2: Executing Valid Operations on Active Account ---")
    print(f"Initial: {active_acc}")
    active_acc.deposit(500)
    print(f"After Deposit: {active_acc}")
    active_acc.withdraw(200)
    print(f"After Withdrawal: {active_acc}")

    print()

    print("--- STEP 3: Attempting Operations on Frozen Account ---")
    try:
        frozen_acc.deposit(100)
    except AccountFrozenError as e:
        print(f"Caught expected error: {e}")

    try:
        frozen_acc.withdraw(50)
    except AccountFrozenError as e:
        print(f"Caught expected error: {e}")
    print()

    print("--- STEP 4: Triggering Bounds and Balance Violations ---")
    try:
        active_acc.withdraw(50000)
    except InsufficientFundsError as e:
        print(f"Caught expected error: {e}")

    try:
        active_acc.deposit(-100)
    except InvalidOperationError as e:
        print(f"Caught expected error: {e}")

# ============================================================
# Day 2
# ============================================================

    print("\n--- SAVINGS ACCOUNT ---")

    savings = SavingsAccount(
        name="Alice",
        balance=50000,
        currency="RUB",
        min_balance=10000,
        monthly_interest_rate=0.01
    )

    print(savings)

    savings.deposit(5000)
    print(f"After deposit: {savings}")

    interest = savings.apply_monthly_interest()
    print(f"Interest applied: {interest:.2f} RUB")
    print(savings)

    savings.withdraw(10000)
    print(f"After withdrawal: {savings}")


    print("\n--- PREMIUM ACCOUNT ---")

    premium = PremiumAccount(
        name="Bob",
        balance=5000,
        currency="USD",
        overdraft_limit=3000,
        transaction_limit=100000,
        fixed_fee=50
    )

    print(premium)

    premium.withdraw(7000)
    print(f"After overdraft withdrawal: {premium}")

    premium.deposit(3000)
    print(f"After deposit: {premium}")

    premium.charge_fixed_fee()
    print(f"After fixed fee: {premium}")


    print("\n--- INVESTMENT ACCOUNT ---")

    investment = InvestmentAccount(
        name="Charlie",
        balance=100000,
        currency="EUR"
    )

    print(investment)

    investment.invest("stocks", 40000)
    investment.invest("bonds", 30000)
    investment.invest("etf", 20000)

    print("Portfolio:", investment.portfolio)
    print(investment)

    growth_rates = {
        "stocks": 0.10,
        "bonds": 0.04,
        "etf": 0.07
    }

    expected_growth = investment.project_yearly_growth(growth_rates)

    print(
        f"Expected yearly portfolio growth: "
        f"{expected_growth:.2f} EUR"
    )


    print("\n--- POLYMORPHISM DEMONSTRATION ---")

    accounts = [
        SavingsAccount(
            name="Alice",
            balance=20000,
            min_balance=5000,
            monthly_interest_rate=0.01
        ),
        PremiumAccount(
            name="Bob",
            balance=10000,
            overdraft_limit=5000,
            fixed_fee=100
        ),
        InvestmentAccount(
            name="Charlie",
            balance=50000
        )
    ]

    for account in accounts:
        print(account)
        print(account.get_account_info())
        print()

# ==============================================================
# Day 3
# ==============================================================

    print("\n" + "=" * 60)
    print("DAY 3 — BANK SYSTEM DEMONSTRATION")
    print("=" * 60)


    # --------------------------------------------------------------
    # 1. Create bank
    # --------------------------------------------------------------

    bank = Bank("Educational Bank")

    print(bank)


    # --------------------------------------------------------------
    # 2. Create clients
    # --------------------------------------------------------------

    client_1 = Client(
        full_name="Alice Johnson",
        client_id="C001",
        age=25,
        contacts={
            "phone": "+123456789",
            "email": "alice@example.com"
        },
        password="alice123"
    )

    client_2 = Client(
        full_name="Bob Smith",
        client_id="C002",
        age=35,
        contacts={
            "phone": "+987654321",
            "email": "bob@example.com"
        },
        password="bob123"
    )

    client_3 = Client(
        full_name="Charlie Brown",
        client_id="C003",
        age=42,
        contacts={
            "phone": "+111222333",
            "email": "charlie@example.com"
        },
        password="charlie123"
    )


    bank.add_client(client_1)
    bank.add_client(client_2)
    bank.add_client(client_3)

    print("\nClients:")
    for client in bank.clients.values():
        print(client)


    # --------------------------------------------------------------
    # 3. Open different account types
    # --------------------------------------------------------------

    savings = bank.open_account(
        "C001",
        account_type=SavingsAccount,
        balance=50000,
        currency="RUB",
        min_balance=10000,
        monthly_interest_rate=0.01
    )

    premium = bank.open_account(
        "C002",
        account_type=PremiumAccount,
        balance=30000,
        currency="USD",
        overdraft_limit=5000,
        transaction_limit=100000,
        fixed_fee=100
    )

    investment = bank.open_account(
        "C003",
        account_type=InvestmentAccount,
        balance=100000,
        currency="EUR"
    )

    print("\nOpened accounts:")
    print(savings)
    print(premium)
    print(investment)


    # --------------------------------------------------------------
    # 4. Freeze / unfreeze account
    # --------------------------------------------------------------

    print("\nFreezing Alice's account...")

    bank.freeze_account(savings.account_id())

    print(savings)

    try:
        savings.deposit(1000)
    except AccountFrozenError as error:
        print("Expected error:", error)

    print("\nUnfreezing Alice's account...")

    bank.unfreeze_account(savings.account_id())

    savings.deposit(1000)

    print(savings)


    # --------------------------------------------------------------
    # 5. Authentication
    # --------------------------------------------------------------

    print("\nAuthentication test:")

    try:
        bank.authenticate_client(
            "C001",
            "wrong_password"
        )
    except InvalidOperationError as error:
        print(error)

    try:
        bank.authenticate_client(
            "C001",
            "wrong_password"
        )
    except InvalidOperationError as error:
        print(error)

    try:
        bank.authenticate_client(
            "C001",
            "wrong_password"
        )
    except InvalidOperationError as error:
        print(error)

    print(
        "Alice blocked:",
        client_1.is_blocked
    )


    # --------------------------------------------------------------
    # 6. Correct authentication for Bob
    # --------------------------------------------------------------

    print("\nBob authentication:")

    try:
        result = bank.authenticate_client(
            "C002",
            "bob123"
        )

        print("Authentication successful:", result)

    except InvalidOperationError as error:
        print("Authentication failed:", error)


    # --------------------------------------------------------------
    # 7. Search accounts
    # --------------------------------------------------------------

    print("\nAlice's accounts:")

    alice_accounts = bank.search_accounts(
        client_id="C001"
    )

    for account in alice_accounts:
        print(account)


    print("\nUSD accounts:")

    usd_accounts = bank.search_accounts(
        currency="USD"
    )

    for account in usd_accounts:
        print(account)


    # --------------------------------------------------------------
    # 8. Total balance
    # --------------------------------------------------------------

    print("\nTotal balance:")

    print(
        f"{bank.get_total_balance():.2f}"
    )


    # --------------------------------------------------------------
    # 9. Client ranking
    # --------------------------------------------------------------

    print("\nClients ranking:")

    ranking = bank.get_clients_ranking()

    for position, client_data in enumerate(
        ranking,
        start=1
    ):
        print(
            f"{position}. "
            f"{client_data['name']} — "
            f"{client_data['total_balance']:.2f}"
        )


    # --------------------------------------------------------------
    # 10. Suspicious actions
    # --------------------------------------------------------------

    print("\nAlice's suspicious actions:")

    for action in client_1.suspicious_actions:
        print(
            f"- {action['action']} "
            f"at {action['timestamp']}"
        )


    # --------------------------------------------------------------
    # 11. Night-time restriction demonstration
    # --------------------------------------------------------------

    print("\nNight-time restriction test:")

    from datetime import time

    try:
        bank._check_operation_time(
            current_time=time(2, 30)
        )
    except InvalidOperationError as error:
        print("Expected error:", error)

    print("\nDay 3 demonstration completed.")

# ==============================================================
# Day 4
# ==============================================================

    print("\n" + "=" * 70)
    print("DAY 4 — TRANSACTION SYSTEM")
    print("=" * 70)


    # --------------------------------------------------------------
    # 1. Create bank and clients
    # --------------------------------------------------------------

    bank = Bank("Transaction Bank")

    client_1 = Client(
        full_name="Alice Johnson",
        client_id="C001",
        age=25,
        contacts={"email": "alice@example.com"},
        password="alice123"
    )

    client_2 = Client(
        full_name="Bob Smith",
        client_id="C002",
        age=35,
        contacts={"email": "bob@example.com"},
        password="bob123"
    )

    client_3 = Client(
        full_name="Charlie Brown",
        client_id="C003",
        age=40,
        contacts={"email": "charlie@example.com"},
        password="charlie123"
    )

    bank.add_client(client_1)
    bank.add_client(client_2)
    bank.add_client(client_3)


    # --------------------------------------------------------------
    # 2. Create accounts
    # --------------------------------------------------------------

    alice_account = bank.open_account(
        "C001",
        account_type=BankAccount,
        balance=100000,
        currency="RUB"
    )

    bob_account = bank.open_account(
        "C002",
        account_type=PremiumAccount,
        balance=50000,
        currency="USD",
        overdraft_limit=10000,
        transaction_limit=100000,
        fixed_fee=100
    )

    charlie_account = bank.open_account(
        "C003",
        account_type=BankAccount,
        balance=50000,
        currency="EUR"
    )

    print("\nAccounts:")
    print(alice_account)
    print(bob_account)
    print(charlie_account)


    # --------------------------------------------------------------
    # 3. Exchange rates
    # --------------------------------------------------------------

    exchange_rates = {
        ("RUB", "USD"): 0.011,
        ("USD", "RUB"): 90.0,

        ("RUB", "EUR"): 0.010,
        ("EUR", "RUB"): 100.0,

        ("USD", "EUR"): 0.92,
        ("EUR", "USD"): 1.09
    }


    processor = TransactionProcessor(
        bank=bank,
        exchange_rates=exchange_rates,
        external_transfer_fee=0.02,
        max_retries=2
    )


    # --------------------------------------------------------------
    # 4. Create transaction queue
    # --------------------------------------------------------------

    queue = TransactionQueue()


    # --------------------------------------------------------------
    # 5. Create 10 transactions
    # --------------------------------------------------------------

    transactions = [

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=5000,
            currency="RUB",
            sender=alice_account.account_id(),
            receiver=bob_account.account_id(),
            priority=2
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=3000,
            currency="USD",
            sender=bob_account.account_id(),
            receiver=alice_account.account_id(),
            priority=1
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=10000,
            currency="RUB",
            sender=alice_account.account_id(),
            receiver=charlie_account.account_id(),
            priority=3
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=2000,
            currency="EUR",
            sender=charlie_account.account_id(),
            receiver=bob_account.account_id(),
            priority=2
        ),

        Transaction(
            transaction_type=TransactionType.EXTERNAL_TRANSFER,
            amount=1000,
            currency="USD",
            sender=bob_account.account_id(),
            receiver=alice_account.account_id(),
            priority=4
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=1500,
            currency="RUB",
            sender=alice_account.account_id(),
            receiver=bob_account.account_id(),
            priority=5
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=7000,
            currency="EUR",
            sender=charlie_account.account_id(),
            receiver=alice_account.account_id(),
            priority=3
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=2500,
            currency="USD",
            sender=bob_account.account_id(),
            receiver=charlie_account.account_id(),
            priority=1
        ),

        Transaction(
            transaction_type=TransactionType.EXTERNAL_TRANSFER,
            amount=800,
            currency="RUB",
            sender=alice_account.account_id(),
            receiver=charlie_account.account_id(),
            priority=4
        ),

        Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=4000,
            currency="EUR",
            sender=charlie_account.account_id(),
            receiver=bob_account.account_id(),
            priority=5
        )
    ]


    # --------------------------------------------------------------
    # 6. Add all transactions to queue
    # --------------------------------------------------------------

    for transaction in transactions:
        queue.add(transaction)

    print(
        f"\nTransactions added to queue: {len(queue)}"
    )


    # --------------------------------------------------------------
    # 7. Delayed transaction demonstration
    # --------------------------------------------------------------

    delayed_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=1000,
        currency="RUB",
        sender=alice_account.account_id(),
        receiver=bob_account.account_id(),
        priority=1,
        scheduled_at=datetime.now() + timedelta(hours=1)
    )

    queue.add(delayed_transaction)

    print(
        "Delayed transaction scheduled for:",
        delayed_transaction.scheduled_at
    )


    # --------------------------------------------------------------
    # 8. Cancel a transaction
    # --------------------------------------------------------------

    cancelled_transaction = transactions[-1]

    queue.cancel(
        cancelled_transaction.transaction_id
    )

    print(
        "Cancelled transaction:",
        cancelled_transaction.transaction_id
    )


    # --------------------------------------------------------------
    # 9. Process transactions
    # --------------------------------------------------------------

    print("\nProcessing queue...")

    results = processor.process_queue(queue)

    for result in results:
        print(result)


    # --------------------------------------------------------------
    # 10. Final account balances
    # --------------------------------------------------------------

    print("\nFinal balances:")

    print(alice_account)
    print(bob_account)
    print(charlie_account)


    # --------------------------------------------------------------
    # 11. Transaction statistics
    # --------------------------------------------------------------

    print("\nTransaction results:")

    for transaction in transactions:
        print(
            f"{transaction.transaction_id}: "
            f"{transaction.status.name} | "
            f"Retries: {transaction.retry_count} | "
            f"Fee: {transaction.fee:.2f}"
        )


    # --------------------------------------------------------------
    # 12. Error log
    # --------------------------------------------------------------

    print("\nProcessor error log:")

    for error in processor.error_log:
        print(error)


    print("\nDay 4 demonstration completed.")
    # ==============================================================
    # DAY 5 DEMONSTRATION
    # ==============================================================

    print("\n" + "=" * 70)
    print("DAY 5 — AUDIT AND RISK ANALYSIS")
    print("=" * 70)


    # --------------------------------------------------------------
    # 1. Create bank
    # --------------------------------------------------------------

    bank = Bank("Secure Educational Bank")


    # --------------------------------------------------------------
    # 2. Create clients
    # --------------------------------------------------------------

    alice = Client(
        full_name="Alice Johnson",
        client_id="C001",
        age=25,
        contacts={"email": "alice@example.com"},
        password="alice123"
    )

    bob = Client(
        full_name="Bob Smith",
        client_id="C002",
        age=35,
        contacts={"email": "bob@example.com"},
        password="bob123"
    )

    charlie = Client(
        full_name="Charlie Brown",
        client_id="C003",
        age=40,
        contacts={"email": "charlie@example.com"},
        password="charlie123"
    )

    bank.add_client(alice)
    bank.add_client(bob)
    bank.add_client(charlie)


    # --------------------------------------------------------------
    # 3. Open accounts
    # --------------------------------------------------------------

    alice_account = bank.open_account(
        "C001",
        account_type=BankAccount,
        balance=150000,
        currency="RUB"
    )

    bob_account = bank.open_account(
        "C002",
        account_type=BankAccount,
        balance=100000,
        currency="RUB"
    )

    charlie_account = bank.open_account(
        "C003",
        account_type=PremiumAccount,
        balance=200000,
        currency="RUB",
        overdraft_limit=50000,
        transaction_limit=500000,
        fixed_fee=100
    )


    # --------------------------------------------------------------
    # 4. Create audit and risk system
    # --------------------------------------------------------------

    audit_log = AuditLog(
        file_path="day5_audit.log"
    )

    risk_analyzer = RiskAnalyzer(
        large_amount_threshold=50000,
        frequent_operations_threshold=5,
        frequent_operations_window_minutes=10
    )

    security = BankSecurityController(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer
    )

    reporter = AuditReporter(
        audit_log=audit_log,
        risk_analyzer=risk_analyzer
    )


    # --------------------------------------------------------------
    # Helper function
    # --------------------------------------------------------------

    def test_transaction(
        transaction,
        timestamp=None
    ):
        print("\nTransaction:")
        print(transaction)

        result = security.check_transaction(
            transaction,
            timestamp=timestamp
        )

        print(
            "Risk:",
            result["risk_level"].name
        )

        print(
            "Indicators:",
            result["indicators"]
        )

        print(
            "Blocked:",
            result["blocked"]
        )

        if not result["blocked"]:
            security.record_successful_transaction(
                transaction
            )

        return result


    # --------------------------------------------------------------
    # 5. Normal transaction
    # --------------------------------------------------------------

    normal_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=1000,
        currency="RUB",
        sender=alice_account.account_id(),
        receiver=bob_account.account_id()
    )

    test_transaction(
        normal_transaction,
        timestamp=datetime(2026, 10, 8, 14, 0)
    )


    # --------------------------------------------------------------
    # 6. Large amount transaction
    # --------------------------------------------------------------

    large_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=100000,
        currency="RUB",
        sender=alice_account.account_id(),
        receiver=bob_account.account_id()
    )

    test_transaction(
        large_transaction,
        timestamp=datetime(2026, 10, 8, 14, 30)
    )


    # --------------------------------------------------------------
    # 7. New receiver transaction
    # --------------------------------------------------------------

    new_receiver_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=2000,
        currency="RUB",
        sender=bob_account.account_id(),
        receiver=charlie_account.account_id()
    )

    test_transaction(
        new_receiver_transaction,
        timestamp=datetime(2026, 10, 8, 15, 0)
    )


    # --------------------------------------------------------------
    # 8. Night-time transaction
    # --------------------------------------------------------------

    night_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=3000,
        currency="RUB",
        sender=alice_account.account_id(),
        receiver=bob_account.account_id()
    )

    test_transaction(
        night_transaction,
        timestamp=datetime(2026, 10, 9, 2, 30)
    )


    # --------------------------------------------------------------
    # 9. Frequent operations
    # --------------------------------------------------------------

    print("\nFrequent operations test:")

    for i in range(6):

        frequent_transaction = Transaction(
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=500,
            currency="RUB",
            sender=alice_account.account_id(),
            receiver=bob_account.account_id()
        )

        result = test_transaction(
            frequent_transaction,
            timestamp=datetime(
                2026,
                10,
                8,
                16,
                i
            )
        )


    # --------------------------------------------------------------
    # 10. HIGH-RISK transaction
    # --------------------------------------------------------------

    high_risk_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=100000,
        currency="RUB",
        sender=alice_account.account_id(),
        receiver=charlie_account.account_id()
    )

    high_risk_result = test_transaction(
        high_risk_transaction,
        timestamp=datetime(
            2026,
            10,
            9,
            2,
            30
        )
    )


    # --------------------------------------------------------------
    # 11. Suspicious operations report
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("SUSPICIOUS OPERATIONS REPORT")
    print("=" * 70)

    suspicious_operations = (
        reporter.suspicious_operations_report()
    )

    for entry in suspicious_operations:
        print(
            f"{entry['timestamp']} | "
            f"{entry['level']} | "
            f"{entry['event_type']} | "
            f"{entry['message']}"
        )


    # --------------------------------------------------------------
    # 12. Client risk profiles
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("CLIENT RISK PROFILES")
    print("=" * 70)

    for client in bank.clients.values():

        profile = reporter.client_risk_profile(
            client.client_id
        )

        print(profile)


    # --------------------------------------------------------------
    # 13. Error statistics
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("ERROR STATISTICS")
    print("=" * 70)

    print(
        reporter.error_statistics()
    )


    # --------------------------------------------------------------
    # 14. Audit filtering
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("CRITICAL AUDIT EVENTS")
    print("=" * 70)

    critical_events = audit_log.filter(
        level=AuditLevel.CRITICAL
    )

    for entry in critical_events:
        print(entry)


    print("\nDay 5 demonstration completed.")

    # ==============================================================
    # DAY 6 — DEMONSTRATION PROGRAM
    # ==============================================================


    print("\n" + "=" * 80)
    print("DAY 6 — COMPLETE BANKING SYSTEM DEMONSTRATION")
    print("=" * 80)


    # ==============================================================
    # 1. INITIALIZATION
    # ==============================================================

    bank = Bank("Demo National Bank")

    print("\n[1] Bank created:")
    print(bank)


    # ==============================================================
    # 2. CREATE 7 CLIENTS
    # ==============================================================

    clients_data = [
        (
            "Alice Johnson",
            "C001",
            25,
            "alice@example.com",
            "alice123"
        ),
        (
            "Bob Smith",
            "C002",
            35,
            "bob@example.com",
            "bob123"
        ),
        (
            "Charlie Brown",
            "C003",
            42,
            "charlie@example.com",
            "charlie123"
        ),
        (
            "Diana Wilson",
            "C004",
            29,
            "diana@example.com",
            "diana123"
        ),
        (
            "Edward Davis",
            "C005",
            51,
            "edward@example.com",
            "edward123"
        ),
        (
            "Fiona Miller",
            "C006",
            31,
            "fiona@example.com",
            "fiona123"
        ),
        (
            "George Taylor",
            "C007",
            46,
            "george@example.com",
            "george123"
        )
    ]


    for full_name, client_id, age, email, password in clients_data:

        client = Client(
            full_name=full_name,
            client_id=client_id,
            age=age,
            contacts={"email": email},
            password=password
        )

        bank.add_client(client)


    print("\n[2] Clients created:", len(bank.clients))

    for client in bank.clients.values():
        print(
            f"  {client.client_id} | "
            f"{client.full_name}"
        )


    # ==============================================================
    # 3. CREATE 12 ACCOUNTS
    # ==============================================================

    accounts = []


    # Alice — Savings
    accounts.append(
        bank.open_account(
            "C001",
            account_type=SavingsAccount,
            balance=120000,
            currency="RUB",
            min_balance=10000,
            monthly_interest_rate=0.01
        )
    )


    # Alice — regular account
    accounts.append(
        bank.open_account(
            "C001",
            account_type=BankAccount,
            balance=30000,
            currency="RUB"
        )
    )


    # Bob — Premium
    accounts.append(
        bank.open_account(
            "C002",
            account_type=PremiumAccount,
            balance=150000,
            currency="RUB",
            overdraft_limit=30000,
            transaction_limit=500000,
            fixed_fee=500
        )
    )


    # Bob — USD account
    accounts.append(
        bank.open_account(
            "C002",
            account_type=BankAccount,
            balance=5000,
            currency="USD"
        )
    )


    # Charlie — Investment
    accounts.append(
        bank.open_account(
            "C003",
            account_type=InvestmentAccount,
            balance=200000,
            currency="EUR"
        )
    )


    # Charlie — regular
    accounts.append(
        bank.open_account(
            "C003",
            account_type=BankAccount,
            balance=50000,
            currency="RUB"
        )
    )


    # Diana — Savings
    accounts.append(
        bank.open_account(
            "C004",
            account_type=SavingsAccount,
            balance=90000,
            currency="RUB",
            min_balance=15000,
            monthly_interest_rate=0.015
        )
    )


    # Edward — Premium
    accounts.append(
        bank.open_account(
            "C005",
            account_type=PremiumAccount,
            balance=250000,
            currency="USD",
            overdraft_limit=50000,
            transaction_limit=1000000,
            fixed_fee=1000
        )
    )


    # Fiona — regular
    accounts.append(
        bank.open_account(
            "C006",
            account_type=BankAccount,
            balance=70000,
            currency="EUR"
        )
    )


    # Fiona — savings
    accounts.append(
        bank.open_account(
            "C006",
            account_type=SavingsAccount,
            balance=60000,
            currency="RUB",
            min_balance=10000,
            monthly_interest_rate=0.01
        )
    )


    # George — regular
    accounts.append(
        bank.open_account(
            "C007",
            account_type=BankAccount,
            balance=100000,
            currency="RUB"
        )
    )


    # George — investment
    accounts.append(
        bank.open_account(
            "C007",
            account_type=InvestmentAccount,
            balance=150000,
            currency="USD"
        )
    )


    print("\n[3] Accounts created:", len(accounts))

    for account in accounts:
        print(" ", account)


    # ==============================================================
    # 4. INVESTMENT PORTFOLIOS
    # ==============================================================

    investment_accounts = [
        account
        for account in accounts
        if isinstance(account, InvestmentAccount)
    ]


    investment_accounts[0].invest(
        "stocks",
        60000
    )

    investment_accounts[0].invest(
        "bonds",
        30000
    )

    investment_accounts[0].invest(
        "etf",
        20000
    )


    investment_accounts[1].invest(
        "stocks",
        50000
    )

    investment_accounts[1].invest(
        "bonds",
        25000
    )

    investment_accounts[1].invest(
        "etf",
        20000
    )


    print("\nInvestment portfolios initialized.")


    # ==============================================================
    # 5. AUDIT + RISK SYSTEM
    # ==============================================================

    audit_log = AuditLog(
        file_path="day6_audit.log"
    )

    risk_analyzer = RiskAnalyzer(
        large_amount_threshold=50000,
        frequent_operations_threshold=5,
        frequent_operations_window_minutes=10
    )

    security = BankSecurityController(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer
    )

    reporter = AuditReporter(
        audit_log=audit_log,
        risk_analyzer=risk_analyzer
    )


    # ==============================================================
    # 6. CURRENCY RATES
    # ==============================================================

    exchange_rates = {
        ("RUB", "USD"): 0.011,
        ("USD", "RUB"): 90.0,

        ("RUB", "EUR"): 0.010,
        ("EUR", "RUB"): 100.0,

        ("USD", "EUR"): 0.92,
        ("EUR", "USD"): 1.09
    }


    processor = TransactionProcessor(
        bank=bank,
        exchange_rates=exchange_rates,
        external_transfer_fee=0.02,
        max_retries=2
    )


    queue = TransactionQueue()


    # ==============================================================
    # 7. TRANSACTION HISTORY
    # ==============================================================

    transaction_history = []


    def add_transaction_to_queue(
        transaction: Transaction
    ):
        """
        Adds transaction to the global history and queue.
        """

        transaction_history.append(transaction)

        queue.add(transaction)

        print(
            f"[QUEUE] Added: "
            f"{transaction.transaction_id} | "
            f"{transaction.transaction_type.name} | "
            f"{transaction.amount:.2f} "
            f"{transaction.currency.value}"
        )


    # ==============================================================
    # 8. HELPER FOR RANDOM ACCOUNTS
    # ==============================================================

    def get_random_account(
        exclude_id=None
    ):
        available = [
            account
            for account in accounts
            if account.account_id() != exclude_id
            and account.status() == AccountStatus.ACTIVE
        ]

        return random.choice(available)


    # ==============================================================
    # 9. CREATE 40 TRANSACTIONS
    # ==============================================================

    print("\n" + "=" * 80)
    print("[4] CREATING 40 TRANSACTIONS")
    print("=" * 80)


    random.seed(42)


    for i in range(40):

        sender = random.choice(accounts)

        receiver = get_random_account(
            exclude_id=sender.account_id()
        )

        # ----------------------------------------------------------
        # Most transactions are normal.
        # Some are deliberately suspicious/invalid.
        # ----------------------------------------------------------

        if i < 30:

            # Normal range
            amount = random.randint(
                500,
                10000
            )

        elif i < 34:

            # Large amount → suspicious
            amount = random.randint(
                60000,
                100000
            )

        elif i < 37:

            # Large amount + potential risk
            amount = random.randint(
                80000,
                150000
            )

        else:

            # Deliberately too large
            amount = 1000000

        transaction_type = (
            TransactionType.EXTERNAL_TRANSFER
            if i % 7 == 0
            else TransactionType.INTERNAL_TRANSFER
        )

        transaction = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            currency=sender.currency.value,
            sender=sender.account_id(),
            receiver=receiver.account_id(),
            priority=random.randint(1, 5)
        )

        # ----------------------------------------------------------
        # Add some delayed transactions.
        # ----------------------------------------------------------

        if i in (10, 20, 30):

            transaction.scheduled_at = (
                datetime.now()
                + timedelta(hours=1)
            )

        add_transaction_to_queue(
            transaction
        )


    print(
        f"\nTotal transactions created: "
        f"{len(transaction_history)}"
    )


    # ==============================================================
    # 10. ADD DELIBERATELY INVALID TRANSACTIONS
    # ==============================================================

    print("\n[5] Adding deliberately invalid transactions...")


    # Insufficient funds
    poor_account = BankAccount(
        name="Temporary",
        balance=10,
        currency="RUB"
    )

    bank.accounts[
        poor_account.account_id()
    ] = poor_account


    invalid_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=100000,
        currency="RUB",
        sender=poor_account.account_id(),
        receiver=accounts[0].account_id(),
        priority=1
    )

    transaction_history.append(
        invalid_transaction
    )

    queue.add(
        invalid_transaction
    )

    print(
        f"[QUEUE] Invalid transaction added: "
        f"{invalid_transaction.transaction_id}"
    )


    # ==============================================================
    # 11. FREEZE AN ACCOUNT
    # ==============================================================

    frozen_account = accounts[3]

    bank.freeze_account(
        frozen_account.account_id()
    )

    print(
        "\n[SECURITY] Account frozen:",
        frozen_account.account_id()
    )


    # Create transaction from frozen account
    frozen_transaction = Transaction(
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=1000,
        currency=frozen_account.currency.value,
        sender=frozen_account.account_id(),
        receiver=accounts[0].account_id(),
        priority=1
    )

    transaction_history.append(
        frozen_transaction
    )

    queue.add(
        frozen_transaction
    )

    print(
        f"[QUEUE] Transaction from frozen account: "
        f"{frozen_transaction.transaction_id}"
    )


    # ==============================================================
    # 12. TRANSACTION PROCESSING WITH RISK CHECK
    # ==============================================================

    print("\n" + "=" * 80)
    print("[6] PROCESSING TRANSACTIONS")
    print("=" * 80)


    processed_count = 0
    completed_count = 0
    failed_count = 0
    blocked_count = 0
    cancelled_count = 0


    while True:

        transaction = queue.get_next()

        if transaction is None:
            break

        processed_count += 1

        print(
            f"\n[PROCESSING] "
            f"{transaction.transaction_id}"
        )

        # ----------------------------------------------------------
        # Risk analysis BEFORE financial processing
        # ----------------------------------------------------------

        risk_result = security.check_transaction(
            transaction
        )

        print(
            f"  Risk: "
            f"{risk_result['risk_level'].name}"
        )

        print(
            f"  Indicators: "
            f"{risk_result['indicators']}"
        )

        # ----------------------------------------------------------
        # HIGH RISK → BLOCK
        # ----------------------------------------------------------

        if risk_result["blocked"]:

            blocked_count += 1

            print(
                "  [BLOCKED] "
                "Transaction rejected by risk system."
            )

            continue

        # ----------------------------------------------------------
        # Normal processing
        # ----------------------------------------------------------

        success = processor.process_with_retry(
            transaction
        )

        if success:

            completed_count += 1

            security.record_successful_transaction(
                transaction
            )

            print(
                "  [EXECUTED] "
                "Transaction completed successfully."
            )

        else:

            failed_count += 1

            print(
                "  [FAILED] "
                "Transaction execution failed."
            )


    # ==============================================================
    # 13. TRANSACTION PROCESSING SUMMARY
    # ==============================================================

    print("\n" + "=" * 80)
    print("[7] TRANSACTION PROCESSING SUMMARY")
    print("=" * 80)

    print(
        f"Processed:   {processed_count}"
    )

    print(
        f"Completed:   {completed_count}"
    )

    print(
        f"Failed:      {failed_count}"
    )

    print(
        f"Blocked:     {blocked_count}"
    )

    print(
        f"Cancelled:   {cancelled_count}"
    )


    # ==============================================================
    # 14. CUSTOMER ACCOUNTS
    # ==============================================================

    print("\n" + "=" * 80)
    print("[8] CUSTOMER ACCOUNT INFORMATION")
    print("=" * 80)


    def show_client_accounts(
        client_id: str
    ):

        client = bank.get_client(
            client_id
        )

        print(
            f"\nClient: "
            f"{client.full_name}"
        )

        print(
            f"Client ID: "
            f"{client.client_id}"
        )

        print(
            f"Status: "
            f"{client.status}"
        )

        print("Accounts:")

        client_accounts = bank.search_accounts(
            client_id=client_id
        )

        for account in client_accounts:
            print(
                f"  {account}"
            )


    # Show several customer scenarios
    show_client_accounts("C001")
    show_client_accounts("C002")
    show_client_accounts("C003")


    # ==============================================================
    # 15. TRANSACTION HISTORY FOR A CLIENT
    # ==============================================================

    print("\n" + "=" * 80)
    print("[9] TRANSACTION HISTORY")
    print("=" * 80)


    def get_client_transaction_history(
        client_id: str
    ):

        client = bank.get_client(
            client_id
        )

        account_ids = set(
            client.account_ids
        )

        history = []

        for transaction in transaction_history:

            if (
                transaction.sender in account_ids
                or transaction.receiver in account_ids
            ):
                history.append(
                    transaction
                )

        return history


    alice_history = get_client_transaction_history(
        "C001"
    )

    print(
        f"\nTransaction history for "
        f"{bank.clients['C001'].full_name}:"
    )

    for transaction in alice_history:

        print(
            f"  {transaction.transaction_id} | "
            f"{transaction.transaction_type.name} | "
            f"{transaction.amount:.2f} "
            f"{transaction.currency.value} | "
            f"{transaction.status.name}"
        )


    # ==============================================================
    # 16. SUSPICIOUS OPERATIONS
    # ==============================================================

    print("\n" + "=" * 80)
    print("[10] SUSPICIOUS OPERATIONS")
    print("=" * 80)


    suspicious_operations = (
        reporter.suspicious_operations_report()
    )


    if suspicious_operations:

        for entry in suspicious_operations:

            print(
                f"{entry['timestamp']} | "
                f"{entry['level']} | "
                f"{entry['event_type']} | "
                f"Client: {entry['client_id']} | "
                f"Transaction: "
                f"{entry['transaction_id']}"
            )

            print(
                f"  {entry['message']}"
            )

    else:

        print(
            "No suspicious operations found."
        )


    # ==============================================================
    # 17. CLIENT RISK PROFILES
    # ==============================================================

    print("\n" + "=" * 80)
    print("[11] CLIENT RISK PROFILES")
    print("=" * 80)


    for client in bank.clients.values():

        profile = reporter.client_risk_profile(
            client.client_id
        )

        print(
            f"{client.client_id} | "
            f"{client.full_name} | "
            f"Risk: {profile['overall_risk']} | "
            f"Warnings: {profile['warning_events']} | "
            f"Critical: {profile['critical_events']}"
        )


    # ==============================================================
    # 18. TOP 3 CLIENTS
    # ==============================================================

    print("\n" + "=" * 80)
    print("[12] TOP 3 CLIENTS BY BALANCE")
    print("=" * 80)


    ranking = bank.get_clients_ranking()


    for position, client_data in enumerate(
        ranking[:3],
        start=1
    ):

        print(
            f"{position}. "
            f"{client_data['name']} — "
            f"{client_data['total_balance']:.2f}"
        )


    # ==============================================================
    # 19. TRANSACTION STATISTICS
    # ==============================================================

    print("\n" + "=" * 80)
    print("[13] TRANSACTION STATISTICS")
    print("=" * 80)


    total_transactions = len(
        transaction_history
    )

    completed_transactions = sum(
        1
        for transaction in transaction_history
        if transaction.status
        == TransactionStatus.COMPLETED
    )

    failed_transactions = sum(
        1
        for transaction in transaction_history
        if transaction.status
        == TransactionStatus.FAILED
    )

    cancelled_transactions = sum(
        1
        for transaction in transaction_history
        if transaction.status
        == TransactionStatus.CANCELLED
    )


    print(
        f"Total transactions:     "
        f"{total_transactions}"
    )

    print(
        f"Completed:              "
        f"{completed_transactions}"
    )

    print(
        f"Failed:                 "
        f"{failed_transactions}"
    )

    print(
        f"Cancelled:              "
        f"{cancelled_transactions}"
    )

    print(
        f"Blocked by risk system: "
        f"{len(security.blocked_transactions)}"
    )


    # ==============================================================
    # 20. TRANSACTION ERROR STATISTICS
    # ==============================================================

    print("\n" + "=" * 80)
    print("[14] ERROR STATISTICS")
    print("=" * 80)


    error_statistics = (
        reporter.error_statistics()
    )

    print(
        f"Total audit errors: "
        f"{error_statistics['total_errors']}"
    )

    print(
        f"Warnings: "
        f"{error_statistics['warnings']}"
    )

    print(
        f"Errors: "
        f"{error_statistics['errors']}"
    )

    print(
        f"Critical: "
        f"{error_statistics['critical']}"
    )


    # ==============================================================
    # 21. TOTAL BANK BALANCE
    # ==============================================================

    print("\n" + "=" * 80)
    print("[15] TOTAL BANK BALANCE")
    print("=" * 80)


    total_balance = bank.get_total_balance()

    print(
        f"Total balance: "
        f"{total_balance:.2f}"
    )


    # ==============================================================
    # 22. FINAL ACCOUNT STATE
    # ==============================================================

    print("\n" + "=" * 80)
    print("[16] FINAL ACCOUNT STATE")
    print("=" * 80)


    for account in accounts:

        print(
            account
        )


    # ==============================================================
    # 23. AUDIT LOG SUMMARY
    # ==============================================================

    print("\n" + "=" * 80)
    print("[17] AUDIT LOG SUMMARY")
    print("=" * 80)


    print(
        f"Total audit entries: "
        f"{len(audit_log.entries)}"
    )

    print(
        f"Audit file: "
        f"{audit_log.file_path}"
    )


    print("\n" + "=" * 80)
    print("DAY 6 DEMONSTRATION COMPLETED")
    print("=" * 80)


    # ==============================================================
    # DAY 7 DEMONSTRATION
    # ==============================================================

    print("\n" + "=" * 80)
    print("DAY 7 — REPORTING AND VISUALIZATION")
    print("=" * 80)


    # ==============================================================
    # 1. Create ReportBuilder
    # ==============================================================

    report_builder = ReportBuilder(
        bank=bank,
        transactions=transaction_history,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer,
        output_dir="reports"
    )


    # ==============================================================
    # 2. CLIENT REPORT
    # ==============================================================

    print("\n[1] CLIENT REPORT")
    print("-" * 80)


    client_report = (
        report_builder.build_client_report(
            "C001"
        )
    )

    print(
        report_builder.build_text_report(
            client_report
        )
    )


    # ==============================================================
    # 3. BANK REPORT
    # ==============================================================

    print("\n[2] BANK REPORT")
    print("-" * 80)


    bank_report = (
        report_builder.build_bank_report()
    )

    print(
        report_builder.build_text_report(
            bank_report
        )
    )


    # ==============================================================
    # 4. RISK REPORT
    # ==============================================================

    print("\n[3] RISK REPORT")
    print("-" * 80)


    risk_report = (
        report_builder.build_risk_report()
    )

    print(
        report_builder.build_text_report(
            risk_report
        )
    )


    # ==============================================================
    # 5. JSON EXPORT
    # ==============================================================

    print("\n[4] JSON EXPORT")
    print("-" * 80)


    client_json = (
        report_builder.export_to_json(
            client_report,
            "client_C001_report.json"
        )
    )

    bank_json = (
        report_builder.export_to_json(
            bank_report,
            "bank_report.json"
        )
    )

    risk_json = (
        report_builder.export_to_json(
            risk_report,
            "risk_report.json"
        )
    )


    print(
        "Client report:",
        client_json
    )

    print(
        "Bank report:",
        bank_json
    )

    print(
        "Risk report:",
        risk_json
    )


    # ==============================================================
    # 6. CSV EXPORT
    # ==============================================================

    print("\n[5] CSV EXPORT")
    print("-" * 80)


    client_csv = (
        report_builder.export_to_csv(
            client_report,
            "client_C001_report.csv"
        )
    )

    bank_csv = (
        report_builder.export_to_csv(
            bank_report,
            "bank_report.csv"
        )
    )

    risk_csv = (
        report_builder.export_to_csv(
            risk_report,
            "risk_report.csv"
        )
    )


    print(
        "Client CSV:",
        client_csv
    )

    print(
        "Bank CSV:",
        bank_csv
    )

    print(
        "Risk CSV:",
        risk_csv
    )


    # ==============================================================
    # 7. SAVE CHARTS
    # ==============================================================

    print("\n[6] CHART GENERATION")
    print("-" * 80)


    chart_paths = (
        report_builder.save_charts(
            bank_report,
            risk_report
        )
    )


    for path in chart_paths:

        print(
            "Chart saved:",
            path
        )


    # ==============================================================
    # 8. BALANCE MOVEMENT CHART
    # ==============================================================

    print("\n[7] BALANCE MOVEMENT CHART")
    print("-" * 80)


    # Select the first account.
    selected_account = accounts[0]

    try:

        balance_chart = (
            report_builder.create_balance_movement_chart(
                transactions=transaction_history,
                account_id=selected_account.account_id(),
                initial_balance=selected_account.balance(),
                filename="balance_movement.png"
            )
        )

        print(
            "Balance chart saved:",
            balance_chart
        )

    except ValueError as error:

        print(
            "Could not create balance chart:",
            error
        )


    # ==============================================================
    # 9. FINAL SUMMARY
    # ==============================================================

    print("\n" + "=" * 80)
    print("DAY 7 SUMMARY")
    print("=" * 80)

    print(
        "Reports generated:"
    )

    print(
        "  - Client report"
    )

    print(
        "  - Bank report"
    )

    print(
        "  - Risk report"
    )

    print(
        "\nFormats:"
    )

    print(
        "  - TXT"
    )

    print(
        "  - JSON"
    )

    print(
        "  - CSV"
    )

    print(
        "\nCharts:"
    )

    print(
        "  - Accounts by type (pie)"
    )

    print(
        "  - Transactions by status (bar)"
    )

    print(
        "  - Risk distribution (pie)"
    )

    print(
        "  - Balance movement (line)"
    )

    print(
        "\nAll files are stored in:"
    )

    print(
        (Path(__file__).resolve().parent / report_builder.output_dir)
    )

    print("\nDay 7 completed successfully.")