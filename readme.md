gcloud config set project stock-analysis-llm
gcloud auth login 
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
---
中間過程
https://chatgpt.com/share/687e5b9f-a260-8013-b59c-0e46ef357705
---
final response:

gcloud run deploy stock-llm \
  --image gcr.io/stock-analysis-llm/stock-llm \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
---
最後
gcloud builds submit --tag gcr.io/stock-analysis-llm/stock-llm

gcloud run deploy stock-llm \
  --image gcr.io/stock-analysis-llm/stock-llm \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
