# Inventory Management System

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Database Structure](#database-structure)
7. [Functions Overview](#functions-overview)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

## Introduction

The Inventory Management System is a Python-based application designed to help businesses manage their inventory, track sales, and maintain product information. This system uses MySQL as its database backend and provides a command-line interface for easy interaction.

## Features

- Product management (add, update, delete)
- Stock tracking
- Sales recording
- Automated stock updates on sales
- Detailed reporting (stocks, products, sales)
- Secure admin access

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.7+
- MySQL Server 5.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/inventory-management-system.git
   ```

2. Navigate to the project directory:
   ```
   cd inventory-management-system
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your MySQL database:
   - Create a new database named `Inventory`
   - Update the `pw` variable in the script with your MySQL root password

## Usage

To run the Inventory Management System:

1. Open a terminal or command prompt
2. Navigate to the project directory
3. Run the following command:
   ```
   python inventory_management.py
   ```
4. Enter the admin password when prompted (default is "admin")
5. Use the menu options to interact with the system

## Database Structure

The system uses three main tables:

1. `stocks`: Stores information about product quantities
   - `pid` (int): Product ID
   - `pname` (varchar): Product name
   - `quantity` (int): Current stock quantity

2. `products`: Stores product information
   - `pid` (int): Product ID
   - `pname` (varchar): Product name
   - `pprice` (int): Product price

3. `sales`: Records sales transactions
   - `id` (int): Sale ID
   - `date_ordered` (date): Date of sale
   - `name` (varchar): Customer name
   - `pid` (int): Product ID
   - `pname` (varchar): Product name
   - `pprice` (int): Product price at time of sale
   - `quantity` (int): Quantity sold
   - `total` (int): Total sale amount

## Functions Overview

- `create_server_connection()`: Establishes a connection to the MySQL server
- `create_database()`: Creates the Inventory database if it doesn't exist
- `create_db_connection()`: Connects to the Inventory database
- `execute_querry()`: Executes SQL queries
- `table_create_exits()`: Creates necessary tables and triggers
- `insert_stock_products()`: Adds new products to the inventory
- `insert_sales()`: Records new sales transactions
- `display_stocks()`, `display_products()`, `display_sales()`: Show current data
- `stock_update()`: Updates product quantities
- `products_update()`: Updates product prices
- `delete_value()`: Removes entries from the database

## Troubleshooting

- If you encounter a "Access denied" error, ensure your MySQL credentials are correct
- For "Table already exists" errors, you can safely ignore them if the tables are already set up
- If you experience connection issues, verify that your MySQL server is running

## Contributing

Contributions to the Inventory Management System are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request
