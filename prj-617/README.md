# BigQuery to GCS Export Function

BigQuery 데이터를 CSV 및 Excel 형식으로 변환하여 Google Cloud Storage에 업로드하는 Cloud Function

## 기능

- BigQuery 테이블에서 데이터 조회
- CSV 및 Excel 형식으로 변환
- Google Cloud Storage에 자동 업로드
- 날짜 기반 파일명 생성 (`YYYYMMDD_<프로젝트 관련 이름>.csv/xlsx`)

## 환경 변수

`env.yaml` 파일에 다음 환경 변수를 설정해야함:

- `PROJECT_ID`: GCP 프로젝트 ID
- `DATASET_ID`: BigQuery 데이터셋 ID
- `TABLE_ID`: BigQuery 테이블 ID
- `BUCKET_NAME`: GCS 버킷 이름
- `GCS_PATH_SUFFIX`: GCS 업로드 경로 접미사 (선택사항)

## 배포

```bash
./deploy.sh
```

또는 직접 배포:

```bash
gcloud functions deploy export-bq-to-gcs \
  --gen2 \
  --region=asia-northeast1 \
  --runtime=python311 \
  --source=. \
  --entry-point=main_handler \
  --trigger-http \
  --allow-unauthenticated \
  --memory=4Gi \
  --timeout=600s \
  --env-vars-file=env.yaml \
  --min-instances=0 \
  --max-instances=5
```


## 사용 방법

HTTP 트리거로 함수를 호출하면 BigQuery에서 데이터를 읽어 GCS에 업로드함.

## 의존성

- `functions-framework`: Cloud Functions Framework
- `google-cloud-bigquery`: BigQuery 클라이언트
- `google-cloud-storage`: GCS 클라이언트
- `pandas`: 데이터 처리
- `pandas-gbq`: BigQuery에서 Pandas DataFrame으로 데이터 읽기
- `openpyxl`: Excel 파일 생성
- `pyarrow`: Apache Arrow 포맷 지원
  - `pandas-gbq`가 BigQuery에서 데이터를 읽을 때 내부적으로 사용
  - Apache Arrow 포맷을 통해 더 빠르고 효율적인 데이터 전송 및 메모리 사용
  - 대용량 데이터 처리 시 성능 향상에 기여

## 주의사항

- 대용량 데이터의 경우 메모리 사용량에 주의
  - 특히 read_gbq()

## GCloud 설정 설명

배포 시 사용되는 주요 설정값과 그 이유:

### `--timeout=600s` (10분)
- **설정 이유**: 
  - Scheduler 시도 기한의 초깃값 3분(180초)이 GCS에 적재가 잘 돼도 데이터 양이 늘어남에 따라 시간 초과로 Scheduler Error 발생
  - BigQuery에서 대용량 데이터를 읽고, Pandas DataFrame으로 변환하며, Excel 파일 생성까지 처리하는 과정에서 시간이 소요될 수 있음
  - 따라서 Scheduler 시도 기한을 늘리고 Cloud Function 타임아웃도 600초로 설정

### `--memory=4Gi` (4GB)
- **설정 이유**:
  - `pd.read_gbq()`로 BigQuery 전체 테이블을 메모리에 로드
  - Pandas DataFrame이 메모리에 상주하며 CSV/Excel 변환 처리
  - `df.to_excel()` 실행 시 openpyxl 엔진이 추가 메모리 사용
  - 대용량 데이터 처리 시 메모리 부족 오류 방지를 위해 충분한 메모리 할당
    - ex. memory 2Gi 설정 시 2049MB 사용으로 에러 발생했었음.

### `--min-instances=0`
- **설정 이유**:
  - 비용 최적화: 함수가 호출되지 않을 때는 인스턴스를 완전히 종료하여 비용 절감
  - 스케줄러 기반 주기적 실행에 적합 (필요할 때만 실행)

### `--max-instances=5`
- **설정 이유**:
  - 동시 요청 수를 제한하여 리소스 사용량과 비용 관리
  - BigQuery 쿼리 및 GCS 업로드 작업의 동시 실행 제어
  - 대용량 데이터 처리 시 과도한 동시 실행으로 인한 메모리/네트워크 부하 방지