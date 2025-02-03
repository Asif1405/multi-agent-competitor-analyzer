# **Competitor Analysis using LLM**

## **Overview**

This is a **Gradio-powered AI application** that leverages OpenAI’s **GPT-4o** to perform **comprehensive competitor analysis** for businesses. The app provides two modes of operation:

1. **Product-Based Search** – Enter a product name and specify a target region (default: global) to find top competitors.  
2. **Direct URL Analysis** – Provide a competitor’s website URL for immediate analysis.

The system automates web searches, extracts key insights, and generates a structured report covering critical business aspects.

---

## **How It Works**

The system operates in three key phases:

1. **Competitor Discovery**  
   - Identifies leading competitors based on the provided product name and region.  
   - Retrieves official websites of the top competitors.  

2. **Competitor Website Analysis**  
   - Scrapes and extracts key details about the competitor’s organization.  

3. **Market & Sentiment Analysis**  
   - Collects external data, including market trends, customer reviews, and financial insights.  

### **Final Report Includes:**  

✅ **Company Overview**  
✅ **Strengths & Weaknesses**  
✅ **Market Position**  
✅ **Unique Selling Proposition (USP)**  
✅ **Online Presence & Branding**  
✅ **Marketing & Advertising Strategy**  
✅ **Key Products & Services**  
✅ **Customer Review Summary & Sentiment**  
✅ **Market & Financial Data**  
✅ **Third-Party Evaluation**  
✅ **Key Takeaways**  

---

## **Workflow**

### **1. Product-Based Search**  
🔹 **Input:** Product name & target region (optional)  
🔹 **Process:**  
   - Searches the web for **top competitors** in the specified region.  
   - Retrieves **official websites** of competitors.  
   - Select a **competitor for deep analysis**.  
   - Extracts **internal data** from the competitor’s website.  
   - Gathers **external insights** (market data, customer reviews, financials).  
   - **Generates a detailed competitor analysis report**.  

### **2. URL-Based Search**  
🔹 **Input:** Direct competitor website URL  
🔹 **Process:**  
   - Scrapes the website to **gather internal data**.  
   - Collects **market intelligence, customer reviews, and financials**.  
   - **Generates a structured competitor analysis report**.  

---

## **Installation Guide**

### **Prerequisites**  
- Python **3.11**  
- Docker & Docker Compose (for containerized deployment)  

### **Local Installation**  

1️⃣ **Create a virtual environment**  

```bash
python3 -m venv venv
```

2️⃣ Activate the virtual environment

- Mac/Linux:

```bash
source venv/bin/activate
```

- Windows:

```bash
venv\Scripts\activate
```


3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

4️⃣ Run the app

```bash
python main.py
```

### **Docker Installation**

1️⃣ Ensure Docker and Docker Compose are installed

2️⃣ Run the application using Docker

```bash
docker compose up -d --build
```

## Usage Instructions

1️⃣ Open a web browser and go to:
```bash
http://localhost:8090
```

2️⃣ Enter either:

    A product name (with an optional location)
    A competitor’s website URL

3️⃣ The system will generate a detailed competitor report.


## Future Improvements

🔹 Database Integration – Store competitor data for historical tracking.
🔹 API Exposure – Enable seamless integration with other business tools.
🔹 Enhanced UI – Improve usability with interactive visualizations.
🔹 Deeper NLP Analysis – Perform advanced text analytics on market sentiment.
