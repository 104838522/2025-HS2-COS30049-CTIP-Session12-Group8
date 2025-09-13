import os
import pandas as pd
# from IPython.#display import #display
import re   # Regular expressions
import numpy as np  # Numerical computations

# Step 1: Collect all source code files inside the testcases folder
testcase_dir = "data/testcases"

data = []
for root, dirs, files in os.walk(testcase_dir):
    for file in files:
        if file.endswith((".c", ".cpp", ".h")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_text = f.read()
                data.append([file_path, code_text])
                # Progress indicator
                if len(data) % 100 == 0:
                    print(f"{len(data)} files read...")

            except Exception as e:
                print(f"Failed to read: {file_path}, error: {e}")

#--------------------------------------Data cleaning----------------------------------------^ 
# Step 2: Initial DataFrame creation and basic cleaning file level
df = pd.DataFrame(data, columns=["file_path", "code"])
print("Total files:", len(df))
#display(df.head())


# 1. Delete empty files
df = df[df["code"].str.strip() != ""]
print("After deleting empty files:", len(df))
#display(df.head())

# 2. Delete duplicate code samples
df = df.drop_duplicates(subset=["code"], keep="first")
print("After deleting duplicate code samples:", len(df))
#display(df.head())

# 3. Delete files with unwanted keywords in the filename
exclude_keywords = ["README", "readme", ".txt", ".md", "CMakeLists", "Makefile","main.cpp","main_linux","testcase.h"]
pattern = "|".join(exclude_keywords)  # "README|readme|.txt|.md|CMakeLists|Makefile|main.cpp|main_linux|testcase.h"
df = df[~df["file_path"].str.contains(pattern, case=False, na=False)]

print("After deleting files with unwanted keywords:", len(df))
#display(df.head())

#Cureent Colums {"file_path", "code"}

#------------------------------------------------------------------------------^ 
# Step 3: Data Cleaning code level code column

#  1. function to remove comments
def remove_comments(code: str) -> str:
    # /* ... */ delete block comments
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL) #reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    # // delete line comments
    code = re.sub(r"//.*", "", code) #reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    return code

# add a new column
df["code_no_comments"] = df["code"].apply(remove_comments)
# delete a old column
df = df.drop(columns=["code"], errors="ignore")
print("Completed removing comments")
#display(df.head())


#  2. function to normalize whitespace
def normalize_whitespace(code: str) -> str:
    # tab -> space
    code = code.replace("\t", " ")
    # continuous spaces -> single space
    code = re.sub(r" +", " ", code)
    # multiple newlines -> single newline
    code = re.sub(r"\n\s*\n", "\n", code)
    # trim leading/trailing whitespace
    return code.strip()

# add a new column
df["code_normalized"] = df["code_no_comments"].apply(normalize_whitespace)
# delete a old column
df = df.drop(columns=["code_no_comments"], errors="ignore")
print("Completed normalizing whitespace")
#display(df.head())


# 3. Split code into functions
def split_functions(code: str):
    pattern = re.compile(
        r"[a-zA-Z_][a-zA-Z0-9_]*\s+\**[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\{[^}]*\}",#reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
        re.DOTALL
    )
    # Extract all function blocks from the input code string as a list
    matches = pattern.findall(code)
    # If at least one function pattern is found, return the list; otherwise return the entire code in a list
    return matches if matches else [code]


# add a new column and explode into multiple rows
df = df.assign(functions=df["code_normalized"].apply(split_functions)).explode("functions").reset_index(drop=True)#reference: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html
#df.assing(functions=...) → add a new column named "functions"
#df["code_normalized"].apply(split_functions) → apply the split_functions to each row in the "code_normalized" column
#.explode("functions") → create a new row for each element in the "functions" list
#.reset_index(drop=True) → reset the index after exploding

# delete a old column
df = df.drop(columns=["code_normalized"], errors="ignore")
print("The total number of samples (function blocks):", len(df))
#display(df.head())

