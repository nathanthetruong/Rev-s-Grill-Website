CREATE TABLE employees (
    "id" int PRIMARY KEY,
    "name" text,
    "is_manager" boolean
);

CREATE TABLE customers (
    "id" int PRIMARY KEY,
    "first_name" text,
    "last_name" text
);

CREATE TABLE orders (
    "id" int PRIMARY KEY,
    "customer_id" int,
    "employee_id" int,
    "total_price" double precision,
    "order_time" timestamp without time zone,
    FOREIGN KEY ("customer_id") REFERENCES customers ("id"),
    FOREIGN KEY ("employee_id") REFERENCES employees ("id")
);

CREATE TABLE inventory (
    "id" int PRIMARY KEY,
    "description" text,
    "quantity_remaining" int,
    "quantity_target" int
);

CREATE TABLE menu_items (
    "id" int PRIMARY KEY,
    "price" double precision,
    "description" text,
    "category" text,
    "times_ordered" int,
    "start_date" timestamp without time zone,
    "end_date" timestamp without time zone
);

CREATE TABLE food_to_inventory (
    "food_item_id" int,
    "food_description" text,
    "quantity" int,
    "inventory_description" text,
    "inventory_id" int,
    FOREIGN KEY ("food_item_id") REFERENCES menu_items ("id")
);

CREATE TABLE order_breakout (
    "order_id" int,
    "food_items" int,
    FOREIGN KEY ("order_id") REFERENCES orders ("id")
);