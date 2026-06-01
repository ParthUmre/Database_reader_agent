# ==========================================
# BUSINESS SCHEMA DICTIONARY
# ==========================================
# This file gives business meaning to database tables.
# It helps the SQL Agent understand user language
# and map it to the correct MySQL/MariaDB tables.


BUSINESS_SCHEMA_DICTIONARY = """
==================================================
DATABASE BUSINESS DICTIONARY
==================================================

The database name is warehouse_db.

This database stores warehouse, inventory, retailer, sales,
item, and finance-related structured data.

The active business tables are:

1. gpos_retailer
2. gpos_sales
3. gpos_salesb2b
4. gpos_items
5. gpos_invsummary_item
6. gpos_item_quantities
7. finance_transactions

The products and warehouses tables currently exist but may be empty.
Do not prefer products or warehouses unless the user specifically asks
about those tables or they contain relevant data.

Users provide store_code.
Backend/store_context_service resolves store_code into retailer_id.
The SQL Agent receives only the resolved retailer_id.
The SQL Agent must filter business tables using retailer_id, not store_code.

==================================================
RETAILER / STORE TABLE
==================================================

TABLE: gpos_retailer

Business meaning:
- This table stores retailer/store/customer information.
- A retailer represents a customer/store/business unit.
- Users usually know store_code, not retailer_id.
- retailer_id is the internal identifier used to filter customer-specific data.
- store_code should be used to find retailer_id.

Important columns:
- gpos_retailer.retailer_id
- gpos_retailer.store_code

Business rules:
- If the user provides a store code, resolve it through gpos_retailer.
- For customer-specific queries, use retailer_id.
- Never assume global sales/inventory unless explicitly asked by admin.
- If the selected table has retailer_id, add:
  WHERE table_name.retailer_id = {{retailer_id}}
- Use retailer_id, not store_code, for filtering business tables.
- store_code is only used by backend/store_context_service to resolve retailer_id.

==================================================
SALES TABLE
==================================================

TABLE: gpos_sales

Business meaning:
- This is the main sales table.
- When the user says sales, sale amount, revenue, net total,
  gross sales, tax, discount, bill amount, or sales performance,
  prefer this table.
- This table should be used for store-level sales analysis.

Common user words mapped to this table:
- "sales" -> gpos_sales
- "revenue" -> gpos_sales
- "net sales" -> gpos_sales.net_total
- "net total" -> gpos_sales.net_total
- "tax" or "taxes" -> gpos_sales.tax
- "discount" -> gpos_sales.discount if column exists
- "bill" or "invoice" -> gpos_sales
- "average tax" -> AVG(gpos_sales.tax)
- "total sales" -> SUM(gpos_sales.net_total)
- "average sales" -> AVG(gpos_sales.net_total)

Mandatory filter:
- For customer/store-specific sales queries, filter using:
  gpos_sales.retailer_id = {retailer_id}

Example:
SELECT
    SUM(gpos_sales.net_total) AS total_sales
FROM gpos_sales
WHERE gpos_sales.retailer_id = {retailer_id};

==================================================
B2B SALES TABLE
==================================================

TABLE: gpos_salesb2b

Business meaning:
- This table stores B2B sales records.
- Use it when the user specifically asks about B2B sales,
  wholesale sales, business-to-business sales, or bulk customer sales.

Common user words:
- "B2B sales" -> gpos_salesb2b
- "wholesale sales" -> gpos_salesb2b
- "business customer sales" -> gpos_salesb2b

Mandatory filter:
- If this table has retailer_id, filter using:
  gpos_salesb2b.retailer_id = {retailer_id}

==================================================
ITEM MASTER TABLE
==================================================

TABLE: gpos_items

Business meaning:
- This table stores item/product master details.
- Use it when the user asks about item names, product names,
  item categories, SKUs, barcodes, or product details.

Common user words:
- "item" -> gpos_items
- "product" -> gpos_items
- "SKU" -> gpos_items
- "barcode" -> gpos_items
- "category" -> gpos_items

Possible joins:
- Inventory tables may connect to gpos_items through item/product/item_id columns.
- Use actual schema columns from dynamic schema context.

==================================================
INVENTORY SUMMARY TABLE
==================================================

TABLE: gpos_invsummary_item

Business meaning:
- This table stores inventory summary at item level.
- Use it when the user asks about stock summary,
  inventory summary, available stock, stock value,
  item-wise inventory, or current inventory position.

Common user words:
- "inventory" -> gpos_invsummary_item
- "stock summary" -> gpos_invsummary_item
- "available stock" -> gpos_invsummary_item
- "current stock" -> gpos_invsummary_item
- "stock value" -> gpos_invsummary_item

Mandatory filter:
- If this table has retailer_id, filter using:
  gpos_invsummary_item.retailer_id = {retailer_id}

==================================================
ITEM QUANTITY TABLE
==================================================

TABLE: gpos_item_quantities

Business meaning:
- This table stores item quantity details.
- Use it when the user asks about item quantity,
  stock count, quantity available, or quantity movement.

Common user words:
- "quantity" -> gpos_item_quantities
- "item quantity" -> gpos_item_quantities
- "stock count" -> gpos_item_quantities
- "available quantity" -> gpos_item_quantities

Mandatory filter:
- If this table has retailer_id, filter using:
  gpos_item_quantities.retailer_id = {retailer_id}

==================================================
FINANCE TRANSACTIONS TABLE
==================================================

TABLE: finance_transactions

Business meaning:
- This table stores finance-related transactions.
- Use it for payment, transaction, accounting, finance,
  debit, credit, expense, and financial movement queries.

Common user words:
- "finance" -> finance_transactions
- "transaction" -> finance_transactions
- "payment" -> finance_transactions
- "amount" -> finance_transactions
- "expense" -> finance_transactions
- "credit" -> finance_transactions
- "debit" -> finance_transactions

Mandatory filter:
- If this table has retailer_id, filter using:
  finance_transactions.retailer_id = {retailer_id}

==================================================
GLOBAL RETAILER FILTERING RULE
==================================================

This is a multi-customer database.

Every normal user query must be filtered to the current retailer.

The current retailer_id will be provided separately as:

retailer_id = {retailer_id}

Rules:
1. If the selected table has retailer_id, always add:
   WHERE table_name.retailer_id = {retailer_id}

2. If the query already has WHERE condition, append:
   AND table_name.retailer_id = {retailer_id}

3. If the selected table does not directly have retailer_id,
   join with the appropriate table that has retailer_id if possible.

4. Never generate customer-wide/global result unless the user is admin
   or the query explicitly asks for all retailers.

5. Never ask the user for retailer_id.
   The system resolves retailer_id from store_code.

==================================================
SQL STYLE RULES
==================================================

1. Use MySQL/MariaDB-compatible SQL.
2. Do not use table aliases.
3. Always use complete table names.
4. Use gpos_sales.net_total, not gs.net_total.
5. Use gpos_sales.tax, not gs.tax.
6. Use gpos_retailer.store_code, not gr.store_code.
7. Do not hallucinate tables.
8. Do not hallucinate columns.
9. Use only columns available in the dynamic schema context.
10. Prefer clear aggregate column names.

==================================================
IMPORTANT EXAMPLES
==================================================

User question:
What is my total sales?

Correct SQL pattern:
SELECT
    SUM(gpos_sales.net_total) AS total_sales
FROM gpos_sales
WHERE gpos_sales.retailer_id = {retailer_id};

--------------------------------------------------

User question:
What is the average tax from sales?

Correct SQL pattern:
SELECT
    AVG(gpos_sales.tax) AS average_tax
FROM gpos_sales
WHERE gpos_sales.retailer_id = {retailer_id};

--------------------------------------------------

User question:
Show sales count

Correct SQL pattern:
SELECT
    COUNT(*) AS total_sales_records
FROM gpos_sales
WHERE gpos_sales.retailer_id = {retailer_id};

--------------------------------------------------

User question:
Show my inventory summary

Correct SQL pattern:
SELECT
    *
FROM gpos_invsummary_item
WHERE gpos_invsummary_item.retailer_id = {retailer_id}
LIMIT 20;

==================================================
END OF BUSINESS DICTIONARY
==================================================
"""