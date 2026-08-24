CREATE TABLE customers (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT customers_status_check
        CHECK (status IN ('active', 'inactive'))
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    billing_cycle VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL,
    next_billing_date DATE NOT NULL,

    CONSTRAINT subscriptions_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers(id),

    CONSTRAINT subscriptions_amount_check
        CHECK (amount > 0),

    CONSTRAINT subscriptions_billing_cycle_check
        CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly')),

    CONSTRAINT subscriptions_status_check
        CHECK (status IN ('active', 'past_due', 'cancelled', 'paused'))
);

CREATE TABLE payment_attempts (
    id UUID PRIMARY KEY,
    subscription_id UUID NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    payment_method VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL,
    failure_reason VARCHAR(100),
    decline_code VARCHAR(50),
    attempt_number INTEGER NOT NULL DEFAULT 1,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT payment_subscription_fk
        FOREIGN KEY (subscription_id)
        REFERENCES subscriptions(id),

    CONSTRAINT payment_amount_check
        CHECK (amount > 0),

    CONSTRAINT payment_status_check
        CHECK (status IN ('success', 'failed', 'pending')),

    CONSTRAINT payment_method_check
        CHECK (payment_method IN (
            'card',
            'upi',
            'bank_transfer',
            'wallet'
        )),

    CONSTRAINT payment_attempt_number_check
        CHECK (attempt_number > 0)
);

CREATE TABLE recovery_cases (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    subscription_id UUID NOT NULL,
    trigger_payment_id UUID NOT NULL,
    revenue_at_risk NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    retry_count INTEGER NOT NULL DEFAULT 0,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,

    CONSTRAINT recovery_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers(id),

    CONSTRAINT recovery_subscription_fk
        FOREIGN KEY (subscription_id)
        REFERENCES subscriptions(id),

    CONSTRAINT recovery_trigger_payment_fk
        FOREIGN KEY (trigger_payment_id)
        REFERENCES payment_attempts(id),

    CONSTRAINT recovery_revenue_check
        CHECK (revenue_at_risk > 0),

    CONSTRAINT recovery_status_check
        CHECK (status IN (
            'active',
            'recovered',
            'escalated',
            'failed',
            'stopped'
        )),

    CONSTRAINT recovery_priority_check
        CHECK (priority IN (
            'low',
            'medium',
            'high',
            'critical'
        )),

    CONSTRAINT recovery_retry_check
        CHECK (retry_count >= 0)
);

CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY,
    recovery_case_id UUID NOT NULL,
    root_cause VARCHAR(100) NOT NULL,
    confidence NUMERIC(5, 4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    recommended_action VARCHAR(50) NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT decision_case_fk
        FOREIGN KEY (recovery_case_id)
        REFERENCES recovery_cases(id),

    CONSTRAINT decision_confidence_check
        CHECK (confidence >= 0 AND confidence <= 1),

    CONSTRAINT decision_risk_check
        CHECK (risk_level IN (
            'low',
            'medium',
            'high',
            'critical'
        )),

    CONSTRAINT decision_action_check
        CHECK (recommended_action IN (
            'retry_payment',
            'wait_and_retry',
            'request_payment_update',
            'send_reminder',
            'escalate',
            'stop'
        ))
);

CREATE TABLE recovery_actions (
    id UUID PRIMARY KEY,
    recovery_case_id UUID NOT NULL,
    agent_decision_id UUID,
    action_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    attempt_number INTEGER NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    result TEXT,

    CONSTRAINT action_case_fk
        FOREIGN KEY (recovery_case_id)
        REFERENCES recovery_cases(id),

    CONSTRAINT action_decision_fk
        FOREIGN KEY (agent_decision_id)
        REFERENCES agent_decisions(id),

    CONSTRAINT action_status_check
        CHECK (status IN (
            'pending',
            'approved',
            'executing',
            'success',
            'failed',
            'rejected'
        )),

    CONSTRAINT action_type_check
        CHECK (action_type IN (
            'retry_payment',
            'wait_and_retry',
            'request_payment_update',
            'send_reminder',
            'escalate',
            'stop'
        )),

    CONSTRAINT action_attempt_check
        CHECK (attempt_number > 0)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    recovery_case_id UUID,
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT audit_case_fk
        FOREIGN KEY (recovery_case_id)
        REFERENCES recovery_cases(id),

    CONSTRAINT audit_actor_check
        CHECK (actor IN (
            'system',
            'ai_agent',
            'policy_engine',
            'executor',
            'admin'
        ))
);

CREATE INDEX idx_subscriptions_customer_id
    ON subscriptions(customer_id);

CREATE INDEX idx_payment_attempts_subscription_id
    ON payment_attempts(subscription_id);

CREATE INDEX idx_payment_attempts_status
    ON payment_attempts(status);

CREATE INDEX idx_payment_attempts_attempted_at
    ON payment_attempts(attempted_at);

CREATE INDEX idx_recovery_cases_status
    ON recovery_cases(status);

CREATE INDEX idx_recovery_cases_customer_id
    ON recovery_cases(customer_id);

CREATE INDEX idx_agent_decisions_case_id
    ON agent_decisions(recovery_case_id);

CREATE INDEX idx_recovery_actions_case_id
    ON recovery_actions(recovery_case_id);

CREATE INDEX idx_audit_logs_case_id
    ON audit_logs(recovery_case_id);

CREATE INDEX idx_audit_logs_created_at
    ON audit_logs(created_at);