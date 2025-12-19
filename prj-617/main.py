import functions_framework
from google.cloud import bigquery, storage
import os
import datetime
import pandas as pd
import sys
from io import BytesIO
import logging


logging.basicConfig(level=logging.INFO)

# 환경 변수 설정
PROJECT_ID = os.environ.get('PROJECT_ID')
DATASET_ID = os.environ.get('DATASET_ID')
TABLE_ID = os.environ.get('TABLE_ID')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
GCS_PATH_SUFFIX = os.environ.get('GCS_PATH_SUFFIX', '')


def export_bq_to_gcs():
    """
    핵심 비즈니스 로직: BQ -> Pandas -> GCS
    """
    # 환경 변수 검증
    if not all([PROJECT_ID, DATASET_ID, TABLE_ID, BUCKET_NAME]):
        raise ValueError('Missing required environment variables')

    # 1. 파일명 및 경로 생성
    datestamp = datetime.datetime.now().strftime("%Y%m%d")
    base_filename = f"{datestamp}_inner_page_source_data"
    csv_filename = f"{base_filename}.csv"
    excel_filename = f"{base_filename}.xlsx"
    blob_path = f"{GCS_PATH_SUFFIX.strip('/')}/" if GCS_PATH_SUFFIX else ""
    
    # 2. BigQuery에서 데이터 읽기
    table_path = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    logging.info(f"🔗 Reading from BigQuery: {table_path}")
    
    # read_gbq는 데이터가 클 경우 메모리 에러를 유발할 수 있으니 주의
    df = pd.read_gbq(f"SELECT * FROM `{table_path}`", project_id=PROJECT_ID)
    logging.info(f"📊 Loaded {len(df):,} rows.")

    # 3. CSV 변환
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    
    # 4. Excel 변환
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_data = excel_buffer.getvalue()

    # 5. GCS 업로드
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # CSV 업로드
    csv_blob = bucket.blob(blob_path + csv_filename)
    csv_blob.upload_from_string(csv_data, content_type='text/csv; charset=utf-8')
    
    # Excel 업로드
    excel_blob = bucket.blob(blob_path + excel_filename)
    excel_blob.upload_from_string(excel_data, content_type='application/vnd.ms-excel')

    return {"csv": csv_blob.name, "excel": excel_blob.name}


@functions_framework.http
def main_handler(request):
    """
    진입점(Entry Point) - 배포 시 이 함수 이름을 '진입점'으로 설정하세요.
    """
    # OPTIONS 요청 처리 (CORS)
    if request.method == 'OPTIONS':
        return ('', 204, {'Access-Control-Allow-Origin': '*'})

    try:
        # 로직 실행
        files = export_bq_to_gcs()
        
        logging.info("✅ Pipeline finished successfully.")
        return {
            "status": "success",
            "files": files
        }, 200

    except Exception as e:
        # 에러 발생 시 상세 정보 로깅
        error_msg = f"❌ Pipeline failed: {str(e)}"
        logging.error(error_msg, exc_info=True) # exc_info는 Traceback 전체를 로깅합니다.
        
        # Scheduler가 실패로 인식하도록 500 리턴
        return {
            "status": "failed",
            "error": str(e)
        }, 500