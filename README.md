# ☁️ Cloud-Deployed AI Pipeline

A production-style data pipeline built with AWS, Docker, and Kubernetes.

## 🏗️ Architecture

- **AWS S3** — Cloud storage for CSV data
- **AWS CloudWatch** — Logging and monitoring
- **SQLite** — Lightweight database (simulating RDS)
- **Docker** — Containerized pipeline
- **Kubernetes (Minikube)** — Container orchestration

## 🚀 Features

- Uploads CSV data to S3
- Logs pipeline runs to CloudWatch
- Stores run metadata in SQLite database
- Fully containerized with Docker
- Deployed and orchestrated with Kubernetes

## 📁 Project Structure 
cloud-ai-pipeline/

├── lambda/

│   └── handler.py        # Main pipeline script

├── data/

│   └── sample_data.csv   # Sample input data

├── Dockerfile            # Docker image definition

├── k8s-deployment.yaml   # Kubernetes Job manifest

└── README.md             # Project documentation
## ⚙️ Setup & Usage

### Prerequisites
- Python 3.11+
- AWS CLI configured
- Docker Desktop
- Minikube

### Run Locally
```bash
python lambda/handler.py
```

### Run with Docker
```bash
docker build -t ai-pipeline .
docker run --rm \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e AWS_DEFAULT_REGION=us-east-1 \
  ai-pipeline
```

### Run with Kubernetes
```bash
minikube start --driver=docker
kubectl create secret generic aws-credentials \
  --from-literal=aws_access_key_id=your-key \
  --from-literal=aws_secret_access_key=your-secret
minikube image load ai-pipeline:latest
kubectl apply -f k8s-deployment.yaml
kubectl logs job/ai-pipeline-job
```

## 📊 CloudWatch Logs

Log Group: `/ai-pipeline/vicky-2026`

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Pipeline logic |
| AWS S3 | Data storage |
| AWS CloudWatch | Monitoring |
| SQLite | Database |
| Docker | Containerization |
| Kubernetes | Orchestration |