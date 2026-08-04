-- Assignment 2 - sample data
--
-- Generated in SQL so the whole assignment runs with psql alone. setseed
-- fixes the random sequence, so running this twice gives the same table.

SELECT setseed(0.42);

TRUNCATE sales;
TRUNCATE monthly_targets;

INSERT INTO sales (
    sale_id, order_id, sale_date,
    customer_id, customer_name, customer_city, customer_state, customer_segment,
    product_id, product_name, category, subcategory,
    region, sales_rep_id, sales_rep_name,
    quantity, unit_price, discount_pct, revenue
)
WITH
products (product_id, product_name, category, subcategory, unit_price) AS (
    VALUES
        ( 1, 'Laptop 14"',          'Electronics', 'Computers',   68000.00),
        ( 2, 'Wireless Mouse',      'Electronics', 'Accessories',   1450.00),
        ( 3, 'Mechanical Keyboard', 'Electronics', 'Accessories',   5900.00),
        ( 4, '27" Monitor',         'Electronics', 'Displays',    24500.00),
        ( 5, 'Noise Cancelling Headphones', 'Electronics', 'Audio', 18900.00),
        ( 6, 'Table Lamp',          'Home',        'Lighting',      2100.00),
        ( 7, 'Cotton Bedsheet Set', 'Home',        'Bedding',       3400.00),
        ( 8, 'Ceramic Mug',         'Home',        'Kitchen',        450.00),
        ( 9, 'Wall Clock',          'Home',        'Decor',         1800.00),
        (10, 'Cast Iron Skillet',   'Home',        'Kitchen',       4200.00),
        (11, 'Cotton T-Shirt',      'Apparel',     'Tops',           899.00),
        (12, 'Denim Jacket',        'Apparel',     'Outerwear',     3600.00),
        (13, 'Running Shoes',       'Apparel',     'Footwear',      5400.00),
        (14, 'Wool Scarf',          'Apparel',     'Accessories',   1250.00),
        (15, 'Formal Shirt',        'Apparel',     'Tops',          1899.00),
        (16, 'Olive Oil 1L',        'Grocery',     'Cooking',        980.00),
        (17, 'Basmati Rice 5kg',    'Grocery',     'Staples',        720.00),
        (18, 'Ground Coffee 500g',  'Grocery',     'Beverages',      640.00),
        (19, 'Dark Chocolate',      'Grocery',     'Confectionery',  310.00),
        (20, 'Green Tea 100 bags',  'Grocery',     'Beverages',      520.00)
),

cities (city_idx, customer_city, customer_state) AS (
    VALUES
        (0, 'Mumbai',    'Maharashtra'),
        (1, 'Pune',      'Maharashtra'),
        (2, 'Bengaluru', 'Karnataka'),
        (3, 'Chennai',   'Tamil Nadu'),
        (4, 'Hyderabad', 'Telangana'),
        (5, 'Ahmedabad', 'Gujarat'),
        (6, 'Jaipur',    'Rajasthan'),
        (7, 'Kolkata',   'West Bengal'),
        (8, 'Delhi',     'Delhi'),
        (9, 'Kochi',     'Kerala')
),

reps (sales_rep_id, sales_rep_name, region) AS (
    VALUES
        ( 1, 'Anjali Deshpande', 'West'),
        ( 2, 'Rohit Kulkarni',   'West'),
        ( 3, 'Priya Nair',       'South'),
        ( 4, 'Karthik Iyer',     'South'),
        ( 5, 'Sneha Reddy',      'South'),
        ( 6, 'Vikram Singh',     'North'),
        ( 7, 'Meera Gupta',      'North'),
        ( 8, 'Arjun Mehta',      'North'),
        ( 9, 'Debjani Bose',     'East'),
        (10, 'Sourav Das',       'East'),
        (11, 'Ritu Agarwal',     'East'),
        (12, 'Nikhil Joshi',     'West')
),

customers AS (
    SELECT
        c                                                    AS customer_id,
        (ARRAY['Aarav','Diya','Ishaan','Ananya','Kabir',
               'Meera','Rohan','Saanvi','Vivaan','Tara'])[1 + (c * 7) % 10]
          || ' ' ||
        (ARRAY['Sharma','Patel','Reddy','Nair','Gupta',
               'Iyer','Bose','Singh','Mehta','Joshi'])[1 + (c * 3) % 10]
                                                             AS customer_name,
        cities.customer_city,
        cities.customer_state,
        (ARRAY['Consumer','Corporate','Small Business'])[1 + (c * 5) % 3]
                                                             AS customer_segment
    FROM generate_series(1, 200) AS c
    JOIN cities ON cities.city_idx = c % 10
),

raw AS (
    SELECT
        g                                              AS sale_id,
        10000 + ((g - 1) / 3)                          AS order_id,
        DATE '2024-01-01' + (random() * 730)::int      AS sale_date,
        1  + floor(random() * 200)::int                AS customer_id,
        1  + floor(random() * 20)::int                 AS product_id,
        1  + floor(random() * 12)::int                 AS sales_rep_id,
        1  + floor(random() * 5)::int                  AS quantity,
        CASE WHEN random() < 0.65
             THEN 0::numeric
             ELSE round((random() * 0.30)::numeric, 4)
        END                                            AS discount_pct
    FROM generate_series(1, 5000) AS g
)
SELECT
    raw.sale_id,
    raw.order_id,
    raw.sale_date,
    cu.customer_id,
    cu.customer_name,
    cu.customer_city,
    cu.customer_state,
    cu.customer_segment,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    r.region,
    r.sales_rep_id,
    r.sales_rep_name,
    raw.quantity,
    p.unit_price,
    raw.discount_pct,
    round(raw.quantity * p.unit_price * (1 - raw.discount_pct), 2) AS revenue
FROM raw
JOIN customers cu ON cu.customer_id = raw.customer_id
JOIN products  p  ON p.product_id   = raw.product_id
JOIN reps      r  ON r.sales_rep_id = raw.sales_rep_id;

INSERT INTO monthly_targets (region, category, target_month, target_revenue)
SELECT
    s.region,
    s.category,
    CAST(DATE_TRUNC('month', s.sale_date) AS date) AS target_month,
    round((sum(s.revenue) * (0.85 + random() * 0.40))::numeric, 2) AS target_revenue
FROM sales s
GROUP BY s.region, s.category, date_trunc('month', s.sale_date)
HAVING random() > 0.08;

INSERT INTO monthly_targets (region, category, target_month, target_revenue)
VALUES
    ('West',  'Electronics', DATE '2026-01-01', 900000.00),
    ('South', 'Grocery',     DATE '2026-01-01', 150000.00);
