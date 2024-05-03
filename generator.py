import subprocess


def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """

    body = """
    ### get 6 phi operators

    manual = input("Do you want to manually enter input values of phi? (y/n): ")
    if(manual == 'y'):
        print("Enter the values of S, n, v, F, sig, and G(optional):")
        print("for values with multiple inputs please separate by commas")
        S = ""
        while S == "":
            S = input("Enter select attributes: ")
        S = S.split(",")

        n = ""
        while n == "":
            n = input("Enter number of grouping variables: ")
        #n = n.split(",")
        n = int(n)

        v = ""
        while v == "":
            v = input("Enter grouping attributes: ")
        v = v.split(",")

        F = []
        for i in range(n+1):
            func = input("Enter aggregate functions for x_{}: ".format(i))
            func = func.split(",")
            F.append(func)

        sig = []
        for i in range(1, n+1):
            pred = input("Enter predicates for x_{}: ".format(i))
            pred = pred.split("and")
            sig.append(pred)
        #print(sig)

        G = input("Enter having clause(optional): ")
        G = G.split(",") if G != "" else []
    else:
        print("Using file for input values")
        input_file = input("Enter the name of the file: ")
        with open(input_file, 'r') as f:
            S_line = f.readline()
            S = S_line.strip().replace(" ", "").split(",")

            n = int(f.readline().strip())

            v_line = f.readline()
            v = v_line.strip().replace(" ", "").split(",")

            F = []
            for i in range(n+1):
                f_line = f.readline().replace(" ", "").strip()
                F.append(f_line)
            
            sig = []
            for i in range(n-1):
                sig_line = f.readline().strip()
                sig.append(re.split(r' (and|or) ', sig_line, flags=re.IGNORECASE))
            print(sig)
            
            G = ""
            g_line = f.readline()
            if g_line != "":
                G = g_line.strip()
            
            # for line in f:
            #     ## save each line as operator of phi
            #     # split line into attributes
            #     attributes = line.strip().split(",")
            #     if len(attributes) == 5 or len(attributes) == 6:
            #         S = attributes[0]
            #         n = attributes[1]
            #         v = attributes[2]
            #         F = attributes[3]
            #         sig = attributes[4]
            #         G = attributes[5] if len(attributes) == 6 else []
            #     else:
            #         print("Invalid input")
            #         break

    
    ### Create H-Table - holds grouping attributes (v) and aggregation functions (F)
    H_table= {};
    grouping_attributes = []
    aggregates = []

    for i in range(len(v)):
        grouping_attributes.append(v[i])


    # for i in range(len(F)):
    #     val = F[i].split("_")
    #     if val != "":
    #         aggregates.append(val[0])
    
    ### iterate through the rows in table
    for row in cur:
        # create a tuple of the grouping attributes
        attributes = []
        for attr in grouping_attributes:
            attr = attr.strip()
            key = row[attr].lower()
            attributes.append(key)
        
        key = tuple(attributes)

        if key not in H_table:
            # if row contains a new combination of grouping attributes
            # add the grouping attributes to the H_table
            # initialize 0th grouping variable (assuming it's 0)

            H_table[key] = {}
    
            for a in F[0]:
                count = 0
                inner_key = a
                a = a.split("_")    
                if inner_key not in H_table[key]: 
                    H_table[key][inner_key] = {}        
                if a[0] == "min":
                    H_table[key][inner_key] = row[a[1]]
                if a[0] == "max":
                    H_table[key][inner_key] = row[a[1]]
                if a[0] == "sum":
                    H_table[key][inner_key] = row[a[1]]
                if a[0] == "avg":
                    H_table[key][inner_key] = row[a[1]]
                if a[0] == "count":
                    H_table[key][inner_key] = 1
        else:
            # update the 0th grouping variable
            for a in F[0]:
                a = a.split("_")    
                count += 1            
                if a[0] == "min":
                    H_table[key][inner_key] = min(row[a[1]], H_table[key][inner_key])
                if a[0] == "max":
                    H_table[key][inner_key] = max(row[a[1]], H_table[key][inner_key])
                if a[0] == "sum":
                    H_table[key][inner_key] += row[a[1]]
                if a[0] == "avg":
                    # incremental average
                    # avg = prev_avg + (new_val - prev_avg) / count

                    H_table[key][inner_key] = H_table[key][inner_key] + (row[a[1]] - H_table[key][inner_key]) / count
                if a[0] == "count":
                    H_table[key][inner_key] = count
    
    
    ### scan the table n times to compute the aggregation functions of N grouping variables
    for i in range(n):
        cur.execute("SELECT * FROM sales")
        # iterate through the rows in table
        for row in cur:
            #if row satisfies the defining condition of the ith grouping variable
            # get condition for ith grouping variable
            condition = sig # EX: ['1.state="NY"', '1.cust="dan"']
            print(condition)
            for pred in condition:
                single_pred = pred[0].split("and")
                col = single_pred[0].split("=")[1].strip()
                print(col)
                


    """

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
import os
import psycopg2
import psycopg2.extras
import re
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():

## access database
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    port = os.getenv('PORT')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password + " port=" + port,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    _global = []
    {body}

    ### get 6 phi operators
    
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()
