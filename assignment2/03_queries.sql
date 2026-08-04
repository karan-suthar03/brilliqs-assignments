-- Assignment 2 - the three required queries.
-- Plain SELECTs only: no stored procedures, no cursors, no loops.


-- Q1. Monthly revenue per category, with the previous month and a 3 month
-- moving average.
--
-- LAG reaches back one row. The moving average reuses the same window but
-- adds a frame, so it covers this month and the two before it.

WITH monthly AS (
    SELECT
        category,
        CAST(DATE_TRUNC('month', sale_date) AS date) AS month,
        SUM(revenue) AS revenue
    FROM sales
    GROUP BY category, CAST(DATE_TRUNC('month', sale_date) AS date)
)
SELECT
    category,
    month,
    revenue,
    LAG(revenue) OVER w AS prev_month,
    ROUND(AVG(revenue) OVER (w ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)
        AS moving_avg_3m
FROM monthly
WINDOW w AS (PARTITION BY category ORDER BY month)
ORDER BY category, month;


-- Q2. Top 3 products by revenue in each category.
--
-- The rank is computed in a CTE and filtered outside it, because a window
-- function is not allowed in WHERE.

WITH product_totals AS (
    SELECT
        category,
        product_name,
        SUM(revenue) AS total_revenue,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY SUM(revenue) DESC) AS rnk
    FROM sales
    GROUP BY category, product_name
)
SELECT category, rnk, product_name, total_revenue
FROM product_totals
WHERE rnk <= 3
ORDER BY category, rnk;


-- Q3. Actual sales against targets.
--
-- sales is one row per order line and monthly_targets is one row per region,
-- category and month, so the sales are rolled up to the target's grain first.
-- FULL OUTER JOIN so that months with no target, and targets with no sales,
-- both still show up.

WITH sales_by_month AS (
    SELECT
        region,
        category,
        CAST(DATE_TRUNC('month', sale_date) AS date) AS month,
        SUM(revenue) AS actual_revenue
    FROM sales
    GROUP BY region, category, CAST(DATE_TRUNC('month', sale_date) AS date)
)
SELECT
    COALESCE(s.region, t.region) AS region,
    COALESCE(s.category, t.category) AS category,
    COALESCE(s.month, t.target_month) AS month,
    s.actual_revenue,
    t.target_revenue
FROM sales_by_month s
FULL OUTER JOIN monthly_targets t
    ON t.region = s.region
   AND t.category = s.category
   AND t.target_month = s.month
ORDER BY region, category, month;
