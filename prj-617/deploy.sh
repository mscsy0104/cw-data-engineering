#!/bin/bash

gcloud functions deploy export-bq-to-gcs \
  --gen2 \
  --region=asia-northeast1 \
  --runtime=python311 \
  --source=. \
  --entry-point=main_handler \
  --trigger-http \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=600s \
  --env-vars-file=env.yaml