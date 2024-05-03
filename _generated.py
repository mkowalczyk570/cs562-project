
import os
import psycopg2
import psycopg2.extras
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
        n = n.split(",")

        v = ""
        while v == "":
            v = input("Enter grouping attributes: ")
        v = v.split(",")

        F = ""
        while F == "":
            F = input("Enter aggregate functions: ")
        F = F.replace("[", "")
        F = F.replace("]", "")
        F = F.split(",")

        sig = ""
        while sig == "":
            sig = input("Enter predicates: ")
        sig = sig.split(",")

        G = input("Enter having clause(optional): ")
        G = G.split(",") if G != "" else []
    else:
        print("Using file for input values")
        input_file = input("Enter the name of the file: ")
        with open(input_file, 'r') as f:
            for line in f:
                ## save each line as operator of phi
                # split line into attributes
                attributes = line.strip().split(",")
                if len(attributes) == 5 or len(attributes) == 6:
                    S = attributes[0]
                    n = attributes[1]
                    v = attributes[2]
                    F = attributes[3]
                    sig = attributes[4]
                    G = attributes[5] if len(attributes) == 6 else []
                else:
                    print("Invalid input")
                    break

    
    
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
            key = row[attr].lower()
            attributes.append(key)
        
        key = tuple(attributes)

        if key not in H_table:
            # if row contains a new combination of grouping attributes
            # add the grouping attributes to the H_table
            # initialize 0th grouping variable (assuming it's 0)
    
            for a in F[0]:
                count = 0
                a = a.split("_")                
                if a[0] == "min":
                    H_table[0] = row[a[1]]
                if a[0] == "max":
                    H_table[0] = row[a[1]]
                if a[0] == "sum":
                    H_table[0] = row[a[1]]
                if a[0] == "avg":
                    H_table[0] = row[a[1]]
                if a[0] == "count":
                    H_table[0] = 1
        else:
            # update the 0th grouping variable
            for a in F[0]:
                loc = H_table.index(key)
                print(loc)
                a = a.split("_")    
                count += 1            
                if a[0] == "min":
                    H_table[key] = min(row[a[1]], H_table[key])
                if a[0] == "max":
                    H_table[key] = max(row[a[1]], H_table[key])
                if a[0] == "sum":
                    H_table[key] += row[a[1]]
                if a[0] == "avg":
                    # incremental average
                    # avg = prev_avg + (new_val - prev_avg) / count

                    H_table[key] = H_table[key-1] + (row[a[1]] - H_table[key-1]) / count
                    H_table[key] = 0
                if a[0] == "count":
                    H_table[key] = count

    ### scan the table n times tocompute the aggregation functions of N grouping variables
    # for i in range(n):
    #     # iterate through the rows in table
    #     for row in cur:
    #         #if row satisfies the defining condition of the ith grouping variable
    #         if row[i] > 0:
    #             # get the row in H_table that matches ROW in sales table
    

    ### get 6 phi operators
    
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    