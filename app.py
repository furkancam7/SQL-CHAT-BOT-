import gradio as gr
import sqlite3
import os
import json
from google import genai
from google.genai import types

# Setup API key and client
api_key = "AIzaSyDjNXs_sBhkVK6AbfYb2n9jOdxk0Zr-TUg"
client = genai.Client(api_key=api_key)

def get_sql_query(query: str) -> str:
    """Generate a SQL query based on given user's prompt."""
    prompt = f"""
    Convert the following natural language query to SQL based on this e-commerce database schema:

    Tables:
    - Categories (CategoryID [PK], CategoryName, Description)
    - Customers (CustomerID [PK], CustomerName, ContactName, Address, City, PostalCode, Country)
    - Employees (EmployeeID [PK], LastName, FirstName, BirthDate, Photo, Notes)
    - Shippers (ShipperID [PK], ShipperName, Phone)
    - Suppliers (SupplierID [PK], SupplierName, ContactName, Address, City, PostalCode, Country, Phone)
    - Products (ProductID [PK], ProductName, SupplierID [FK->Suppliers], CategoryID [FK->Categories], Unit, Price)
    - Orders (OrderID [PK], CustomerID [FK->Customers], EmployeeID [FK->Employees], OrderDate, ShipperID [FK->Shippers])
    - OrderDetails (OrderDetailID [PK], OrderID [FK->Orders], ProductID [FK->Products], Quantity)

    Query: {query}

    IMPORTANT:
    - Return ONLY the raw SQL without any markdown formatting, comments, or backticks.
    - Always end SQL statements with a semicolon (;).
    - Use the exact column names for query (ProductName not "Product Name", etc.)
    - Do NOT assume information that is not explicitly mentioned in the database.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def get_sql_result(query: str):
    """Execute SQL query on SQLite database and return results as JSON."""
    try:
        db_path = 'company.db'
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file '{db_path}' not found.")

        cx = sqlite3.connect(db_path)
        cu = cx.cursor()
        cu.execute(query)
        results = cu.fetchall()
        column_names = [description[0] for description in cu.description]
        cu.close()
        cx.close()

        dict_results = [dict(zip(column_names, result)) for result in results]
        return json.dumps(dict_results, indent=4)

    except FileNotFoundError as fnf_error:
        return json.dumps({"error": str(fnf_error)}, indent=4)
    except sqlite3.Error as db_error:
        return json.dumps({"error": f"Database error: {str(db_error)}"}, indent=4)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=4)

# Setup chat with tools
config = {
    'tools': [get_sql_query, get_sql_result],
    'system_instruction': [
    """
    You are an ai asistant for a componay. You are connected to a SQLite database. In this database you have Tables:
      - Categories (CategoryID [PK], CategoryName, Description)
      - Customers (CustomerID [PK], CustomerName, ContactName, Address, City, PostalCode, Country)
      - Employees (EmployeeID [PK], LastName, FirstName, BirthDate, Photo, Notes)
      - Shippers (ShipperID [PK], ShipperName, Phone)
      - Suppliers (SupplierID [PK], SupplierName, ContactName, Address, City, PostalCode, Country, Phone)
      - Products (ProductID [PK], ProductName, SupplierID [FK->Suppliers], CategoryID [FK->Categories], Unit, Price)
      - Orders (OrderID [PK], CustomerID [FK->Customers], EmployeeID [FK->Employees], OrderDate, ShipperID [FK->Shippers])
      - OrderDetails (OrderDetailID [PK], OrderID [FK->Orders], ProductID [FK->Products], Quantity)


    As prompt, you are going to get natural language request in English or some other languages. Respond in the same language you get the prompt.

    Try to find the necessary information on the database for your responses. You can use your tools to generate sql queries and execute those queries.
    If prompt is not related to your databases, do NOT generate a response on your own. Kindly explain question is unrelated.
    """
        ],
}
'''
generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are an ai asistant for a componay. You are connected to a SQLite database. In this database you have Tables:
      - Categories (CategoryID [PK], CategoryName, Description)
      - Customers (CustomerID [PK], CustomerName, ContactName, Address, City, PostalCode, Country)
      - Employees (EmployeeID [PK], LastName, FirstName, BirthDate, Photo, Notes)
      - Shippers (ShipperID [PK], ShipperName, Phone)
      - Suppliers (SupplierID [PK], SupplierName, ContactName, Address, City, PostalCode, Country, Phone)
      - Products (ProductID [PK], ProductName, SupplierID [FK->Suppliers], CategoryID [FK->Categories], Unit, Price)
      - Orders (OrderID [PK], CustomerID [FK->Customers], EmployeeID [FK->Employees], OrderDate, ShipperID [FK->Shippers])
      - OrderDetails (OrderDetailID [PK], OrderID [FK->Orders], ProductID [FK->Products], Quantity)


    As prompt, you are going to get natural language request in English or some other languages. Respond in the same language you get the prompt.

    Try to find the necessary information on the database for your responses. You can use your tools to generate sql queries and execute those queries.
    """),
        ],
    )
