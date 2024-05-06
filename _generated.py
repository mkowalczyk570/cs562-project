
import os
import psycopg2
import psycopg2.extras
import re
import tabulate
from dotenv import load_dotenv
import numpy as np

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
    

    def eval(pred, cur):
    # This function should take in a predicate and evaluate it. It should return True or False.
        pred = pred.split(".")[1]
        att = re.split(r'(<=|>=|!=|<|>|=)', pred)

        # col_names = [desc[0] for desc in cur.description]

        # if att[2] in col_names:
        #     # handling a grouping variable
        #     ## group by prod --> prod = current prod being grouped
        #     att[2] = cur[]

        return att

    ### get 6 phi operators

    manual = input("Do you want to manually enter input values of phi? (y/n): ")
    if(manual == 'y'):
        print("Enter the values of S, n, v, F, sig, and G(optional):")
        print("for values with multiple inputs please separate by commas")
        S = ""
        while S == "":
            S = input("Enter select attributes: ")
        S = S.strip().replace(" ", "").split(",")

        n = ""
        while n == "":
            n = input("Enter number of grouping variables: ")
        #n = n.split(",")
        n = int(n.strip())

        v = ""
        while v == "":
            v = input("Enter grouping attributes: ")
        v = v.strip().replace(" ", "").split(",")

        F = []
        for i in range(n+1):
            func = input("Enter aggregate functions for x_{}: ".format(i))
            func = func.replace(" ", "").strip().split(",")
            F.append(func)

        sig = []
        for i in range(1, n+1):
            sig_line = input("Enter predicates for x_{}: ".format(i))
            sig_line = sig_line.strip()
            sig.append(re.split(r' (and|or) ', sig_line, flags=re.IGNORECASE))
        #print(sig)

        G = input("Enter having clause(optional): ")
        # G = G.split(",") if G != "" else []
        if G != "": G = re.split(r' (and|or) ', G.strip(), flags=re.IGNORECASE)
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
                f_line = f.readline().replace(" ", "").strip().split(",")
                F.append(f_line)
            
            sig = []
            for i in range(n):
                sig_line = f.readline().strip()
                sig.append(re.split(r' (and|or) ', sig_line, flags=re.IGNORECASE))
            
            G = ""
            g_line = f.readline()
            if g_line != "":
                G = re.split(r' (and|or) ', g_line.strip(), flags=re.IGNORECASE)
            
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
            key = row[attr]
            attributes.append(key)
        
        key = tuple(attributes)

        if key not in H_table:
            # if row contains a new combination of grouping attributes
            # add the grouping attributes to the H_table
            # initialize 0th grouping variable (assuming it's 0)

            H_table[key] = {}
    
            for a in F[0]:
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
                    H_table[key][inner_key + "_count"] = 1
                    H_table[key][inner_key] = row[a[1]]
                if a[0] == "count":
                    H_table[key][inner_key] = 1
        else:
            # update the 0th grouping variable
            for a in F[0]:
                inner_key = a
                a = a.split("_")    
                if a[0] == "min":
                    H_table[key][inner_key] = min(row[a[1]], H_table[key][inner_key])
                if a[0] == "max":
                    H_table[key][inner_key] = max(row[a[1]], H_table[key][inner_key])
                if a[0] == "sum":
                    H_table[key][inner_key] += row[a[1]]
                if a[0] == "avg":
                    # incremental average
                    # avg = prev_avg + (new_val - prev_avg) / count

                    H_table[key][inner_key + "_count"] += 1
                    H_table[key][inner_key] = H_table[key][inner_key] + (row[a[1]] - H_table[key][inner_key]) / H_table[key][inner_key + "_count"]
                if a[0] == "count":
                    H_table[key][inner_key] += 1
    
    
    ### scan the table n times to compute the aggregation functions of N grouping variables
    for i in range(n):
        cur.execute("SELECT * FROM sales")
        # iterate through the rows in table
        result = []
        predicates = []
        evaluated = False
        isAnd = False
        isOr = False
        condition = sig
        # 1. get list of all evaluated predicates
        # 2. Scan through table
        # 3. for each row, check row against each predicate (stopping when any is false for AND; stopping when any is true for OR)
        for pred in condition[i]:
            if not evaluated:
                pred_eval = eval(pred, cur)
                predicates.append(pred_eval)
                evaluated = True
            else:
                # check and vs or
                if pred == "and": isAnd = True
                elif pred == "or": isOr = True
                evaluated = False

        if not isAnd and not isOr: isOr = True
        for row in cur:
            for key in H_table.keys():
                isTrue = isAnd
                for pred_eval in predicates:
                    #check for grouping variable
                    col_names = [desc[0] for desc in cur.description]
                    match_value = ""

                    if pred_eval[2] in col_names:
                        index = v.index(pred_eval[2])
                        match_value = key[index]
                    elif pred_eval[2] in H_table[key].keys():
                        # TODO
                        match_value = H_table[key][pred_eval[2]]
                    else: match_value = pred_eval[2]
                    
                    if(pred_eval[1] == "="):
                        if isAnd:
                            if row[pred_eval[0]] != match_value: 
                                isTrue = False
                                break 
                        elif isOr:
                            if row[pred_eval[0]] == match_value: #true
                                isTrue = True
                                break
                    elif(pred_eval[1] == "<"):
                        if isAnd:
                            if row[pred_eval[0]] >= match_value: 
                                isTrue = False
                                break 
                        elif isOr:
                            if row[pred_eval[0]] < match_value: #true
                                IsTrue = True
                                break
                    elif(pred_eval[1] == ">"):
                        if isAnd:
                            if row[pred_eval[0]] <= match_value: 
                                isTrue = False
                                break 
                        elif isOr:
                            if row[pred_eval[0]] > match_value: #true
                                isTrue = True
                                break
                    elif(pred_eval[1] == "<="):
                        if isAnd:
                            if row[pred_eval[0]] > match_value: 
                                isTrue = False
                                break 
                        elif isOr:
                            if row[pred_eval[0]] <= match_value: #true
                                isTrue = True
                                break
                    elif(pred_eval[1] == ">="):
                        if isAnd:
                            if row[pred_eval[0]] < match_value: 
                                isTrue = False
                                break 
                        elif isOr:
                            if row[pred_eval[0]] >= match_value: #true
                                isTrue = True
                                break
                    elif(pred_eval[1] == "!="):
                        if isAnd:
                            if row[pred_eval[0]] == match_value: #false
                                isTrue = False
                                break 
                        elif isOr:
                            if row[pred_eval[0]] != match_value: #true
                                isTrue = True
                                break
                if not isTrue:
                    continue
                
                for attr in F[i+1]:
                    inner_key = attr
                    a = attr.split("_")
                    if inner_key not in H_table[key]: 
                        H_table[key][inner_key] = {}        
                    if a[0] == "min":
                        H_table[key][inner_key] = row[a[2]]
                    if a[0] == "max":
                        H_table[key][inner_key] = row[a[2]]
                    if a[0] == "sum":
                        H_table[key][inner_key] = row[a[2]]
                    if a[0] == "avg":
                        H_table[key][inner_key + "_count"] = 1
                        H_table[key][inner_key] = row[a[2]]
                    if a[0] == "count":
                        H_table[key][inner_key] = 1
                else:
                    for attr in F[i+1]:
                        inner_key = attr
                        a = attr.split("_")    
                        if a[0] == "min":
                            H_table[key][inner_key] = min(row[a[2]], H_table[key][inner_key])
                        if a[0] == "max":
                            H_table[key][inner_key] = max(row[a[2]], H_table[key][inner_key])
                        if a[0] == "sum":
                            H_table[key][inner_key] += row[a[2]]
                        if a[0] == "avg":
                            # incremental average
                            # avg = prev_avg + (new_val - prev_avg) / count

                            H_table[key][inner_key + "_count"] += 1
                            H_table[key][inner_key] = H_table[key][inner_key] + (row[a[2]] - H_table[key][inner_key]) / H_table[key][inner_key + "_count"]
                        if a[0] == "count":
                            H_table[key][inner_key] += 1
                result.append(row)
            #update H_table
        #print(result)  

    def eval_having(pred):
    # This function should take in a predicate and evaluate it. It should return True or False.
        # pred = pred.split(".")[1]
        attr = re.split(r'(<=|>=|!=|<|>|=)', pred)
        
        attr[2] = attr[2].replace(" ", "")
        attr[2] = re.split(r'(\+|\-|\*|\/)', attr[2])
        
        return attr
    
    def eval_sub(subexpr, key):
        i = 0
        isOperator = False
        operator = ""
        value = None
        while i < len(subexpr):
            if isOperator:
                operator = subexpr[i]
                isOperator = False
            else:
                temp = 0
                try:
                    temp = float(subexpr[i])
                except ValueError:
                    temp = H_table[key][subexpr[i]]
                if i == 0: value = temp
                else:
                    if operator == "+":
                        value += temp
                    elif operator == "-":
                        value -= temp
                    elif operator == "*":
                        value *= temp
                    elif operator == "/":
                        value /= temp
                    else:
                        raise ValueError("Unknown operator: " + operator)
                isOperator = True    
            i += 1
        return value

    # HAVING Clause
    # iterate through H_table
    # if row satisfies having, select based on S
    output = []

    for key in H_table.keys():
        having_conds = []
        evaluated = False
        isAnd = False
        isOr = False
        for cond in G:
            if not evaluated:
                e_cond = eval_having(cond)
                e_cond[2] = eval_sub(e_cond[2], key)
                having_conds.append(e_cond)
                evaluated = True
            else:
                if cond == "and": isAnd = True
                elif cond == "or": isOr = True
                evaluated = False
        
        # TODO: continue
        isMatch = isAnd
        for cond in having_conds:
            table_value = H_table[key][cond[0].strip()]
            cond_value = cond[2]
            if cond[1] == "=":
                if isAnd:
                    if table_value != cond_value:
                        isMatch = False
                        break
                else:
                    if table_value == cond_value:
                        isMatch = True
                        break
            elif cond[1] == "<":
                if isAnd:
                    if table_value >= cond_value:
                        isMatch = False
                        break
                else:
                    if table_value < cond_value:
                        isMatch = True
                        break
            elif cond[1] == ">":
                if isAnd:
                    if table_value <= cond_value:
                        isMatch = False
                        break
                else:
                    if table_value > cond_value:
                        isMatch = True
                        break
            elif cond[1] == "<=":
                if isAnd:
                    if table_value > cond_value:
                        isMatch = False
                        break
                else:
                    if table_value <= cond_value:
                        isMatch = True
                        break
            elif cond[1] == ">=":
                if isAnd:
                    if table_value < cond_value:
                        isMatch = False
                        break
                else:
                    if table_value >= cond_value:
                        isMatch = True
                        break
            elif cond[1] == "!=":
                if isAnd:
                    if table_value == cond_value:
                        isMatch = False
                        break
                else:
                    if table_value != cond_value:
                        isMatch = True
                        break
        if G and not isMatch: continue
        group = []
        for attr in S:
            value = None
            if attr in v: value = key[v.index(attr)]
            else: value = H_table[key][attr]
            group.append(value)
        output.append(group)
    print(output)
        

    

    ### get 6 phi operators
    
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    