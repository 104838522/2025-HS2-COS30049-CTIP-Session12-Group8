import os
import pandas as pd
# from IPython.#display import #display
import re   # Regular expressions
import numpy as np  # Numerical computations
import json
import re

#--------------------------------------------------------
# Juliet dataset processing
#--------------------------------------------------------
# Juliet dataset: Step 1: Collect all source code files inside the testcases folder
#--------------------------------------------------------
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

#--------------------------------------Data cleaning (file level)----------------------------------------^ 
# Juliet dataset: Step 2: Initial DataFrame creation and basic cleaning 
#------------------------------------------------------------------------------^
df_juliet = pd.DataFrame(data, columns=["file_path", "code"])
print("Total files:", len(df_juliet))
#display(df_juliet.head())


# 1. Delete empty files
df_juliet = df_juliet[df_juliet["code"].str.strip() != ""]
print("After deleting empty files:", len(df_juliet))
#display(df_juliet.head())

# 2. Delete duplicate code samples
df_juliet = df_juliet.drop_duplicates(subset=["code"], keep="first")
print("After deleting duplicate code samples:", len(df_juliet))
#display(df_juliet.head())

# 3. Delete files with unwanted keywords in the filename
exclude_keywords = ["README", "readme", ".txt", ".md", "CMakeLists", "Makefile","main.cpp","main_linux","testcase.h"]
pattern = "|".join(exclude_keywords)  # "README|readme|.txt|.md|CMakeLists|Makefile|main.cpp|main_linux|testcase.h"
df_juliet = df_juliet[~df_juliet["file_path"].str.contains(pattern, case=False, na=False)]

print("After deleting files with unwanted keywords:", len(df_juliet))
#display(df_juliet.head())

#Cureent Colums {"file_path", "code"}

#-----------------------------------------Data cleaning (code level)-------------------------------------^ 
# Juliet dataset: Step 3: Data Cleaning code level code column
#------------------------------------------------------------------------------^
#  1. function to remove comments
def remove_comments(code: str) -> str:
    # /* ... */ delete block comments - reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL) 
    # // delete line comments - reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    code = re.sub(r"//.*", "", code) 
    return code

# add a new column
df_juliet["code_no_comments"] = df_juliet["code"].apply(remove_comments)
# delete a old column
df_juliet = df_juliet.drop(columns=["code"], errors="ignore")
print("Completed removing comments")
#display(df_juliet.head())


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
df_juliet["code_normalized"] = df_juliet["code_no_comments"].apply(normalize_whitespace)
# delete a old column
df_juliet = df_juliet.drop(columns=["code_no_comments"], errors="ignore")
print("Completed normalizing whitespace")
#display(df_juliet.head())


# 3. Split code into functions
def split_functions(code: str):
    results = []
    header_pattern = re.compile(
        #reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
        r'(?:^|\n)\s*'                                          # Usually at the beginning of a line, start of function header
        r'(?:template\s*<[^>{}]*>\s*)*'                         # template<...> 
        r'(?:\[\[[^\]]*\]\]\s*)*'                               # [[attributes]] 
        r'(?:[A-Za-z_][A-Za-z0-9_\s\*\&\(\),:<>~]*\s+)?'        # Return type / scope / modifiers (for constructors, optional)
        r'(?!(?:if|for|while|switch|catch|return|sizeof)\b)'    # Exclude control statements
        r'([A-Za-z_][A-Za-z0-9_:<>~]*|operator[^\s(]*)\s*'      # Function name or operator=, operator<<, operator()
        r'\([^;{}]*\)\s*'                                       # Parameters (...)
        r'(?:->\s*[A-Za-z_][A-Za-z0-9_:<>\s\*\&]+)?\s*'         # Trailing return type: -> T 
        r'(?:\s*(?:const|noexcept(?:\s*\([^)]*\))?|override|final|throw\s*\([^)]*\)))*\s*'  # Modifiers 
        r'\{',                                                  # Start of function body
        flags=re.M | re.S
    )

    for m in header_pattern.finditer(code):
        start = m.start()
        open_brace_idx = code.find('{', m.end() - 1)
        if open_brace_idx == -1:
            continue

        # find matching closing brace "}"
        depth = 0
        idx = open_brace_idx
        while idx < len(code):
            ch = code[idx]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    results.append(code[start:idx+1])
                    break
            idx += 1

    # return list of functions or empty list if none found
    return results




