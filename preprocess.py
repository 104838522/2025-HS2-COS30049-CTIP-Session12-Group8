# --------------------------------------------------------------------
# Preprocessing function for FastAPI integration
# --------------------------------------------------------------------
import re

def preprocess_code(raw_code: str) -> str:
    """
    This function takes a single code string and performs:
    1) Comment removal
    2) Whitespace normalization
    3) Tokenization and token normalization
    4) Returns the normalized tokens as a single string
    """

    # 1. Remove comments
    code = re.sub(r"/\*.*?\*/", "", raw_code, flags=re.DOTALL)
    code = re.sub(r"//.*", "", code)

    # 2. Normalize whitespace
    code = code.replace("\t", " ")
    code = re.sub(r" +", " ", code)
    code = re.sub(r"\n\s*\n", "\n", code)
    code = code.strip()

    # 3. Tokenization
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|\d+|==|!=|<=|>=|[{}();,+\-*/<>]", code)

    # 4. Token normalization
    keywords = {
        "auto","break","case","char","const","continue","default","do","double","else",
        "enum","extern","float","for","goto","if","inline","int","long","register",
        "restrict","return","short","signed","sizeof","static","struct","switch",
        "typedef","union","unsigned","void","volatile","while","_Alignas","_Alignof",
        "_Atomic","_Bool","_Complex","_Generic","_Imaginary","_Noreturn",
        "_Static_assert","_Thread_local",
        "alignas","alignof","asm","bool","catch","char16_t","char32_t","class","constexpr",
        "const_cast","delete","dynamic_cast","explicit","export","false","friend","mutable",
        "namespace","new","noexcept","nullptr","operator","private","protected","public",
        "reinterpret_cast","static_assert","static_cast","template","this","thread_local",
        "throw","true","try","typename","using","virtual","wchar_t"
    }

    normalized = []
    for token in tokens:
        if token.isdigit():
            normalized.append("<NUM>")
        elif re.match(r'".*"', token) or re.match(r"'.*'", token):
            normalized.append("<STR>")
        elif re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", token):
            if token in keywords:
                normalized.append(token)
            else:
                normalized.append("<VAR>")
        else:
            normalized.append(token)

    # 5. Combine tokens into a single string
    return " ".join(normalized)
