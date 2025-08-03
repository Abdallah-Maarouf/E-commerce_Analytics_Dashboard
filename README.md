# Brazilian E-commerce Analytics Dashboard

A comprehensive end-to-end data analysis portfolio project that demonstrates real-world data science skills through the analysis of Brazilian e-commerce data. This project showcases the complete data science pipeline from data collection through deployment, focusing on answering specific business questions that provide actionable value to e-commerce stakeholders.

## 🎯 Project Overview

This project transforms raw Brazilian e-commerce data into actionable business insights through a modern, interactive dashboard. The analysis addresses five critical business questions:

1. **Market Expansion**: Identify underserved Brazilian states with high growth potential
2. **Customer Analytics**: Predict high-value customers and optimize lifetime value
3. **Seasonal Intelligence**: Forecast inventory needs and understand seasonal patterns
4. **Payment & Operations**: Analyze payment behaviors and operational performance
5. **Executive Overview**: Provide comprehensive KPIs and business metrics

## 🚀 Key Features

- **Interactive Dark-Themed Dashboard**: Modern Streamlit web application with purple/navy theme
- **Comprehensive Business Analysis**: Five distinct analytical modules addressing key business questions
- **Predictive Analytics**: Customer lifetime value prediction and demand forecasting
- **Geographic Insights**: Brazilian market penetration and expansion opportunity analysis
- **Operational Intelligence**: Payment behavior analysis and delivery performance metrics

## 📊 Dashboard Pages

- **Executive Overview**: High-level KPIs, revenue trends, and key business metrics
- **Market Expansion**: Geographic analysis, market penetration maps, and expansion opportunities
- **Customer Analytics**: RFM segmentation, CLV analysis, and retention insights
- **Seasonal Intelligence**: Demand forecasting, seasonal patterns, and inventory optimization
- **Payment & Operations**: Payment behavior analysis and operational performance metrics

## 🛠 Technology Stack

- **Data Processing**: Python, Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Dashboard**: Streamlit
- **Machine Learning**: Scikit-learn (for predictive models)
- **Version Control**: Git, GitHub
- **Deployment**: Streamlit Cloud

## 📁 Project Structure

```
ecommerce-analytics-dashboard/
├── data/                          # Raw and processed datasets
│   ├── olist_customers_dataset.csv
│   ├── olist_orders_dataset.csv
│   └── ... (other CSV files)
├── src/                           # Source code modules
│   ├── data_loader.py            # Data loading utilities
│   ├── data_cleaner.py           # Data cleaning functions
│   ├── feature_engineer.py       # Feature engineering
│   └── analysis/                 # Business analysis modules
├── dashboard/                     # Streamlit dashboard components
│   ├── app.py                    # Main dashboard application
│   ├── pages/                    # Individual dashboard pages
│   └── components/               # Reusable UI components
├── notebooks/                     # Jupyter notebooks for exploration
├── reports/                       # Analysis reports and documentation
│   ├── phase_reports/            # Step-by-step analysis documentation
│   └── case_study.md             # Comprehensive business case study
└── requirements.txt              # Python dependencies
```

## 🎯 Business Questions Addressed

### 1. Market Expansion Analysis
- Which Brazilian states represent the biggest untapped market opportunities?
- How should seller distribution be optimized to reduce delivery times?
- What are the geographic patterns in customer demand vs seller availability?

### 2. Customer Lifetime Value Optimization
- Which customers will become high-value repeat buyers within their first 3 purchases?
- How does delivery experience impact customer retention rates?
- What customer segments provide the highest lifetime value?

### 3. Seasonal Demand Intelligence
- How do Brazilian cultural events (Christmas, Carnival, Black Friday) impact different product categories?
- What inventory levels should be maintained 3 months ahead based on seasonal patterns?
- Which product categories show the strongest seasonal variance?

### 4. Payment Behavior & Operations Analysis
- How do payment method preferences vary by region and customer segment?
- What is the relationship between installment plans and customer satisfaction?
- How do delivery delays impact customer satisfaction and repeat purchases?

### 5. Executive Performance Metrics
- What are the key performance indicators for overall business health?
- How do different regions and product categories contribute to revenue growth?
- What operational metrics most strongly correlate with business success?

## 📈 Key Insights & Business Impact

This project demonstrates the ability to:
- Transform raw data into actionable business intelligence
- Build predictive models for customer behavior and demand forecasting
- Create professional, interactive dashboards for stakeholder communication
- Apply statistical analysis to solve real-world business problems
- Document methodology and findings in a business-friendly format

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git for version control
- Brazilian E-commerce dataset (Olist dataset from Kaggle)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/[username]/ecommerce-analytics-dashboard.git
cd ecommerce-analytics-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place the Brazilian e-commerce dataset CSV files in the `data/` directory

4. Run the dashboard:
```bash
streamlit run dashboard/app.py
```

## 📊 Dataset Information

This project uses the Brazilian E-Commerce Public Dataset by Olist, which contains:
- 100k orders from 2016 to 2018
- Order details, customer information, and product data
- Geolocation data for customers and sellers
- Payment and review information
- Product category translations

**Dataset Source**: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## 🎨 Dashboard Design

The dashboard features a modern dark theme with:
- **Primary Colors**: Dark purple (#1a1625) and navy backgrounds
- **Accent Colors**: Vibrant orange, blue, green, and pink for different metrics
- **Interactive Elements**: Hover effects, smooth transitions, and responsive design
- **Professional Layout**: Clean typography and intuitive navigation

## 📝 Documentation

Comprehensive documentation includes:
- **Methodology Documentation**: Technical approach and analytical choices
- **Phase Reports**: Step-by-step analysis findings for each business question
- **Case Study Report**: Executive summary with business impact quantification
- **Code Documentation**: Inline comments and function documentation

## 🔄 Development Workflow

This project follows a collaborative development approach:
1. **Requirements Gathering**: Define business questions and success criteria
2. **Data Engineering**: Clean, process, and prepare data for analysis
3. **Business Analysis**: Answer each business question with statistical analysis
4. **Dashboard Development**: Create interactive visualizations and user interface
5. **Documentation**: Comprehensive reporting and methodology documentation
6. **Deployment**: Public deployment with professional presentation

## 🤝 Contributing

This is a portfolio project demonstrating data science capabilities. The development process emphasizes:
- Clean, well-documented code
- Meaningful commit messages following conventional commit standards
- Comprehensive testing and validation
- Professional documentation and presentation

## 📄 License

This project is created for educational and portfolio purposes.

## 👤 Author

**Abdallah Maarouf Sayed**
- LinkedIn: [Your LinkedIn Profile]
- GitHub: [Your GitHub Profile]

---

*This project demonstrates end-to-end data science capabilities including data engineering, statistical analysis, machine learning, dashboard development, and business communication skills.*
