# MCP Data Analysis Assistant
# Connects to a PostgreSQL database to enable natural language queries via MCP
# Requirements: psycopg2-binary, a PostgreSQL database (e.g., Supabase)

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import asyncio
import os

# Database configuration
# Replace with your cloud PostgreSQL credentials (e.g., Supabase, ElephantSQL)
DB_CONFIG = {
    "dbname": "your_db_name",  # e.g., "postgres"
    "user": "your_username",   # e.g., "postgres"
    "password": "your_password",
    "host": "your_host",       # e.g., "db.supabase.co"
    "port": "5432"
}

# Simulated MCP Server class
class DataAnalysisMCPServer:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect_db()

    def connect_db(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Connected to PostgreSQL database")
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def diagnose(self):
        """Run diagnostic checks on the database"""
        try:
            # Check if 'sales' table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'sales'
                )
            """)
            table_exists = self.cursor.fetchone()['exists']
            print(f"Diagnostic: Table 'sales' {'exists' if table_exists else 'does not exist'}")
            
            if table_exists:
                # Check row count
                self.cursor.execute("SELECT COUNT(*) AS count FROM sales")
                row_count = self.cursor.fetchone()['count']
                print(f"Diagnostic: Table 'sales' contains {row_count} rows")
        except Exception as e:
            print(f"Diagnostic error: {e}")

    async def handle_tool_call(self, tool_name, parameters):
        """Handle tool calls from the LLM"""
        if tool_name == "execute_sql_query":
            return await self.execute_sql_query(parameters)
        elif tool_name == "get_table_schema":
            return await self.get_table_schema(parameters)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def execute_sql_query(self, parameters):
        """Execute a read-only SQL query and return results"""
        query = parameters.get("query")
        try:
            if not query.lower().startswith("select"):
                return {"error": "Only SELECT queries are allowed"}
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return {"results": [dict(row) for row in results]}
        except Exception as e:
            return {"error": f"Query execution failed: {e}"}

    async def get_table_schema(self, parameters):
        """Return schema for a specified table"""
        table_name = parameters.get("table_name")
        try:
            self.cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s
            """, (table_name,))
            schema = self.cursor.fetchall()
            return {"schema": [dict(row) for row in schema]}
        except Exception as e:
            return {"error": f"Schema retrieval failed: {e}"}

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")

# Tool definitions for the LLM
TOOLS = [
    {
        "name": "execute_sql_query",
        "description": "Execute a read-only SQL SELECT query on the database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The SQL SELECT query to execute"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_table_schema",
        "description": "Retrieve the schema of a specified database table",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "Name of the table"}
            },
            "required": ["table_name"]
        }
    }
]

# Mock LLM function to simulate tool calls
async def mock_llm_query(server, user_query):
    """Simulate LLM processing a user query and generating tool calls"""
    print(f"Processing user query: {user_query}")
    
    if "sales" in user_query.lower():
        # Get schema for 'sales' table
        schema_result = await server.handle_tool_call("get_table_schema", {"table_name": "sales"})
        print("Schema result:", json.dumps(schema_result, indent=2))
        
        # Handle specific queries
        if "total sales" in user_query.lower():
            sql_query = "SELECT product, SUM(quantity * price) as revenue FROM sales GROUP BY product"
            query_result = await server.handle_tool_call("execute_sql_query", {"query": sql_query})
            print("Query result:", json.dumps(query_result, indent=2))
            return {"response": f"Results for '{user_query}': {query_result}"}
        elif "sales for 2024" in user_query.lower():
            sql_query = "SELECT * FROM sales WHERE EXTRACT(YEAR FROM date) = 2024"
            query_result = await server.handle_tool_call("execute_sql_query", {"query": sql_query})
            print("Query result:", json.dumps(query_result, indent=2))
            return {"response": f"Results for '{user_query}': {query_result}"}
    
    return {"response": "No relevant query processed"}

# Main function
async def main():
    server = DataAnalysisMCPServer()
    try:
        # Run diagnostics
        server.diagnose()
        
        # Simulate a user query
        user_query = "Show total sales by product"
        result = await mock_llm_query(server, user_query)
        print("Final response:", result["response"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    asyncio.run(main())