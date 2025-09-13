import os
import pandas as pd
from IPython.display import display
import re   # 정규식
import numpy as np  # 수치계산

# 🍉 Step 1: testcases 폴더 내 모든 소스코드 수집
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
                 # 진행상황 표시
                if len(data) % 100 == 0:
                    print(f"{len(data)} 개 파일 읽음...")
            except Exception as e:
                print(f"읽기 실패: {file_path}, 오류: {e}")



#--------------------------------------Data cleaning----------------------------------------^ 여기까지 해서 파일읽고 리스트에 저장 완료
# 🍉🍉 Step 2: DataFrame으로 변환, 파일 수준 전처리
df = pd.DataFrame(data, columns=["file_path", "code"])
print("총 파일 개수:", len(df))
display(df.head())


# 1. 빈 코드 제거 (strip() 후 공백만 남은 경우 제외)
df = df[df["code"].str.strip() != ""]
print("빈 파일 제거 후 개수:", len(df))
display(df.head())

# 2. 중복 코드 제거 (code 컬럼 기준)
df = df.drop_duplicates(subset=["code"], keep="first")
print("중복 제거 후 개수:", len(df))
display(df.head())

# 3. 불필요한 파일 제외 (README, .txt, .md 등)
exclude_keywords = ["README", "readme", ".txt", ".md", "CMakeLists", "Makefile","main.cpp","main_linux","testcase.h"]
pattern = "|".join(exclude_keywords)  # 정규식 패턴으로 묶음
df = df[~df["file_path"].str.contains(pattern, case=False, na=False)]

print("전처리 후 남은 파일 개수:", len(df))
display(df.head())

#Cureent Colums {"file_path", "code"}

#------------------------------------------------------------------------------^ 
# 🍉🍉🍉 Step 3: 코드수준 전처리: 주석처리/공백,줄바꿈 정리/코드분할

# ✅ 1. 주석 제거 함수
def remove_comments(code: str) -> str:
    # /* ... */ 블록 주석 제거
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL) #reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    # // 라인 주석 제거
    code = re.sub(r"//.*", "", code) #reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    return code

# 새로운 컬럼으로 추가
df["code_no_comments"] = df["code"].apply(remove_comments)
# 원본 code 컬럼은 삭제
df = df.drop(columns=["code"], errors="ignore")
print("주석 제거 완료")
display(df.head())


# ✅ 2. 공백 / 줄바꿈 정리 함수
def normalize_whitespace(code: str) -> str:
    # 탭 → 공백
    code = code.replace("\t", " ")
    # 여러 공백 → 하나
    code = re.sub(r" +", " ", code)
    # 연속된 줄바꿈 → 하나
    code = re.sub(r"\n\s*\n", "\n", code)
    # 맨 앞/뒤 공백 제거
    return code.strip()

# 새로운 컬럼으로 추가
df["code_normalized"] = df["code_no_comments"].apply(normalize_whitespace)
# 주석 제거된 컬럼 삭제
df = df.drop(columns=["code_no_comments"], errors="ignore")
print("공백/줄바꿈 정리 완료")
display(df.head())


# ✅ 3. 함수 단위 분리 =>몇몇 함수단위 잘못잡을 수있음 예: 매개변수()중첩, {}중괄호 중첩
def split_functions(code: str):
    """
    함수 단위로 코드 분리
    예: 'void foo() {...}' 단위별로 리스트 반환
    """
    pattern = re.compile(
        r"[a-zA-Z_][a-zA-Z0-9_]*\s+\**[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\{[^}]*\}",#reference: https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
        re.DOTALL
    )
    #입력받은 코드 문자열에서 모든 함수 블록을 리스트로 추출
    matches = pattern.findall(code)
    #만약 함수 패턴을 하나라도 찾았다면 → 그 리스트 반환
    return matches if matches else [code]

# 새로운 열추가, 함수 단위로 분리된 컬럼 추가 후, 행 단위로 explode
df = df.assign(functions=df["code_normalized"].apply(split_functions)).explode("functions").reset_index(drop=True)#reference: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html
#df.assing(functions=...) → 새로운 컬럼 추가
#df["code_normalized"].apply(split_functions) → 각 행의 코드를 함수 단위로 분리
#.explode("functions") → 리스트로 된 각 행을 개별 행으로 분리 
#.reset_index(drop=True) → 인덱스 재설정

