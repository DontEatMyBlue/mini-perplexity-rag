## 실행 방법

### 1. 가상환경 생성 및 패키지 설치

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2. 환경 변수 설정 (.env)

루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

---

### 3. 서버 실행

```bash
uvicorn main:app --reload
```

---

### 4. 프론트 실행 (Streamlit)

```bash
streamlit run streamlit/chat_ui.py
```