#Cureent Colums {"file_path", "functions"}
#------------------------------------------------------------------------------^ 
# Step 4: Add  id, language, Vulnerability ID / Type columns(metadata)

#  1. ID 
df = df.reset_index(drop=True)  
df["id"] = df.index + 1         # ID starts from 1

#  2. Language
def detect_language(path: str) -> str:
    if path.endswith(".c") or path.endswith(".h"):
        return "C"
    elif path.endswith(".cpp"):
        return "C++"
    else:
        return "Unknown"

df["language"] = df["file_path"].apply(detect_language)

# 3. Vulnerability ID  (Only CWE "number")

# ex: CWE121 → 121
df["vulnerability_cwe_id"] = df["file_path"].str.extract(r"CWE(\d+)")
df["vulnerability_cwe_id"] = df["vulnerability_cwe_id"].fillna("0").astype(int)  # fill NaN with 0 and convert to int

print("Complete ID and Language & vulnerability_cwe_id columns")
#display(df.head())
#Cureent Colums {"file_path", "functions", "id", "language", "vulnerability_cwe_id"}

#------------------------------------------------------------------------------^ 
#Step 5: Vulnerable / Safe labeling (

df["label"] = "unknown"  # default label

# vulnerable label
df.loc[
    df["functions"].str.contains("bad", case=False, na=False) |
    df["file_path"].str.contains("bad", case=False, na=False),
    "label"
] = "vulnerable"

# safe label
df.loc[
    df["functions"].str.contains("good", case=False, na=False) |
    df["file_path"].str.contains("good", case=False, na=False),
    "label"
] = "safe"

#delete old column
df = df.drop(columns=["file_path"], errors="ignore")
print("Completed labeling")
#display(df.head())

#Cureent Colums {"functions", "id", "language", "vulnerability_cwe_id",  "label"}

#------------------------------------------------------------------------------^
#  Step 6: Handle missing values (NaN)

# Check missing values
print("The number of missing values :\n", df.isna().sum())

# delete rows with 'unknown' label
df = df[df["label"] != "unknown"]

# # If there are missing values, remove them (dropna)  or replace with default values (fillna)

#if any column has NaN in 'functions', drop those rows
df = df.dropna(subset=["functions"])

# fill unknown or 0 for other columns
df = df.fillna({
    "language": "Unknown",
    "vulnerability_cwe_id": "0"
})
df["vulnerability_cwe_id"] = df["vulnerability_cwe_id"].astype(int)



print("Completed handling missing values")
#display(df.head())
#Cureent Colums {"functions", "id", "language", "vulnerability_cwe_id", "label"}

#--------------------------------Transformation----------------------------------------------^
#  Step 7: One-Hot Encoding (language) & 
# 1.mapping label to integers (safe:0, vulnerable:1)
df["label_encoded"] = df["label"].map({
    "safe": 0,
    "vulnerable": 1
})
# delete old column
df = df.drop(columns=["label"], errors="ignore")
print(df["label_encoded"].head())

# 2. language → One-Hot Encoding
language_onehot = pd.get_dummies(df["language"], prefix="lang").astype(int)

# combine with the original dataframe
df = pd.concat([df, language_onehot], axis=1)

# delete old column
df = df.drop(columns=["language"], errors="ignore")
print("One-Hot Encoding completed")
#Cureent Colums {"functions", "id", "vulnerability_cwe_id",  "label_encoded", "lang_C", "lang_C++", "lang_Unknown"}

#------------------------------------------------------------------------------^
# Step 8: Tokenization

def tokenize_code(code: str):
    
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|\d+|==|!=|<=|>=|[{}();,+\-*/<>]", code)
    return tokens

# add a new column
df["tokens"] = df["functions"].apply(tokenize_code)
print("Completed tokenization")
# delete old column
df = df.drop(columns=["functions"], errors="ignore")

