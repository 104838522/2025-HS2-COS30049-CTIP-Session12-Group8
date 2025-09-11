import os
#🍉 Step 1: testcases 폴더 내의 모든 C, C++ 소스코드 파일을 재귀적으로 탐색하여 코드 추출

# testcases 폴더 경로 (data 폴더 바로 안에 있다고 가정)
testcase_dir = "data/testcases"

# 추출된 소스코드 저장용 리스트 => [{ "file_path": "...", "code": "..." }, {...}, ...] 형태
source_files = []

# testcases 폴더를 재귀적으로 순회
    # root: 현재 탐색 중인 폴더 경로
    # dirs: root 안에 있는 하위 폴더 목록
    # files: root 안에 있는 파일 목록
for root, dirs, files in os.walk(testcase_dir):
    for file in files:
        if file.endswith((".c", ".cpp", ".h")):  # C, C++ 소스코드만
            file_path = os.path.join(root, file) # 파일의 전체 경로
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:# 파일 열기
                    code_text = f.read() # 파일 내용 읽기
                # 추출된 코드와 파일 경로를 리스트에 추가
                source_files.append({
                    "file_path": file_path,
                    "code": code_text
                })
                 # 진행상황 표시
                if len(source_files) % 100 == 0:
                    print(f"{len(source_files)} 개 파일 읽음...")

            except Exception as e:
                print(f"읽기 실패: {file_path}, 오류: {e}")

print("총 추출된 소스코드 개수:", len(source_files))

# ☢️예시 출력 (앞부분만)
for i, src in enumerate(source_files[:3]):
    print(f"\n[{i+1}] 파일 경로: {src['file_path']}")
    print(src["code"][:300])  # 앞 300자만 미리보기
 #--------------------------------------------------------------여기까지 해서 파일읽고 리스트에 저장 완료

