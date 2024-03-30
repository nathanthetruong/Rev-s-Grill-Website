/* 
This file starts with a completely empty sql enviornment and creates all tables,
then populates the tables with 100,000 orders
*/


/* insert all tables into the database */
\i /home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/Create_Empty_Tables.sql;

/* insert employee, inventory, menu, menu_btrakout */
\COPY employees FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/employee.csv' WITH (FORMAT csv, HEADER true);
\COPY inventory FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/inventory.csv' WITH (FORMAT csv, HEADER true);
\COPY menu_items FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/menu_items.csv' WITH (FORMAT csv, HEADER true);
\COPY food_to_inventory FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/food_to_inventory.csv' WITH (FORMAT csv, HEADER true);

/* insert orders, customer, order_breakout */
\COPY customers FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/customer.csv' WITH (FORMAT csv, HEADER true);
\COPY orders FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/orders.csv' WITH (FORMAT csv, HEADER true);
\COPY order_breakout FROM '/home/matthew/project-3-full-stack-agile-web-project-3-900-01/SQL_Sample_Data/csv/order_breakout.csv' WITH (FORMAT csv, HEADER true);
