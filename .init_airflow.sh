#!/bin/bash
# Airflow 초기 셋업 스크립트

# 1. docker-compose.yaml 다운로드
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.0/docker-compose.yaml'

# 2. 필수 디렉토리 생성
mkdir -p ./dags ./logs ./plugins ./config

# 3. .env 파일 생성 (AIRFLOW_UID 설정)
echo "AIRFLOW_UID=$(id -u)" > .env

# 4. Airflow 설정 리스트 보기
sudo docker compose run airflow-cli airflow config list

# 5. Airflow 초기화
sudo docker compose up airflow-init

# 6. Airflow 전체 서비스 실행
sudo docker compose up