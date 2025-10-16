#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy_samdiagnosis.sh <GCP_PROJECT_ID> <GCP_REGION>
# Example: ./deploy_samdiagnosis.sh my-project us-central1

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <GCP_PROJECT_ID> <GCP_REGION>"
  exit 1
fi

PROJECT_ID="$1"
REGION="$2"
SERVICE_NAME="samdiagnosis-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:$(date +%Y%m%d-%H%M%S)"
DATASET="samdiagnosis_data"
BUCKET="${PROJECT_ID}-samdiagnosis-bucket"
SA_NAME="samdiagnosis-svc"
PUBSUB_TOPIC="samdiagnosis-embeddings"
MIGRATION_FILE="migrations/001_init_bq.sql"
DEPLOY_DIR="samdiagnosis_deploy_temp"

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service name: $SERVICE_NAME"
echo

read -p "تأكد أنك سجلت دخول gcloud وأن المشروع صحيح. استمر؟ (y/n) " confirm
if [ "$confirm" != "y" ]; then
  echo "Aborted."
  exit 0
fi

echo "1) تمكين APIs المطلوبة..."
gcloud config set project "$PROJECT_ID"
gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com run.googleapis.com cloudbuild.googleapis.com pubsub.googleapis.com storage.googleapis.com iam.googleapis.com --quiet

echo "2) إعداد ملفات النشر..."
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy backend and migrations files to the deployment directory
echo "نسخ ملفات الواجهة الخلفية والترحيل إلى دليل النشر..."
cp -r backend "$DEPLOY_DIR/"
cp -r migrations "$DEPLOY_DIR/"

cd "$DEPLOY_DIR"

# ----------- 3) Create resources on GCP --------------
echo "3) إنشاء service account وroles..."
if ! gcloud iam service-accounts describe "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$SA_NAME" --display-name "SAMDIAGNOSIS service account" --project "$PROJECT_ID"
fi

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/run.admin" --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/storage.admin" --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/bigquery.admin" --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/pubsub.admin" --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/aiplatform.user" --quiet

# create bucket
echo "4) إنشاء GCS bucket (لرفعات المريض إن احتجت)..."
if ! gsutil ls -b "gs://${BUCKET}" >/dev/null 2>&1; then
  gsutil mb -l "$REGION" "gs://${BUCKET}"
  echo "Bucket gs://${BUCKET} created."
else
  echo "Bucket gs://${BUCKET} already exists."
fi

# create pubsub topic
echo "5) إنشاء Pub/Sub topic..."
if ! gcloud pubsub topics describe "$PUBSUB_TOPIC" >/dev/null 2>&1; then
  gcloud pubsub topics create "$PUBSUB_TOPIC"
  echo "Pub/Sub topic ${PUBSUB_TOPIC} created."
else
  echo "Topic ${PUBSUB_TOPIC} exists."
fi

# create BigQuery dataset and run migration
echo "6) إنشاء BigQuery dataset وتهيئة الجداول (تشغيل migration)..."
bq --location="${REGION}" mk -d --dataset_id="${DATASET}" "${PROJECT_ID}" || true
echo "Running SQL migration..."
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" < "${MIGRATION_FILE}"

# ----------- 7) Build & push Docker image via Cloud Build --------------
echo "7) رفع وبناء صورة الـDocker باستخدام Cloud Build..."
gcloud builds submit --tag "${IMAGE_NAME}" backend

# ----------- 8) نشر Cloud Run service --------------
echo "8) نشر Cloud Run service..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format 'value(status.url)')
echo "Cloud Run service URL: $SERVICE_URL"

# ----------- 9) إعداد متغيرات بيئة في Cloud Run (Env vars) --------------
echo "9) ضبط متغيرات البيئة في Cloud Run (GCP project + VERTEX_LOCATION)..."
gcloud run services update "${SERVICE_NAME}" --region "${REGION}" --update-env-vars "GCP_PROJECT=${PROJECT_ID},VERTEX_LOCATION=${REGION}"

# ----------- 10) الخاتمة --------------
cd ..
echo
echo "=============================="
echo "تم الانتهاء — التفاصيل:"
echo " - Backend (Cloud Run): $SERVICE_URL"
echo " - BigQuery Dataset: ${PROJECT_ID}.${DATASET}"
echo " - GCS Bucket: gs://${BUCKET}"
echo " - Pub/Sub Topic: ${PUBSUB_TOPIC}"
echo " - Service Account: ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo
echo "ملاحظات تالية (هام):"
echo " - قبل استخدام استدعاءات Vertex AI، تأكّد أن حساب الخدمة لديه الأذونات اللازمة (roles/aiplatform.user إذا لزم)."
echo " - لتعديل أسماء نماذج Vertex التي تريد استدعاءها، عدّل ملف backend/vertexClient.js واستخدم أسماء النماذج المتاحة في حسابك."
echo " - للتعامل مع بيانات حساسة: طبّق عملية de-identification قبل إرسال النصوص إلى Vertex AI."
echo "=============================="