# 주석 제거된 컬럼 삭제
df = df.drop(columns=["code_normalized"], errors="ignore")
print("함수 단위 분리 후 총 샘플 개수:", len(df))
display(df.head())

#Cureent Colums {"file_path", "functions"}
#------------------------------------------------------------------------------^ 
# 🍉🍉🍉 Step 4: 새로운 열 추가  id, language, Vulnerability ID / Type

# ✅ 1. ID 부여 (순서대로 번호 붙이기)
df = df.reset_index(drop=True)  # 혹시 모를 인덱스 꼬임 방지
df["id"] = df.index + 1         # 1부터 시작하는 id 부여

# ✅ 2. Language 컬럼 생성
def detect_language(path: str) -> str:
    if path.endswith(".c") or path.endswith(".h"):
        return "C"
    elif path.endswith(".cpp"):
        return "C++"
    else:
        return "Unknown"

df["language"] = df["file_path"].apply(detect_language)

# ✅ 3. Vulnerability ID 및 Type 추출 (CWE 숫자만 추출)

# CWE 뒤의 숫자만 가져오기 → 예: CWE121 → 121
df["vulnerability_cwe_id"] = df["file_path"].str.extract(r"CWE(\d+)")

# 취약점 유형 추출
df["vulnerability_type"] = df["file_path"].str.extract(r"CWE\d+_(.*?)(?:/|$)")

print("ID 및 Language & vulnerability_cwe_id와 type 컬럼 추가 완료")
display(df.head())
#Cureent Colums {"file_path", "functions", "id", "language", "vulnerability_cwe_id", "vulnerability_type"}

#------------------------------------------------------------------------------^ 
# 🍉 Step 5: Vulnerable / Safe 라벨링 (강화된 규칙)

df["label"] = "unknown"  # 기본값

# vulnerable 라벨
df.loc[
    df["functions"].str.contains("bad", case=False, na=False) |
    df["file_path"].str.contains("bad", case=False, na=False),
    "label"
] = "vulnerable"

# safe 라벨
df.loc[
    df["functions"].str.contains("good", case=False, na=False) |
    df["file_path"].str.contains("good", case=False, na=False),
    "label"
] = "safe"

#file_path 컬럼 삭제
df = df.drop(columns=["file_path"], errors="ignore")
print("라벨링 완료")
display(df.head())

#Cureent Colums {"functions", "id", "language", "vulnerability_cwe_id", "vulnerability_type", "label"}

#------------------------------------------------------------------------------^
# 🍉 Step 6: 결측치 처리

# 결측치 개수 확인
print("컬럼별 결측치 개수:\n", df.isna().sum())

# unknown 라벨 제거
df = df[df["label"] != "unknown"]

# 결측치가 있다면 제거 (dropna) → 혹은 기본값 대체(fillna)

# 필수 컬럼에 NaN이 있으면 제거
df = df.dropna(subset=["functions"])

# 나머지 메타데이터는 Unknown으로 채움
df = df.fillna({
    "language": "Unknown",
    "vulnerability_cwe_id": "0",
    "vulnerability_type": "Unknown"
})
df["vulnerability_cwe_id"] = df["vulnerability_cwe_id"].astype(int)



print("결측치 처리 완료")
display(df.head())
#Cureent Colums {"functions", "id", "language", "vulnerability_cwe_id", "vulnerability_type", "label"}

#--------------------------------Transformation----------------------------------------------^
# 🍉 Step 7: One-Hot Encoding (language) & 
# ✅1.라벨 매핑 (Scikit-learn용)
df["label_encoded"] = df["label"].map({
    "safe": 0,
    "vulnerable": 1
})
# 원본 label 컬럼 삭제
df = df.drop(columns=["label"], errors="ignore")
print(df["label_encoded"].head())

# ✅2. language → One-Hot Encoding
language_onehot = pd.get_dummies(df["language"], prefix="lang")

