from google.cloud import bigquery
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BQ_PROJECT = os.getenv("BQ_PROJECT")
BQ_DATASET = os.getenv("BQ_DATASET")

client = bigquery.Client(
    
)

print(client)
# # 1. 대상 테이블 리스트업 쿼리
# query = """
#     SELECT table_name 
#     FROM `your-project.ods.INFORMATION_SCHEMA.TABLES`
#     WHERE table_name LIKE '%_cdc'
# """

# # 2. 리스트 저장
# tables = [row.table_name for row in client.query(query)]

# # 3. 이후 각 테이블에 대해 시차 체크 로직 실행
# for table in tables:
#     check_time_gap(table) # 개별 테이블 시차 확인 함수 (직전 답변의 SQL 활용)