from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# CSV 파일 경로
CSV_FILE_PATH = "./data/program.csv"

def load_and_filter_data(page, limit, region=None, time=None, days=None):
    try:
        # CSV 파일 읽기
        df = pd.read_csv(CSV_FILE_PATH)

        # 필터링: 지역
        if region:
            df = df[df["CTPRVN_NM"] == region]

        # 필터링: 시간 (예: morning, afternoon)
        if time == "morning":
            df = df[df["PROGRAM_ESTBL_TIZN_VALUE"].str.contains("오전", na=False)]
        elif time == "afternoon":
            df = df[df["PROGRAM_ESTBL_TIZN_VALUE"].str.contains("오후", na=False)]

        # 필터링: 요일
        if days:
            for day in days:
                df = df[df[day].notna()]  # 요일 컬럼이 NaN이 아닌 경우만 필터링

        # 페이지네이션
        total_count = len(df)
        start = (page - 1) * limit
        end = start + limit
        paged_data = df.iloc[start:end].to_dict(orient="records")

        return paged_data, total_count

    except Exception as e:
        print(f"Error loading and filtering data: {e}")
        return [], 0

@app.route('/api/programs', methods=['GET'])
def get_programs():
    """프로그램 데이터를 반환하는 엔드포인트"""
    try:
        # 요청 파라미터 읽기
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        region = request.args.get('region')
        time = request.args.get('time')
        days = request.args.getlist('days')  # 리스트로 받음 (예: days=Mon&days=Tue)

        # 데이터 로드 및 필터링
        data, total_count = load_and_filter_data(page, limit, region, time, days)

        # 응답 데이터 형식
        response = {
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit,  # 전체 페이지 수 계산
            'total_count': total_count,
            'data': data
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error in get_programs: {e}")
        return jsonify({"error": "Failed to load programs"}), 500

if __name__ == '__main__':
    app.run(debug=True)