# df에 결합 (가로로 붙임)
df = pd.concat([df, language_onehot], axis=1)

# 원본 language 컬럼 삭제
df = df.drop(columns=["language"], errors="ignore")
print("One-Hot Encoding 완료")
#Cureent Colums {"functions", "id", "vulnerability_cwe_id", "vulnerability_type", "label_encoded", "lang_C", "lang_C++", "lang_Unknown"}

#------------------------------------------------------------------------------^
# 🍉 Step 8: 토큰화

def tokenize_code(code: str):
    """
    C/C++ 코드를 토큰 단위로 분리
    - 키워드, 식별자
    - 숫자
    - 연산자, 구분자
    """
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|\d+|==|!=|<=|>=|[{}();,+\-*/<>]", code)
    return tokens

# 새로운 컬럼으로 추가
df["tokens"] = df["functions"].apply(tokenize_code)
print("토큰화 완료")
# 원본 functions 컬럼 삭제
df = df.drop(columns=["functions"], errors="ignore")
display(df["tokens"].head())
#Cureent Colums {"id", "vulnerability_cwe_id", "vulnerability_type", "label_encoded", "lang_C", "lang_C++", "lang_Unknown", "tokens"}

#------------------------------------------------------------------------------^
# 🍉 Step 9: 정규화
# ✅ C & C++ 주요 키워드 집합 (C99 + C11 + C++17까지 포함)
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

        if token.isdigit():  # 숫자 -> <NUM>
            normalized.append("<NUM>")
        elif re.match(r'".*"', token) or re.match(r"'.*'", token):  # 문자열 -> <STR>
            normalized.append("<STR>")
        elif re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", token):  # 식별자 (변수명, 함수명 등)
            if token in keywords:
                normalized.append(token)  # 키워드는 그대로 유지
            else:
                normalized.append("<VAR>")
        else:
            normalized.append(token)  # 연산자/구분자는 그대로 유지

    return normalized

df["tokens_normalized"] = df["tokens"].apply(normalize_tokens)

print("정규화 완료")
# 원본 tokens 컬럼 삭제
df = df.drop(columns=["tokens"], errors="ignore")
display(df[ "tokens_normalized"].head())

#Cureent Colums {"id", "vulnerability_cwe_id", "vulnerability_type", "label_encoded", "lang_C", "lang_C++", "lang_Unknown", "tokens_normalized"}
#--------------------------------Break----------------------------------------------^
# Data collection step 1
# Cleaning step 2,4,5,6
#Transformations step 3,7,8,9



#  JSON Lines 형식으로 저장
output_path_jsonl = "processed_dataset.jsonl"
df.to_json(output_path_jsonl, orient="records", lines=True, force_ascii=False)
print(f"JSONL 파일 저장 완료: {output_path_jsonl}")

#  CSV 형식으로 저장
output_path_csv = "processed_dataset.csv"
df.to_csv(output_path_csv, index=False, encoding="utf-8-sig")
print(f"CSV 파일 저장 완료: {output_path_csv}")

#-----------------------Feature Engineering------------------------------------------------^
# 🍉 Step 10: Feature engineering: TF-IDF 벡터화
from sklearn.feature_extraction.text import TfidfVectorizer

# 1) 토큰 리스트를 문자열로 변환
df["tokens_str"] = df["tokens_normalized"].apply(lambda x: " ".join(x))
# 원본 토큰 컬럼 삭제
df = df.drop(columns=["tokens_normalized"], errors="ignore")  

# 2) TF-IDF 적용
vectorizer = TfidfVectorizer() #tf-idf 벡터라이저 객체 생성
X_tfidf = vectorizer.fit_transform(df["tokens_str"]) #문자열 데이터를 TF-IDF 행렬로 변환 / fit()+transform() 합친것

print("TF-IDF Feature Matrix shape(samples,colums):", X_tfidf.shape)#(샘플수, 특성수) => (function의 갯수,colunm의 갯수)

# 3) DataFrame으로 변환해서 확인 (옵션)
tfidf_df = pd.DataFrame(
    X_tfidf.toarray(),
    columns=vectorizer.get_feature_names_out()
)
display(tfidf_df.head())
