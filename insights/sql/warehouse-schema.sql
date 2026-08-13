-- BirdLife Australia — Insights Model target schema
-- Portable ANSI SQL. Runs on Power BI/Fabric, Business Central's warehouse,
-- Cloudflare D1, Postgres, or DuckDB — deliberately platform-neutral because
-- no warehouse decision has been made.
--
-- Conventions:
--   * Natural source keys are kept verbatim (sf_*, ns_*, stripe_*, woo_*).
--   * Every fact carries source_system so provenance is always queryable.
--   * Money is AUD, stored as DECIMAL(14,2).
--   * Loads are idempotent upserts on the natural key.

-- ============================================================ dimensions

CREATE TABLE dim_supporter (
    supporter_key        INTEGER PRIMARY KEY,
    sf_contact_id        VARCHAR(18) UNIQUE,      -- C-… convention on the label
    sf_account_id        VARCHAR(18),             -- household, N-… convention
    raisely_uuid         VARCHAR(64),
    betterimpact_id      VARCHAR(32),             -- ~empty until BI go-live
    ortto_synced         BOOLEAN DEFAULT FALSE,
    display_label        VARCHAR(120),            -- non-PII label for dashboards
    postcode             VARCHAR(10),
    state_code           VARCHAR(3),
    is_donor             BOOLEAN DEFAULT FALSE,
    is_member            BOOLEAN DEFAULT FALSE,
    is_regular_giver     BOOLEAN DEFAULT FALSE,
    is_volunteer         BOOLEAN DEFAULT FALSE,
    is_deceased          BOOLEAN DEFAULT FALSE,
    first_gift_date      DATE,
    last_gift_date       DATE,
    merged_into_key      INTEGER                  -- Plauti merge lineage
);