#display(df["tokens"].head())
#Cureent Colums {"id", "vulnerability_cwe_id", "label_encoded", "lang_C", "lang_C++", "lang_Unknown", "tokens"}

#------------------------------------------------------------------------------^
#  Step 9: Normalization
#  C & C++ keywords set
keywords = { # reference:  https://www.w3schools.com/c/c_ref_keywords.php & https://www.w3schools.com/cpp/cpp_ref_keywords.asp
    # C keywords
    "auto","break","case","char","const","continue","default","do","double","else",
    "enum","extern","float","for","goto","if","inline","int","long","register",
    "restrict","return","short","signed","sizeof","static","struct","switch",
    "typedef","union","unsigned","void","volatile","while","_Alignas","_Alignof",
    "_Atomic","_Bool","_Complex","_Generic","_Imaginary","_Noreturn",
    "_Static_assert","_Thread_local",

    # C++ keywords
    "alignas","alignof","asm","bool","catch","char16_t","char32_t","class","constexpr",
    "const_cast","delete","dynamic_cast","explicit","export","false","friend","mutable",
    "namespace","new","noexcept","nullptr","operator","private","protected","public",
    "reinterpret_cast","static_assert","static_cast","template","this","thread_local",
    "throw","true","try","typename","using","virtual","wchar_t"
}

def normalize_tokens(tokens):
    normalized = []
    for token in tokens:

        if token.isdigit():  # digit -> <NUM>
            normalized.append("<NUM>")
        elif re.match(r'".*"', token) or re.match(r"'.*'", token):  # string -> <STR>
            normalized.append("<STR>")
        elif re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", token):  # identifier
            if token in keywords:
                normalized.append(token)  # keep keywords as is
            else:
                normalized.append("<VAR>")
        else:
            normalized.append(token)  # keep operators and others as is

    return normalized

df["tokens_normalized"] = df["tokens"].apply(normalize_tokens)

print("Completed normalization")
# delete old column
df = df.drop(columns=["tokens"], errors="ignore")

#display(df[ "tokens_normalized"].head())
#Cureent Colums {"id", "vulnerability_cwe_id",  "label_encoded", "lang_C", "lang_C++", "lang_Unknown", "tokens_normalized"}

#-----------------------Feature Engineering------------------------------------------------^
#  Step 10: Feature engineering: TF-IDF Vectorization
from sklearn.feature_extraction.text import TfidfVectorizer

# 1) transform tokens list to string
df["tokens_str"] = df["tokens_normalized"].apply(lambda x: " ".join(x))
# delete old column
df = df.drop(columns=["tokens_normalized"], errors="ignore")  

# 2) Apply TF-IDF 
vectorizer = TfidfVectorizer() #Create tf-idf vectorizer object
X_tfidf = vectorizer.fit_transform(df["tokens_str"]) #transform the text data into TF-IDF feature matrix

print("TF-IDF Feature Matrix shape(samples,colums):", X_tfidf.shape)# => (The num of functions,The nun of colunms)

# 3) Create a DataFrame from the TF-IDF matrix
tfidf_df = pd.DataFrame(
    X_tfidf.toarray(),
    columns=vectorizer.get_feature_names_out()
)
#display(tfidf_df.head())

# delete old column
df = df.drop(columns=["tokens_str"], errors="ignore")

# Combine the original df with the tfidf_df
df_final = pd.concat([df.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)

print("final DataFrame shape:", df_final.shape)
#display(df_final.head())

#-----------------------Final Save----------------------------------------------------^
# # step 11: Save final processed dataset

# CSV file 
output_path_csv_final = "processed_dataset_final.csv"
df_final.to_csv(output_path_csv_final, index=False, encoding="utf-8-sig")
print(f"completed final csv file path: {output_path_csv_final}")

# JSON Lines files
output_path_jsonl_final = "processed_dataset_final.jsonl"
df_final.to_json(output_path_jsonl_final, orient="records", lines=True, force_ascii=False)
print(f"completed final jsonl file path : {output_path_jsonl_final}")