# add a new column and explode into multiple rows
df_juliet = df_juliet.assign(functions=df_juliet["code_normalized"].apply(split_functions)).explode("functions").reset_index(drop=True)#reference: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html
#-> add a new column named "functions"
#-> apply the split_functions to each row in the "code_normalized" column
#-> create a new row for each element in the "functions" list
#-> reset the index after exploding

# Remove NaN values and empty strings
df_juliet = df_juliet.dropna(subset=["functions"])
df_juliet = df_juliet[df_juliet["functions"].map(lambda x: isinstance(x, str) and x.strip() != "")]
df_juliet = df_juliet.reset_index(drop=True)
# delete a old column
df_juliet = df_juliet.drop(columns=["code_normalized"], errors="ignore")
print("The total number of samples (function blocks):", len(df_juliet))
#display(df_juliet.head())

#Cureent Columns {"file_path", "functions"}
#------------------------------------------------------------------------------^ 
# Juliet dataset: Step 4: Add  id, language, Vulnerability ID / Type columns(metadata)
#------------------------------------------------------------------------------^
#  1. ID 
df_juliet = df_juliet.reset_index(drop=True)  
df_juliet["id"] = df_juliet.index + 1         # ID starts from 1

#  2. Language
def detect_language(path: str) -> str:
    if path.endswith(".c") or path.endswith(".h"):
        return "C"
    elif path.endswith(".cpp"):
        return "C++"
    else:
        return "Unknown"

df_juliet["language"] = df_juliet["file_path"].apply(detect_language)

# 3. Vulnerability Type
# ex: CWE121_Stack_Based_Buffer_Overflow -> "Stack_Based_Buffer_Overflow"
df_juliet["vulnerability_type"] = df_juliet["file_path"].str.extract(r"CWE\d+_(.+?)(?:[\\/]|$)")

# NaN value -> Unknown
df_juliet["vulnerability_type"] = df_juliet["vulnerability_type"].fillna("Unknown")


print("Complete ID and Language & vulnerability_type columns")
#display(df_juliet.head())
#Cureent Colums {"file_path", "functions", "id", "language", "vulnerability_type"}

#------------------------------------------------------------------------------^ 
# Juliet dataset: Step 5: Vulnerable / Safe labeling 
#------------------------------------------------------------------------------^
# extract function name from code
def get_function_name(code: str):
    if not isinstance(code, str):
        return "" # early return for non-string inputs
    #reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    pattern = re.compile(
        r"\s*"
        r"(?:template\s*<[^>{}]*>\s*)*"                       # template<...> 
        r"(?:\[\[[^\]]*\]\]\s*)*"                             # [[attributes]] 
        r"(?:[A-Za-z_][A-Za-z0-9_\s\*\&\(\),:<>~]*\s+)?"      # Return type / scope / modifiers 
        r"(?!(?:if|for|while|switch|catch|return|sizeof)\b)"  # Exclude control statements
        r"([A-Za-z_][A-Za-z0-9_:<>~]*|operator[^\s(]*)\s*"    # Function name / scope or operator
        r"\(",                                                # Start of parameters
        flags=re.M | re.S                                     # Multiline and dotall flags
    )
    m = pattern.match(code)
    return m.group(1) if m else ""


df_juliet["func_name"] = df_juliet["functions"].apply(get_function_name)

#labeling based on function name
df_juliet["label"] = "unknown"
df_juliet.loc[df_juliet["func_name"].str.contains("good", case=False, na=False), "label"] = "safe"
df_juliet.loc[df_juliet["func_name"].str.contains("bad", case=False, na=False), "label"] = "vulnerable"


#delete old column
df_juliet = df_juliet.drop(columns=["file_path"], errors="ignore")
df_juliet = df_juliet.drop(columns=["func_name"], errors="ignore")
print("Completed labeling")

#Cureent Colums {"functions", "id", "language", "vulnerability_type",  "label"}

#------------------------------------------------------------------------------^
# Juliet dataset: Step 6: Handle missing values (NaN)
#------------------------------------------------------------------------------^
# Check missing values
print("The number of missing values :\n", df_juliet.isna().sum())

