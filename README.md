MCP Data Analysis Assistant
MCP Data Analysis Assistant: A Python tool using MCP to connect LLMs with PostgreSQL for natural language data queries. Securely executes SQL, retrieves schemas, and supports cloud databases. Includes sample dataset.
Installation

Clone the Repository:
git clone https://github.com/bharatydv/MCP-Data-Analysis-Assistant/blob/main/mcp_data_assistant.py
cd mcp-data-analysis-assistant


Install Dependencies:
pip install -r requirements.txt


Set Up PostgreSQL Database:

Create a cloud PostgreSQL database (e.g., Supabase).
Create a sales table:CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    date DATE
);
INSERT INTO sales (product, quantity, price, date) VALUES
('Product A', 100, 10.00, '2024-01-15'),
('Product B', 50, 20.00, '2024-02-10');


Update DB_CONFIG in mcp_data_assistant.py with your credentials.



Usage

Run the Script:
python mcp_data_assistant.py


Example Output:
Connected to PostgreSQL database
Diagnostic: Table 'sales' exists
Diagnostic: Table 'sales' contains 2 rows
Processing user query: Show total sales by product
Query result: {
  "results": [
    {"product": "Product A", "revenue": 1000.00},
    {"product": "Product B", "revenue": 1000.00}
  ]
}



Dataset
Sample dataset on Hugging Face: [Insert Hugging Face Dataset URL]
License
MIT License. See LICENSE.
Acknowledgments

MCP
psycopg2