'''

# Initialize the chat session
chat = client.chats.create(model='gemini-2.0-flash', config=config)

# Define the function that will be called when the interface is used
def process_input(message, history):
    # Send the user's query to the LLM
    response = chat.send_message(message)
    # Return the response text for the chat interface
    return response.text

theme = gr.themes.Citrus(
    primary_hue="orange",
    secondary_hue="orange",
    neutral_hue="slate",
    text_size="lg",
    spacing_size="sm",
    radius_size="xxl",
    font=[gr.themes.GoogleFont('Merriweather'), 'Merriweather', 'Merriweather', 'Merriweather'],
    font_mono=[gr.themes.GoogleFont('Merriweather'), 'Merriweather', 'Merriweather', 'Merriweather'],
).set(
    body_background_fill='*primary_100',
    body_text_color='black',
    body_text_size='16px',
    body_text_color_subdued='black',
    body_text_weight='100',
    embed_radius='*radius_xxl',
    background_fill_primary='*primary_100',
    background_fill_secondary='*primary_100',
    border_color_accent='orange',
    border_color_accent_subdued='white',
    border_color_primary='white',
    color_accent='white',
    color_accent_soft='white',
    code_background_fill='white',
    code_background_fill_dark='white',
    shadow_drop='white',
    shadow_spread='1.5px',
    shadow_spread_dark='2px',
    block_background_fill='*primary_50',
    block_border_color='*primary_200',
    block_border_width='3px',
    block_info_text_color='black',
    block_info_text_size='14px',
    block_info_text_weight='450',
    accordion_text_color='black',
    table_text_color='black',
    chatbot_text_size='18px',
    input_background_fill='white',
    button_border_width='2px',
    button_transform_hover='scale(0.9)',
    button_transform_active='scale(0.9)',
    button_transition='all 0.2s ease;',
    button_large_padding='*spacing_md',
    button_large_radius='*radius_xxl',
    button_large_text_size='18px',
    button_large_text_weight='400',
    button_small_padding='*spacing_md',
    button_small_radius='*radius_xxl',
    button_small_text_size='16px',
    button_small_text_weight='300',
    button_primary_background_fill='*primary_200',
    button_primary_background_fill_hover='*primary_200',
    button_primary_border_color='white',
    button_primary_border_color_hover='white',
    button_primary_text_color='black',
    button_primary_text_color_hover='black',
    button_primary_text_color_hover_dark='black',
    button_primary_shadow='*button_secondary_shadow_active',
)

# Gradio ChatInterface oluşturma
demo = gr.ChatInterface(
    fn=process_input,
    title="SQL Database Assistant",
    description="Ask questions about the database in natural language. The assistant will generate and execute SQL queries for you.",
    examples=[
        "List the top 5 customers by order count", 
        "What's the average price of products in each category?", 
        "Show orders from customers in Germany", 
        "List all products with price greater than $100",
        "List products served in bottles",
        "Give me an ideal dinner menu from your products"
    ],
    theme=theme
)


# Launch the interface
if __name__ == "__main__":
    demo.launch()