# delete rows with 'unknown' label
df_juliet = df_juliet[df_juliet["label"] != "unknown"]

# # If there are missing values, remove them (dropna)  or replace with default values (fillna)

#if any column has NaN in 'functions', drop those rows
df_juliet = df_juliet.dropna(subset=["functions"])

# fill unknown or 0 for other columns
df_juliet = df_juliet.fillna({
    "language": "Unknown",
    "vulnerability_type": "Unknown"
})



print("Completed handling missing values")
#display(df_juliet.head())
#Cureent Colums {"functions", "id", "language", "vulnerability_type", "label"}

#--------------------------------Transformation----------------------------------------------^
#  Juliet dataset: Step 7: One-Hot Encoding (language) & Label Encoding (label)
#------------------------------------------------------------------------------^
# 1.mapping label to integers (safe:0, vulnerable:1)
df_juliet["label_encoded"] = df_juliet["label"].map({
    "safe": 0,
    "vulnerable": 1
})
# delete old column
df_juliet = df_juliet.drop(columns=["label"], errors="ignore")
print(df_juliet["label_encoded"].head())

# 2. language → One-Hot Encoding
language_onehot = pd.get_dummies(df_juliet["language"], prefix="lang").astype(int)

# combine with the original dataframe
df_juliet = pd.concat([df_juliet, language_onehot], axis=1)

# delete old column
df_juliet = df_juliet.drop(columns=["language"], errors="ignore")
print("One-Hot Encoding completed")
#Cureent Colums {"functions", "id", "vulnerability_type",  "label_encoded", "lang_C", "lang_C++", "lang_Unknown", ...}

#------------------------------------------------------------------------------^
# Juliet dataset: Step 8: Tokenization
#------------------------------------------------------------------------------^
def tokenize_code(code: str):
    
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|\d+|==|!=|<=|>=|[{}();,+\-*/<>]", code)
    return tokens

# add a new column
df_juliet["tokens"] = df_juliet["functions"].apply(tokenize_code)
print("Completed tokenization")
# delete old column
df_juliet = df_juliet.drop(columns=["functions"], errors="ignore")

#display(df_juliet["tokens"].head())
#Cureent Colums {"id", "vulnerability_type", "label_encoded", "lang_C", "lang_C++", "lang_Unknown", "tokens"}

#------------------------------------------------------------------------------^
#  Juliet dataset: Step 9: Normalization
#------------------------------------------------------------------------------^
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

df_juliet["tokens_normalized"] = df_juliet["tokens"].apply(normalize_tokens)

print("Completed normalization")
# delete old column
df_juliet = df_juliet.drop(columns=["tokens"], errors="ignore")

#------------------------------------------------------------------------------^
# Juliet dataset: Step 10: Remove too short or meaningless functions (quality filtering)
#------------------------------------------------------------------------------^
# minimum number of tokens to keep a function
MIN_TOKENS = 10  

df_juliet["token_count"] = df_juliet["tokens_normalized"].apply(len)
df_juliet = df_juliet[df_juliet["token_count"] >= MIN_TOKENS]

# only more than 10 tokens
df_juliet = df_juliet.drop(columns=["token_count"], errors="ignore")

#display(df_juliet[ "tokens_normalized"].head())
#Cureent Colums {"id", "vulnerability_type",  "label_encoded", "lang_C", "lang_C++", "lang_Unknown", "tokens_normalized"}

#------------------------------------------------------------------------------^
#   basic_data_3.jsonl
#------------------------------------------------------------------------------^
# Basic_data: Step 1: Load JSONL dataset
#------------------------------------------------------------------------------^
records = []
with open("basic_data_3.jsonl", "r", encoding="utf-8") as f:
    buffer = ""
    for line in f:
        line = line.strip()
        if not line:
            continue
        buffer += line
        if line.endswith("}"):
            try:
                records.append(json.loads(buffer))
            except:
                pass
            buffer = ""

df_basic = pd.DataFrame(records)
print("Total samples:", len(df_basic))

#------------------------------------------------------------------------------^
# Basic_data: Step 2: Keep required columns
#------------------------------------------------------------------------------^
df_basic = df_basic[["language", "vulnerability_type", "code_snippet"]].copy()
df_basic.rename(columns={"code_snippet": "code"}, inplace=True)