CREATE TABLE dim_staff (
    staff_key            INTEGER PRIMARY KEY,
    worker_code          VARCHAR(10) UNIQUE,      -- BLA### — the ruled join key
    company_email        VARCHAR(120),
    entra_object_id      VARCHAR(36),
    in_employment_hero   BOOLEAN DEFAULT FALSE,
    in_netsuite_payroll  BOOLEAN DEFAULT FALSE,
    in_entra             BOOLEAN DEFAULT FALSE,   -- guests (#EXT#) excluded at load
    department           VARCHAR(80),
    is_active            BOOLEAN DEFAULT TRUE,
    start_date           DATE,
    termination_date     DATE
);

CREATE TABLE dim_date (
    date_key             DATE PRIMARY KEY,
    au_fy                VARCHAR(9),              -- 'FY2026-27' (Jul–Jun)
    ns_fy                INTEGER,                 -- NetSuite fiscal = calendar year
    month_start          DATE,
    is_business_day_vic  BOOLEAN                  -- drives the ±3-business-day window
);

CREATE TABLE dim_campaign (
    campaign_key         INTEGER PRIMARY KEY,
    sf_campaign_id       VARCHAR(18) UNIQUE,
    name                 VARCHAR(200),
    parent_campaign_key  INTEGER,
    attribution_grain    VARCHAR(15) NOT NULL     -- 'campaign' | 'appeal-only' (DQ-10)
        CHECK (attribution_grain IN ('campaign','appeal-only'))
);

CREATE TABLE dim_gl_account (
    gl_account_key       INTEGER PRIMARY KEY,
    ns_account_number    VARCHAR(12) UNIQUE,      -- e.g. 11104, 41001
    name                 VARCHAR(120),
    account_type         VARCHAR(30),             -- asset/liability/income/expense
    is_bank              BOOLEAN DEFAULT FALSE,
    known_issue          VARCHAR(200)             -- e.g. '44013 GST ~$7,224/yr'
);

CREATE TABLE dim_org_unit (
    org_unit_key         INTEGER PRIMARY KEY,
    canonical_name       VARCHAR(120) NOT NULL,   -- the conformed department/programme
    ns_department_id     VARCHAR(20),
    ns_class_id          VARCHAR(20),
    ns_location_id       VARCHAR(20),
    ns_project_id        VARCHAR(20),
    asana_team_gid       VARCHAR(20),
    eh_department        VARCHAR(80),
    is_mapped            BOOLEAN DEFAULT FALSE    -- FALSE rows feed the unmapped % (DQ-13)
);

CREATE TABLE dim_membership_tier (
    tier_key             INTEGER PRIMARY KEY,
    name                 VARCHAR(40) UNIQUE,      -- Individual/Concession/Family/Hardship/Free
    price_aud            DECIMAL(8,2),
    max_household        INTEGER,
    is_hidden            BOOLEAN DEFAULT FALSE,
    verified_on          DATE                     -- tiers verified on staging 30 Jul 2026
);

CREATE TABLE dim_channel (
    channel_key          INTEGER PRIMARY KEY,
    name                 VARCHAR(40) UNIQUE       -- web/raisely/direct-debit/email/phone/event/bequest/internal
);

-- ================================================================= facts

CREATE TABLE fact_gift (
    sf_opportunity_id    VARCHAR(18) PRIMARY KEY,
    supporter_key        INTEGER REFERENCES dim_supporter,
    campaign_key         INTEGER REFERENCES dim_campaign,
    channel_key          INTEGER REFERENCES dim_channel,
    close_date           DATE NOT NULL,           -- the fundraising date basis
    amount_aud           DECIMAL(14,2) NOT NULL,
    is_membership        BOOLEAN DEFAULT FALSE,
    is_recurring_instal  BOOLEAN DEFAULT FALSE,
    gau_allocation       VARCHAR(120),
    record_type          VARCHAR(60),
    source_system        VARCHAR(20) NOT NULL DEFAULT 'salesforce'
);

CREATE TABLE fact_payment (
    payment_id           VARCHAR(40) PRIMARY KEY, -- npe01__OppPayment__c Id or Stripe bt id
    sf_opportunity_id    VARCHAR(18),
    stripe_charge_id     VARCHAR(40),
    stripe_refund_id     VARCHAR(40),             -- NULL until DQ-03 fixed
    paid_date            DATE,
    amount_aud           DECIMAL(14,2) NOT NULL,  -- refunds NEGATIVE here, whatever SF says
    is_refund            BOOLEAN DEFAULT FALSE,
    is_refund_defect     BOOLEAN DEFAULT FALSE,   -- TRUE where source showed positive refund (DQ-03)
    source_system        VARCHAR(20) NOT NULL
);

CREATE TABLE fact_recurring_agreement (
    agreement_id         VARCHAR(40) PRIMARY KEY,
    supporter_key        INTEGER REFERENCES dim_supporter,
    source_object        VARCHAR(30) NOT NULL     -- MANDATORY union provenance (DQ-05)
        CHECK (source_object IN ('npe03__Recurring_Donation__c','AAkPay__Recurring_Payment__c')),
    status               VARCHAR(20),
    frequency            VARCHAR(20),
    amount_per_instal    DECIMAL(10,2),
    monthly_value_aud    DECIMAL(10,2),           -- normalised at load
    start_date           DATE,
    end_date             DATE
);

CREATE TABLE fact_membership_period (
    period_id            VARCHAR(40) PRIMARY KEY,
    supporter_key        INTEGER REFERENCES dim_supporter,
    tier_key             INTEGER REFERENCES dim_membership_tier,
    start_date           DATE NOT NULL,
    end_date             DATE,                    -- start + 12m
    cease_date           DATE,                    -- start + 15m (3m grace)
    auto_renew           BOOLEAN,
    is_becs              BOOLEAN DEFAULT FALSE,   -- cannot migrate; needs fresh mandate
    source_system        VARCHAR(20) NOT NULL     -- 'payments2us' | 'woocommerce' during migration (DQ-06)
);

CREATE TABLE fact_order (
    woo_order_id         INTEGER PRIMARY KEY,
    sf_opportunity_id    VARCHAR(18),
    sf_writeback_ok      BOOLEAN,                 -- post meta present (DQ-02)
    sync_ok              BOOLEAN,                 -- miniOrange success (DQ-01)
    order_date           DATE,
    status               VARCHAR(20),             -- completed/refunded/failed
    total_aud            DECIMAL(12,2)
);

CREATE TABLE fact_gl_line (
    ns_line_id           VARCHAR(30) PRIMARY KEY,
    gl_account_key       INTEGER REFERENCES dim_gl_account,
    org_unit_key         INTEGER REFERENCES dim_org_unit,
    posting_date         DATE NOT NULL,           -- the finance date basis
    amount_aud           DECIMAL(14,2) NOT NULL,
    memo                 VARCHAR(400),
    subsidiary_id        INTEGER NOT NULL DEFAULT 2
        CHECK (subsidiary_id = 2)                 -- parent context never loads
);

CREATE TABLE fact_bank_line (
    bank_line_id         VARCHAR(40) PRIMARY KEY,
    gl_account_key       INTEGER REFERENCES dim_gl_account,
    value_date           DATE,
    amount_aud           DECIMAL(14,2),
    is_reconciled        BOOLEAN DEFAULT FALSE,
    reconciled_date      DATE
);

CREATE TABLE fact_reconciliation (
    sf_opportunity_id    VARCHAR(18) PRIMARY KEY,
    close_date           DATE,
    amount_aud           DECIMAL(14,2),
    ns_match_ref         VARCHAR(40),             -- NULL = unreconciled (the $671K backlog)
    matched_within_days  INTEGER,                 -- business days; policy Option A allows ≤3
    match_method         VARCHAR(20)              -- 'exact' | 'window' | 'manual' | NULL
);

CREATE TABLE fact_case (
    sf_case_id           VARCHAR(18) PRIMARY KEY,
    case_number          VARCHAR(12),
    record_type_dev_name VARCHAR(40) NOT NULL,    -- 'Zeus' = ICT; NEVER query without it (DQ-08)
    status               VARCHAR(30),
    case_type            VARCHAR(60),             -- 65% blank baseline
    owner_name           VARCHAR(80),             -- 'Zeus' = unassigned intake queue
    channel_key          INTEGER REFERENCES dim_channel,
    created_date         DATE,
    closed_date          DATE,
    days_to_resolution   INTEGER
);

CREATE TABLE fact_work_item (
    asana_task_gid       VARCHAR(20) PRIMARY KEY,
    project_gid          VARCHAR(20),
    section_name         VARCHAR(60),
    org_unit_key         INTEGER REFERENCES dim_org_unit,
    assignee             VARCHAR(80),
    due_on               DATE,                    -- NULL feeds the hygiene metric (DQ-14)
    completed            BOOLEAN,
    last_modified        DATE
);

CREATE TABLE fact_engagement (
    engagement_id        VARCHAR(60) PRIMARY KEY,
    supporter_key        INTEGER REFERENCES dim_supporter,
    campaign_key         INTEGER REFERENCES dim_campaign,
    event_type           VARCHAR(30),             -- open/click/unsubscribe/page-view/action
    event_date           DATE,
    source_system        VARCHAR(20) NOT NULL     -- 'ortto' | 'campaign-monitor' | 'ga4'
);

CREATE TABLE fact_training (
    enrolment_id         VARCHAR(40) PRIMARY KEY,
    staff_key            INTEGER REFERENCES dim_staff,
    course_name          VARCHAR(200),
    enrolled_date        DATE
    -- no completion columns on purpose: completion is not captured (DQ-21)
);

CREATE TABLE fact_event_attendance (
    ticket_id            VARCHAR(40) PRIMARY KEY,
    supporter_key        INTEGER REFERENCES dim_supporter,
    event_name           VARCHAR(200),
    event_date           DATE,
    source_system        VARCHAR(20) DEFAULT 'humanitix'
);

CREATE TABLE fact_payroll_summary (
    payrun_id            VARCHAR(30),
    org_unit_key         INTEGER REFERENCES dim_org_unit,
    payrun_date          DATE,
    headcount            INTEGER,                 -- aggregates only; no per-person salary
    gross_total_aud      DECIMAL(14,2),
    PRIMARY KEY (payrun_id, org_unit_key)
);

CREATE TABLE fact_security_posture (
    snapshot_month       DATE,
    measure              VARCHAR(60),             -- secure_score_pct/mfa_coverage_pct/device_compliance_pct/e8_<control>_level
    value_numeric        DECIMAL(10,2),
    value_text           VARCHAR(40),
    PRIMARY KEY (snapshot_month, measure)
    -- aggregate-only by design: named per-user weakness data never lands here
);

CREATE TABLE fact_volunteer_activity (
    activity_id          VARCHAR(40) PRIMARY KEY, -- placeholder until Better Impact go-live (DQ-24)
    supporter_key        INTEGER REFERENCES dim_supporter,
    activity_date        DATE,
    hours                DECIMAL(6,2),
    program              VARCHAR(120),
    source_system        VARCHAR(20) DEFAULT 'betterimpact'
);

-- ======================================================== metric views

-- Regular giving: the ONLY sanctioned count (DQ-05)
CREATE VIEW v_regular_giving AS
SELECT COUNT(*)                    AS active_agreements,
       SUM(monthly_value_aud)      AS monthly_value_aud,
       COUNT(DISTINCT source_object) AS source_objects_present  -- must be 2 pre-decommission
FROM fact_recurring_agreement
WHERE status = 'Active';

-- ICT queue: scope is part of the definition (DQ-08)
CREATE VIEW v_ict_open_queue AS
SELECT CASE WHEN owner_name = 'Zeus' THEN 'UNASSIGNED INTAKE' ELSE owner_name END AS owner_group,
       status, COUNT(*) AS open_cases,
       SUM(CASE WHEN case_type IS NULL THEN 1 ELSE 0 END) AS missing_type
FROM fact_case
WHERE record_type_dev_name = 'Zeus' AND closed_date IS NULL
GROUP BY 1, 2;

-- Unreconciled income: the standing finance control number (DQ-18/19)
CREATE VIEW v_unreconciled_income AS
SELECT COUNT(*) AS unmatched_records,
       SUM(amount_aud) AS unmatched_aud,
       MIN(close_date) AS oldest_close_date
FROM fact_reconciliation
WHERE ns_match_ref IS NULL;

-- Headcount triangle: should be three zeros (DQ-15)
CREATE VIEW v_headcount_triangle AS
SELECT SUM(CASE WHEN in_employment_hero AND NOT in_netsuite_payroll THEN 1 ELSE 0 END) AS eh_not_ns,
       SUM(CASE WHEN in_netsuite_payroll AND NOT in_employment_hero THEN 1 ELSE 0 END) AS ns_not_eh,
       SUM(CASE WHEN in_employment_hero AND NOT in_entra THEN 1 ELSE 0 END)            AS eh_not_entra
FROM dim_staff
WHERE is_active;

-- Woo→SF sync integrity (DQ-01/02)
CREATE VIEW v_sync_integrity AS
SELECT COUNT(*) AS paid_orders,
       AVG(CASE WHEN sf_writeback_ok THEN 1.0 ELSE 0.0 END) AS writeback_rate,
       AVG(CASE WHEN sync_ok         THEN 1.0 ELSE 0.0 END) AS sync_success_rate
FROM fact_order
WHERE status = 'completed';
