# Karma Fraud Detector

> **AI-powered system to detect fraudulent and suspicious karma activities using behavioral analytics, NLP, and a Random Forest model with React + FastAPI deployment.**
    [**Try it here**](https://karma-fraud-detector.onrender.com/)

## Overview
Karma Fraud Detector is an automated, explainable, and scalable tool designed to identify karma manipulation on activity score-based platforms. It leverages:

- **Machine Learning** (Random Forest classifier)
- **Natural Language Processing** (spam and low-effort detection submodels)
- **Behavioral Analytics** (burst patterns, mutual upvotes, upvote diversity)

The system provides **real-time fraud predictions** and detailed suspicious activity analyses to ensure platform integrity.

---

## Architecture

- **Frontend:** React.js for user input, analysis results, and visualization.
- **Backend:** FastAPI serving RESTful APIs for prediction, built with Python.
- **Models:** Random Forest classifier + NLP submodels.
- **Data:** Synthetic dataset generation for normal, suspicious, and fraudulent users.
- **Deployment:** Dockerized microservices; backend on Hugging Face Spaces, frontend on Render or static hosting.

---

## Features

- Upload or input user activity logs
- Real-time fraud classification (normal, suspicious, fraudulent)
- Activity-level suspicious behavior explanations
- Visual dashboards (pie charts, bar graphs, tables)
- Containerized for scalable deployment

---

##  Results

- **Accuracy:** 92% overall with macro F1-score of 0.91
- **Key indicators:** Upvote burstiness, mutual upvotes, upvote concentration from new accounts
- **Outcome:** Interpretable, actionable outputs for effective moderation

---

## Tech Stack

- **Frontend:** React.js
- **Backend:** FastAPI, scikit-learn, joblib
- **NLP Models:** Sentence Transformers + Random Forest
- **Containerization:** Docker
- **Deployment:** Hugging Face Spaces, Render

---

## Project Structure

```
karma-fraud-detector/
├── backend/
│   ├── app/                 
│   ├── data/                
│   ├── model/               
│   ├── Dockerfile           # Backend Dockerfile for Hugging Face deployment
│   ├── requirements.txt 
├── frontend/
│   ├── public/              
│   ├── src/                 
│   ├── package.json         
│   └── package-lock.json
```


### Description

- **backend/** – FastAPI app, model training scripts, feature extraction modules.
- **frontend/** – React app for user input, real-time analysis results, and visualization.
- **deployment/** – Dockerfiles for scalable cloud deployment.

---

## Deployment Details

- **Backend:** Hugging Face Spaces 
- **Frontend:** Render
---

## Future Enhancements

- Advanced transformer-based NLP models
- Real-time APIs for continuous monitoring
- Platform-wide trustworthiness scoring dashboards
- Automated alerting and integration with moderation pipelines