# Assign ID
df_basic = df_basic.reset_index(drop=True)
df_basic["id"] = df_basic.index + 1

# Label: all vulnerable
df_basic["label_encoded"] = 1

#------------------------------------------------------------------------------^
# Basic_data: Step 3: Tokenization & normalization
#------------------------------------------------------------------------------^

df_basic["tokens"] = df_basic["code"].apply(tokenize_code)
df_basic["tokens_normalized"] = df_basic["tokens"].apply(normalize_tokens)

#------------------------------------------------------------------------------^
# Basic_data: Step 4: Filter short code
#------------------------------------------------------------------------------^

df_basic["token_count"] = df_basic["tokens_normalized"].apply(len)
df_basic = df_basic[df_basic["token_count"] >= MIN_TOKENS].drop(columns=["token_count", "tokens"])

#------------------------------------------------------------------------------^
# Basic_data: Step 5: One-hot encoding for language
#------------------------------------------------------------------------------^
lang_onehot = pd.get_dummies(df_basic["language"], prefix="lang").astype(int)
df_basic = pd.concat([df_basic.drop(columns=["language"]), lang_onehot], axis=1)



#-----------------------Feature Engineering(Juliet & basic)------------------------------------------------^
#  Step : Feature engineering: TF-IDF Vectorization
#------------------------------------------------------------------------------^
from sklearn.feature_extraction.text import TfidfVectorizer

# 1) transform tokens list to string & drop old column
df_juliet["tokens_str"] = df_juliet["tokens_normalized"].apply(lambda x: " ".join(x))
df_juliet = df_juliet.drop(columns=["tokens_normalized"], errors="ignore")  

df_basic["tokens_str"] = df_basic["tokens_normalized"].apply(lambda x: " ".join(x))
df_basic = df_basic.drop(columns=["tokens_normalized", "code"])

#  2) Combine the tokens from both datasets for a unified vocabulary
all_tokens = pd.concat([df_juliet["tokens_str"], df_basic["tokens_str"]])

# 3) Fit vectorizer on combined tokens
vectorizer = TfidfVectorizer(min_df=5)  # ignore tokens that appear in less than 5 documents
vectorizer.fit(all_tokens)

# 4) Juliet transform
X_juliet = vectorizer.transform(df_juliet["tokens_str"])
df_juliet_final = pd.concat(
    [df_juliet.reset_index(drop=True).drop(columns=["tokens_str"]),
     pd.DataFrame(X_juliet.toarray(), columns=vectorizer.get_feature_names_out())],
    axis=1
)

# 5) Basic transform
X_basic = vectorizer.transform(df_basic["tokens_str"])
df_basic_final = pd.concat(
    [df_basic.reset_index(drop=True).drop(columns=["tokens_str"]),
     pd.DataFrame(X_basic.toarray(), columns=vectorizer.get_feature_names_out())],
    axis=1
)

# 6) Merge
df_merged = pd.concat([df_juliet_final, df_basic_final], axis=0, ignore_index=True).fillna(0)
# delete old id column
df_merged = df_merged.drop(columns=["id"], errors="ignore")
# Reassign new ID
df_merged = df_merged.reset_index(drop=True)
df_merged["id"] = df_merged.index + 1

print("Merged dataset shape:", df_merged.shape)
print(df_merged.head())
#------------------------------------------------------------------------------^
# column reordering
#------------------------------------------------------------------------------^
lang_cols = sorted([c for c in df_merged.columns if c.startswith("lang_")])
front_cols = ["id", "vulnerability_type","label_encoded"] + lang_cols
other_cols = [c for c in df_merged.columns if c not in front_cols]

df_merged = df_merged[front_cols + other_cols]

#-----------------------Final Save----------------------------------------------------^
# # step : Save final processed dataset
#------------------------------------------------------------------------------^
# CSV file 
output_path_csv_final = "processed_dataset_final5.csv"
df_merged.to_csv(output_path_csv_final, index=False, encoding="utf-8-sig")
print(f"completed final csv file path: {output_path_csv_final}")

# JSON Lines files
# output_path_jsonl_final = "processed_dataset_final.jsonl"
# df_merged.to_json(output_path_jsonl_final, orient="records", lines=True, force_ascii=False)
# print(f"completed final jsonl file path : {output_path_jsonl_final}")
