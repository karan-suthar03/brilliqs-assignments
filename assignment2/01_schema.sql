-- Assignment 2 - tables
--
-- sales is denormalised on purpose: the customer, product and rep details
-- repeat on every row, the way a flat export from a reporting system does.
--
-- monthly_targets is one row per region, category and month. That coarser
-- grain is the mismatch the reconciliation query has to bridge.

DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS monthly_targets;

CREATE TABLE sales (
    sale_id          bigint PRIMARY KEY,
    order_id         bigint NOT NULL,
    sale_date        date NOT NULL,

    customer_id      integer NOT NULL,
    customer_name    varchar(100) NOT NULL,
    customer_city    varchar(50) NOT NULL,
    customer_state   varchar(50) NOT NULL,
    customer_segment varchar(20) NOT NULL,

    product_id       integer NOT NULL,
    product_name     varchar(100) NOT NULL,
    category         varchar(50) NOT NULL,
    subcategory      varchar(50) NOT NULL,

    region           varchar(20) NOT NULL,
    sales_rep_id     integer NOT NULL,
    sales_rep_name   varchar(100) NOT NULL,

    quantity         integer NOT NULL,
    unit_price       numeric(10,2) NOT NULL,
    discount_pct     numeric(5,4) NOT NULL DEFAULT 0,
    revenue          numeric(12,2) NOT NULL
);

CREATE INDEX sales_category_date_idx ON sales (category, sale_date);
CREATE INDEX sales_region_date_idx ON sales (region, sale_date);

CREATE TABLE monthly_targets (
    region         varchar(20) NOT NULL,
    category       varchar(50) NOT NULL,
    target_month   date NOT NULL,
    target_revenue numeric(12,2) NOT NULL,

    PRIMARY KEY (region, category, target_month)
);
