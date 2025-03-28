#!/bin/bash
# 디버깅 정보 추가
echo "Starting debug.sh script..." > /tmp/pr_reviewer_debug.log
echo "Current directory: $(pwd)" >> /tmp/pr_reviewer_debug.log

# 절대 경로 설정
PR_REVIEWER_PATH="/Users/taekyeong/IdeaProjects/pr_reviewer"
cd "$PR_REVIEWER_PATH"
echo "Changed to directory: $(pwd)" >> /tmp/pr_reviewer_debug.log

# 가상 환경 활성화 검사
if [ -f "$PR_REVIEWER_PATH/.venv/bin/activate" ]; then
    echo "Activating virtual environment..." >> /tmp/pr_reviewer_debug.log
    source "$PR_REVIEWER_PATH/.venv/bin/activate"
else
    echo "ERROR: Virtual environment not found at $PR_REVIEWER_PATH/.venv/bin/activate" >> /tmp/pr_reviewer_debug.log
    exit 1
fi

# Python 인터프리터 검사
if [ -x "$PR_REVIEWER_PATH/.venv/bin/python" ]; then
    echo "Using Python at $PR_REVIEWER_PATH/.venv/bin/python" >> /tmp/pr_reviewer_debug.log
    PYTHON_PATH="$PR_REVIEWER_PATH/.venv/bin/python"
elif [ -x "$PR_REVIEWER_PATH/.venv/bin/python3" ]; then
    echo "Using Python3 at $PR_REVIEWER_PATH/.venv/bin/python3" >> /tmp/pr_reviewer_debug.log
    PYTHON_PATH="$PR_REVIEWER_PATH/.venv/bin/python3"
else
    echo "ERROR: Python interpreter not found in virtual environment" >> /tmp/pr_reviewer_debug.log
    echo "Available files in .venv/bin:" >> /tmp/pr_reviewer_debug.log
    ls -la "$PR_REVIEWER_PATH/.venv/bin" >> /tmp/pr_reviewer_debug.log
    exit 1
fi

# 필요한 파일 확인
if [ -f "$PR_REVIEWER_PATH