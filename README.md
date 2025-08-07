# 프로젝트 루트에서 가상환경 생성
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 환경 변수 설정 (.env)
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key

# 서버 실행
uvicorn main:app --reload

# 프론트 실행
streamlit run streamlit/chat_ui.py   

   
