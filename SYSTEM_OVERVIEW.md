# Point of Sale (POS) System for Computer Parts and Services

The POS system is designed to streamline the management of inventory, billing, and sales tracking for computer parts and service items. Because computer shops handle many products (with different SKUs, categories, and stock counts) while also needing fast checkout and accurate reporting, a centralized desktop POS system is essential for day-to-day operations.

Problem 1: Difficulty in Tracking Inventory of Computer Parts

Tracking inventory manually can lead to stockouts, overstocking, and mismatched counts. This is especially challenging when managing many parts (CPU, motherboard, RAM, storage, peripherals) that move quickly and must be updated every time there is a sale or stock adjustment.

Solution 1: Inventory and Stock Monitoring (Products & Inventory Module)

The current system provides a dedicated **Products & Inventory** screen where products can be created, categorized, and searched. Stock levels are stored in the database and shown in the table, including **low-stock highlighting** to help staff quickly identify items that need replenishment. Stock adjustments (add/remove/set) are recorded as stock change logs to improve accountability.

Problem 2: Inaccurate or Slow Billing Process

Manual billing increases the chance of wrong totals, missed payment details, and delays during checkout. For a shop with frequent sales, a slow billing process impacts customer experience and increases staff workload.

Solution 2: Automated Sales, Checkout, and Receipt Generation (Sales/POS Module)

The system includes a **Sales (POS)** screen with a product search (by name or SKU), category filtering, and a cart-based checkout flow. It automatically computes totals, supports multiple payment methods (**cash, card, check**), and records each sale as a transaction with itemized transaction items. After checkout, the user can generate and view a digital receipt using the built-in receipt dialog.

Problem 3: Limited Visibility into Customers and Business Performance

Without consolidated sales history and reporting, it is hard to track customer transactions, see best-selling products, and understand profitability. This can lead to weak purchasing decisions and limited insight into daily/monthly performance.

Solution 3: Customer Transaction History and Sales Reporting (Customers + Reports Modules)

The system stores transaction history (including optional customer name and phone at checkout). The **Customers & Transactions** screen summarizes customer activity and provides a searchable transaction list with quick receipt viewing.

For management, the **Reports** screen provides date-range reporting including total sales, total orders, average order value, profit computation (sales vs recorded cost), top products, low stock list, and CSV export. Report access is protected through role-based permissions (admin vs employee).

Conclusion

The POS system solves key operational challenges in computer parts retail by combining real-time inventory tracking, fast and consistent billing with receipts, and clear customer/sales reporting. By using a desktop application with a centralized database, the system reduces errors, improves checkout speed, and supports better decision-making through reporting and analytics.

Tools

The POS system is developed using the following tools and technologies (based on the current implementation):

1. Integrated Development Environment (IDE):

Visual Studio Code (VS Code) is used for editing and maintaining the source code.

2. Programming Language:

The system is built using **Python**.

3. Frontend / User Interface:

The system uses **PyQt6** to implement the desktop user interface (login screen, dashboard, products, sales, customers, reports, settings).

4. Database Management:

The system uses **MySQL** as the database, connected through **SQLAlchemy** (ORM) and the **PyMySQL** driver. Database connection settings are managed through environment variables loaded via **python-dotenv**.
