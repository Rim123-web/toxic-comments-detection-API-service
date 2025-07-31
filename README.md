# toxic-comments-detection-API-service
This project provides a Toxic Comment Detection API powered by Flask, where users can fill out a simple form to instantly receive their API key and use it to analyze text comments for toxicity.



This project is a complete **Toxic Comment Detection API as a Service**, built using **Flask** for the backend and **HTML/CSS/JavaScript** for the frontend. It allows users to generate an API key via a simple form, test their key, and use it to get predictions about whether a given comment is **toxic (1)** or **non-toxic (0)**.

##  Project Overview

*  **Main Objective**: Detect if a user-submitted comment is **toxic** or **non-toxic**.
*  **API Key System**: Users fill out a form to receive an API key and then test it directly from the interface.
*  **Visualization Dashboard**: Integrated data visualizations (heatmaps, bar plots, radar charts) for insight into the dataset and prediction behavior.
*  **ML Model**: XGBoost classifier trained on preprocessed text data, achieving **\~94% accuracy**.

---

##  Features

* **User Form** to get a unique API key (no registration required).
* **API Endpoint** to predict toxicity of comments.
* **API Key Testing** via frontend interface.
* **Interactive Dashboard** with:

  * Correlation heatmap
  * Threshold-based bar plots
  * Toxicity radar chart

---

##  Machine Learning Pipeline

1. **Data Cleaning**:

   * Lowercasing, punctuation removal, stop word filtering.
   * Lemmatization using NLP tools.
2. **Balancing the Dataset**:

   * Used **SMOTE** (Synthetic Minority Over-sampling Technique) to handle class imbalance.
3. **Vectorization**:

   * Applied **TF-IDF Vectorizer** on the cleaned text data.
4. **Model Training**:

   * Tried several classifiers: `Random Forest`, `SVM`, etc.
   * Final model: **XGBoost**, selected for best performance (accuracy \~94%).

---

##  Tech Stack

| Layer         | Tools & Libraries                                     |
| ------------- | ----------------------------------------------------- |
| Frontend      | HTML, CSS, JavaScript                                 |
| Backend       | Python, Flask                                         |
| ML Libraries  | pandas, scikit-learn, XGBoost, imbalanced-learn, nltk |
| Visualization | Plotly, seaborn, matplotlib                           |

---



##  How it works



1.Fill out the form on the main page to receive your personal API key.
2. The API key is generated and assigned with a limited quota (e.g., 2000 requests).
3. The user sends a request with:

   * `api_key`
   * `comment_text`
4. The server responds with:

   * `Prediction`: 0 (non-toxic) or 1 (toxic)
   * `Probability`: e.g., 0.932
   * `Requests used`: 1
   * `Requests remaining`: 1000


---

##  Dashboard

Visualizations are embedded directly in the dashboard:

*  Correlation heatmap
*  Threshold frequency bar chart
*  Radar chart of toxicity distribution

---

##  Installation

```bash
git clone https://github.com/yourusername/toxic-comment-api.git
cd toxic-comment-api
pip install -r requirements.txt
python app.py
```

---

##  Notes

* No registration or login is required.
* The prediction model is optimized for performance and speed.




















