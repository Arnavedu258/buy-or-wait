
-- =====================================
-- Buy or Wait - ER Schema
-- =====================================

CREATE TABLE user_profile (
    user_id TEXT PRIMARY KEY,
    home_currency TEXT NOT NULL,
    available_balance REAL NOT NULL,
    minimum_balance_to_keep REAL NOT NULL,
    financial_priority TEXT,
    spending_preference TEXT,
    payment_methods_user_will_consider TEXT,
    max_installment_months INTEGER
);

CREATE TABLE request (
    request_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    request_date DATE NOT NULL,
    request_type TEXT NOT NULL,
    requested_amount REAL NOT NULL,
    desired_completion_date DATE NOT NULL,
    allows_partial_payment BOOLEAN NOT NULL,
    request_text TEXT,
    FOREIGN KEY(user_id) REFERENCES user_profile(user_id)
);

CREATE TABLE financial_event (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_type TEXT,
    category TEXT,
    amount REAL,
    currency TEXT,
    status TEXT,
    recurring BOOLEAN,
    flexible BOOLEAN,
    linked_event_id TEXT,
    FOREIGN KEY(user_id) REFERENCES user_profile(user_id)
);

CREATE TABLE message (
    message_id TEXT PRIMARY KEY,
    user_id TEXT,
    request_id TEXT,
    related_event_id TEXT,
    message_date DATE,
    source TEXT,
    content TEXT,
    FOREIGN KEY(user_id) REFERENCES user_profile(user_id),
    FOREIGN KEY(request_id) REFERENCES request(request_id),
    FOREIGN KEY(related_event_id) REFERENCES financial_event(event_id)
);

CREATE TABLE payment_option (
    payment_option_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    payment_method TEXT,
    number_of_payments INTEGER,
    interval_days INTEGER,
    first_payment_date DATE,
    financing_fee REAL,
    total_payable REAL,
    FOREIGN KEY(request_id) REFERENCES request(request_id)
);

CREATE TABLE image_reference (
    image_id TEXT PRIMARY KEY,
    user_id TEXT,
    request_id TEXT,
    related_event_id TEXT,
    image_path TEXT,
    FOREIGN KEY(user_id) REFERENCES user_profile(user_id),
    FOREIGN KEY(request_id) REFERENCES request(request_id),
    FOREIGN KEY(related_event_id) REFERENCES financial_event(event_id)
);

CREATE TABLE exchange_rate (
    rate_date DATE,
    from_currency TEXT,
    to_currency TEXT,
    rate REAL,
    PRIMARY KEY(rate_date, from_currency, to_currency)
);