import streamlit as st
import mysql.connector
import pandas as pd

# Connect to MySQL database
mydb = mysql.connector.connect(host="localhost",
                               user="myuser",
                               password="P@ssw0rd!123_#",
                               database="bank")
mycursor = mydb.cursor()

# Function to insert customer data
def acc_insert():
    st.subheader("Add Customer")
    accno = st.text_input("Enter the account number")
    name = st.text_input("Enter the Customer Name")
    age = st.number_input("Enter Age of Customer", min_value=0)
    occupation = st.text_input("Enter the Customer Occupation")
    address = st.text_input("Enter the Address of the Customer")
    mobile = st.text_input("Enter the Mobile number")
    aadharno = st.text_input("Enter the Aadhaar number")
    balance = st.number_input("Enter the Money Deposited", min_value=0.0)
    acc_type = st.selectbox("Enter the account Type", ["Saving", "RD", "PPF", "Current"])
    
    if st.button("Submit"):
        cust_data = (accno, name, age, occupation, address, mobile, aadharno, balance, acc_type)
        sql = '''INSERT INTO account(accno, name, age, occupation, address, mobile, aadharno, balance, acctype)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        mycursor.execute(sql, cust_data)
        mydb.commit()
        st.success("Customer added successfully!")

# Function to view customer data
# Function to view customer data
def acc_view():
    st.subheader("View Customer")
    search_criteria = st.selectbox("Select the search criteria", ["Acc no", "Name", "Mobile", "aadhaarno", "View All"])
    if search_criteria == "View All":
        sql = "SELECT account.*, amount.Amtdeposit, amount.Month FROM account INNER JOIN amount ON account.Accno = amount.Accno"
        mycursor.execute(sql)
        results = mycursor.fetchall()
        if results:
            df = pd.DataFrame(results, columns=['Id', 'Acc no', 'Name', 'Age', 'Occupation', 'Address', 'Mobile', 'aadhaarno', 'Balance', 'Acc Type', 'Amount Deposited', 'Month'])
            st.write(df)
        else:
            st.warning("No records found.")
    else:
        search_term = st.text_input(f"Enter {search_criteria}")
        if st.button("Search"):
            if search_criteria == "Acc no":
                sql = f'SELECT account.*, amount.Amtdeposit, amount.Month FROM account INNER JOIN amount ON account.Accno = amount.Accno WHERE account.accno = "{search_term}"'
            elif search_criteria == "Name":
                sql = f'SELECT account.*, amount.Amtdeposit, amount.Month FROM account INNER JOIN amount ON account.Accno = amount.Accno WHERE account.name LIKE "%{search_term}%"'
            elif search_criteria == "Mobile":
                sql = f'SELECT account.*, amount.Amtdeposit, amount.Month FROM account INNER JOIN amount ON account.Accno = amount.Accno WHERE account.mobile LIKE "%{search_term}%"'
            elif search_criteria == "aadhaarno":  
                sql = f'SELECT account.*, amount.Amtdeposit, amount.Month FROM account INNER JOIN amount ON account.Accno = amount.Accno WHERE account.aadhaarno LIKE "%{search_term}%"'  
            mycursor.execute(sql)
            results = mycursor.fetchall()
            if results:
                df = pd.DataFrame(results, columns=['Id', 'Acc no', 'Name', 'Age', 'Occupation', 'Address', 'Mobile', 'aadhaarno', 'Balance', 'Acc Type', 'Amount Deposited', 'Month'])
                st.write(df)
            else:
                st.warning("No records found.")


# Function to withdraw money
def acc_withdraw():
    st.subheader("Withdraw Money")
    accno = st.text_input("Enter the account number")
    amount = st.number_input("Enter the Amount to be withdrawn", min_value=0.0)
    remark = st.text_input("Enter remark for Withdrawal")
    
    if st.button("Withdraw"):
        sql_select = "SELECT * FROM account WHERE accno = %s AND balance >= %s"
        mycursor.execute(sql_select, (accno, amount))
        result = mycursor.fetchone()
        if result:
            sql_insert = "INSERT INTO amount(Accno, Amtdeposit, month) VALUES (%s, -%s, %s)"
            sql_update = "UPDATE account SET balance = balance - %s WHERE accno = %s"
            try:
                mycursor.execute(sql_insert, (accno, amount, remark))
                mycursor.execute(sql_update, (amount, accno))
                mydb.commit()
                st.success("Amount withdrawn successfully!")
                st.info(f"Updated balance is: {get_updated_balance(accno)}")
            except mysql.connector.Error as err:
                st.error(f"Error: {err.msg}")
        else:
            st.warning("Not enough balance available")

# Function to close account
def close_acc():
    st.subheader("Close Account")
    accno = st.text_input("Enter the account number")
    if st.button("Close Account"):
        try:
            sql_delete_amount = "DELETE FROM amount WHERE Accno = %s"
            sql_delete_account = "DELETE FROM account WHERE Accno = %s"
            mycursor.execute(sql_delete_amount, (accno,))
            mycursor.execute(sql_delete_account, (accno,))
            mydb.commit()
            st.success("Account closed successfully!")
        except mysql.connector.Error as err:
            st.error(f"Error: {err.msg}")

# Function to get updated balance
def get_updated_balance(accno):
    sql = "SELECT balance FROM account WHERE accno = %s"
    mycursor.execute(sql, (accno,))
    result = mycursor.fetchone()
    if result:
        return result[0]
    else:
        return "N/A"

# Main function to run the application
def main():
    st.title("Bank Management System")
    menu = ["Add Customer", "View Customer", "Deposit Money", "Withdraw Money", "Close Account"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Add Customer":
        acc_insert()
    elif choice == "View Customer":
        acc_view()
    elif choice == "Deposit Money":
        acc_deposit()
    elif choice == "Withdraw Money":
        acc_withdraw()
    elif choice == "Close Account":
        close_acc()

if __name__ == "__main__":
    main()
