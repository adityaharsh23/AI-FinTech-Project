import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai

# Set your Gemini API key
genai.configure(api_key="API_KEY")

# Function to create a database and table from CSV
def create_database(csv_file, db_name="my_database.db", table_name="my_table"):
    try:
        df = pd.read_csv(csv_file)
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists='replace', index=False)  # Replace if table exists
        conn.close()
        return True, None  # Success, no error
    except Exception as e:
        return False, str(e)  # Failure, return error messageclear

# Function to execute SQL query and fetch results
def execute_query(db_name, query):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results, None
    except Exception as e:
        return None, str(e)


# Function to use Gemini for natural language to SQL conversion
def natural_language_to_sql(natural_language_query, table_name="my_table"):
    prompt = f"""Convert the following natural language query into a SQL query that can be executed on a table named {table_name}:
    Natural Language Query: {natural_language_query}
    SQL Query:"""

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    sql_query = response.text.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    return sql_query

# Streamlit app
st.title("Talk to your Stock Data")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file is not None:
    db_created, error_message = create_database(uploaded_file)

    if db_created:
        st.success("Database created successfully!")

        user_query = st.text_input("Enter your query (natural language):")

        if st.button("Submit"):
            if user_query:
                with st.spinner("Thinking..."):  # Show a spinner while processing
                    sql_query = natural_language_to_sql(user_query)

                    st.write("Generated SQL Query:")
                    st.code(sql_query, language="sql") # Display SQL in a code block

                    results, query_error = execute_query("my_database.db", sql_query)

                    if results:
                        st.write("Query Results:")
                        if results: # Check if Results are not empty
                            df_results = pd.DataFrame(results) # Convert to dataframe for better display
                            st.dataframe(df_results) # Display results as a dataframe
                        else:
                            st.write("No results found.")

                    elif query_error:
                        st.error(f"Error executing SQL query: {query_error}")

            else:
                st.warning("Please enter a query.")
    else:
        st.error(f"Error creating database: {error_message}")
