from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # CORS 설정

# CSV 파일 경로
CSV_FILE_PATH = "./data/program.csv"

# 데이터를 로드하는 함수
def load_filtered_program_data(region=None, time=None, days=None, page=1, limit=20):
    try:
        # CSV 데이터를 pandas로 읽기
        df = pd.read_csv(CSV_FILE_PATH)
        
        # 필터링 시작
        if region:
            df = df[df["CTPRVN_NM"] == region]
        
        if time:
            df = df[df[time] == True]
        
        if days:
            for day in days:
                df = df[df[day] == True]

        # 페이지네이션 처리
        start = (page - 1) * limit
        end = start + limit
        total_count = len(df)
        paged_data = df.iloc[start:end].to_dict(orient="records")

        return paged_data, total_count
    except Exception as e:
        print(f"Error loading or filtering data: {e}")
        return [], 0

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """프로그램 데이터를 반환하는 엔드포인트"""
    # 요청 파라미터 가져오기
    region = request.args.get('region', None)
    time = request.args.get('time', None)
    days = request.args.getlist('days')  # 요일은 리스트 형태로 받음
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    # 데이터를 로드하고 필터링
    data, total_count = load_filtered_program_data(region, time, days, page, limit)
    
    # 응답 데이터 형식
    response = {
        'page': page,
        'limit': limit,
        'total_count': total_count,
        'total_pages': (total_count + limit - 1) // limit,  # 총 페이지 수 계산
        'data': data
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
