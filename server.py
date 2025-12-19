"""
FastMCP Server Implementation
A complete example MCP server with Tools, Resources, and Prompts
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List
from fastmcp import FastMCP
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataAnalyticsServer:
    """
    Comprehensive MCP Server for Data Analytics
    Demonstrates Tools, Resources, and Prompts
    """
    
    def __init__(self):
        self.mcp = FastMCP(name="Data Analytics Server")
        self._setup_tools()
        self._setup_resources()
        self._setup_prompts()
        logger.info("Data Analytics Server initialized")
    
    def _setup_tools(self):
        """Register all tool capabilities"""
        
        @self.mcp.tool()
        def fetch_sales_data(region: str, year: int) -> dict:
            """
            Fetch sales data for a specific region and year.
            
            Args:
                region: Sales region (APAC, EMEA, AMERICAS)
                year: Fiscal year
            
            Returns:
                Dictionary with sales metrics
            """
            # Simulated sales database
            sales_db = {
                "APAC": {
                    2024: {
                        "total_revenue": 125000.50,
                        "units_sold": 1250,
                        "growth_rate": 0.15,
                        "top_product": "Analytics Pro",
                        "customer_count": 150
                    },
                    2023: {
                        "total_revenue": 108700.25,
                        "units_sold": 1050,
                        "growth_rate": 0.12,
                        "top_product": "Analytics Starter",
                        "customer_count": 120
                    }
                },
                "EMEA": {
                    2024: {
                        "total_revenue": 98500.75,
                        "units_sold": 890,
                        "growth_rate": 0.08,
                        "top_product": "Enterprise Suite",
                        "customer_count": 110
                    },
                    2023: {
                        "total_revenue": 91100.50,
                        "units_sold": 820,
                        "growth_rate": 0.10,
                        "top_product": "Analytics Pro",
                        "customer_count": 95
                    }
                },
                "AMERICAS": {
                    2024: {
                        "total_revenue": 156000.00,
                        "units_sold": 1400,
                        "growth_rate": 0.22,
                        "top_product": "Enterprise Suite",
                        "customer_count": 200
                    },
                    2023: {
                        "total_revenue": 127800.00,
                        "units_sold": 1150,
                        "growth_rate": 0.18,
                        "top_product": "Analytics Pro",
                        "customer_count": 175
                    }
                }
            }
            
            if region not in sales_db or year not in sales_db[region]:
                return {
                    "error": f"Data not found for {region} in {year}",
                    "available_regions": list(sales_db.keys())
                }
            
            data = sales_db[region][year]
            logger.info(f"Fetched sales data for {region} ({year})")
            return {
                "region": region,
                "year": year,
                **data
            }
        
        @self.mcp.tool()
        def calculate_metrics(revenue: float, expenses: float) -> dict:
            """
            Calculate profitability metrics.
            
            Args:
                revenue: Total revenue
                expenses: Total expenses
            
            Returns:
                Dictionary with calculated metrics
            """
            if revenue <= 0:
                return {"error": "Revenue must be greater than 0"}
            
            profit = revenue - expenses
            margin = (profit / revenue * 100)
            roi = (profit / expenses * 100) if expenses > 0 else 0
            
            logger.info(f"Calculated metrics: Revenue={revenue}, Profit={profit}")
            return {
                "revenue": revenue,
                "expenses": expenses,
                "profit": profit,
                "profit_margin_percentage": round(margin, 2),
                "roi_percentage": round(roi, 2),
                "is_profitable": profit > 0
            }
        
        @self.mcp.tool()
        def forecast_trend(region: str, months_ahead: int = 3) -> dict:
            """
            Generate trend forecast for a region.
            
            Args:
                region: Sales region
                months_ahead: Number of months to forecast
            
            Returns:
                Dictionary with forecast data
            """
            base_growth = {"APAC": 0.15, "EMEA": 0.08, "AMERICAS": 0.22}.get(region, 0.10)
            
            forecast = []
            current_revenue = 125000
            
            for month in range(1, months_ahead + 1):
                current_revenue *= (1 + base_growth / 12)
                forecast.append({
                    "month": month,
                    "projected_revenue": round(current_revenue, 2),
                    "confidence": 0.95 - (month * 0.05)
                })
            
            logger.info(f"Generated {months_ahead}-month forecast for {region}")
            return {
                "region": region,
                "forecast_period_months": months_ahead,
                "base_growth_rate": base_growth,
                "forecast": forecast
            }
    
    def _setup_resources(self):
        """Register all resource capabilities"""
        
        @self.mcp.resource("resource://company/config")
        def get_company_config() -> dict:
            """
            Provide company configuration as a static resource.
            """
            return {
                "company": "DataCorp Analytics",
                "founded": 2015,
                "headquarters": "San Francisco, CA",
                "departments": [
                    "Sales",
                    "Engineering",
                    "Marketing",
                    "Operations",
                    "Finance"
                ],
                "employees": 250,
                "main_product": "Enterprise Analytics Platform",
                "website": "https://datacorp-analytics.com"
            }
        
        @self.mcp.resource("report://{report_type}")
        def get_report(report_type: str) -> str:
            """
            Provide dynamic reports based on type.
            """
            reports = {
                "quarterly": """
                Q4 2024 Performance Review
                ===========================
                Revenue: $379,501.25
                Growth: +15.8% YoY
                Key Highlights:
                - AMERICAS region exceeded targets by 12%
                - New enterprise customers: +45
                - Customer retention: 98.5%
                - NPS Score: 72
                """,
                "annual": """
                2024 Annual Report
                ==================
                Total Revenue: $1,489,045.00
                Growth: +14.2% YoY
                Regions:
                - AMERICAS: $483,001.25 (32.4%)
                - APAC: $378,500.25 (25.4%)
                - EMEA: $270,543.50 (18.2%)
                Key Achievements:
                - 465 new customers
                - 98.2% customer satisfaction
                - 3 major product releases
                """,
                "compliance": """
                2024 Compliance Audit Report
                =============================
                Status: PASSED
                Date: 2024-12-01
                Auditor: Big Four Audit Firm
                Findings:
                - SOC 2 Type II Certified
                - GDPR Compliant
                - Data Security: Excellent
                - Financial Controls: Satisfactory
                Recommendations: None
                """
            }
            
            if report_type not in reports:
                return f"Report '{report_type}' not found. Available: {', '.join(reports.keys())}"
            
            logger.info(f"Retrieved {report_type} report")
            return reports[report_type].strip()
        
        @self.mcp.resource("database://{table_name}")
        def query_database(table_name: str) -> List[Dict]:
            """
            Query database tables as resources.
            """
            tables = {
                "customers": [
                    {"id": 1, "name": "Acme Corp", "region": "AMERICAS", "mrr": 5000},
                    {"id": 2, "name": "Tech Industries", "region": "EMEA", "mrr": 3500},
                    {"id": 3, "name": "Innovation Labs", "region": "APAC", "mrr": 4200}
                ],
                "products": [
                    {"id": 1, "name": "Analytics Pro", "price": 99, "tier": "professional"},
                    {"id": 2, "name": "Enterprise Suite", "price": 499, "tier": "enterprise"},
                    {"id": 3, "name": "Analytics Starter", "price": 29, "tier": "starter"}
                ],
                "transactions": [
                    {"id": 1, "date": "2024-12-01", "amount": 15000, "type": "sale"},
                    {"id": 2, "date": "2024-12-02", "amount": 8500, "type": "refund"},
                    {"id": 3, "date": "2024-12-03", "amount": 22000, "type": "sale"}
                ]
            }
            
            if table_name not in tables:
                return [{"error": f"Table '{table_name}' not found"}]
            
            logger.info(f"Queried database table: {table_name}")
            return tables[table_name]
    
    def _setup_prompts(self):
        """Register all prompt templates"""
        
        @self.mcp.prompt()
        def sales_analysis_prompt(region: str) -> List[Dict]:
            """Template for regional sales analysis."""
            return [
                {
                    "role": "system",
                    "content": f"""You are a sales analyst specializing in the {region} market.
Your task is to analyze sales trends, identify opportunities, and provide actionable insights.
Focus on:
1. Growth trends and patterns
2. Customer acquisition and retention
3. Revenue optimization opportunities
4. Competitive positioning
5. Regional market dynamics

Provide specific, data-driven recommendations."""
                },
                {
                    "role": "user",
                    "content": f"""Please analyze the sales performance for {region} and provide:
1. Current performance metrics
2. Key growth drivers
3. Areas needing improvement
4. Opportunities for expansion
5. 3-month forecast
6. Recommended actions"""
                }
            ]
        
        @self.mcp.prompt()
        def budget_planning_prompt() -> List[Dict]:
            """Template for budget planning."""
            return [
                {
                    "role": "system",
                    "content": """You are a financial planning expert specializing in SaaS budgeting.
Your expertise includes:
- Cost optimization and allocation
- Revenue forecasting and modeling
- Risk assessment and contingency planning
- Resource optimization
- Scenario planning

Provide realistic, actionable budget recommendations."""
                },
                {
                    "role": "user",
                    "content": """Based on the provided financial data, help me create an optimized budget plan for Q1 2025:
1. Recommended departmental allocations
2. Revenue targets by region
3. Contingency reserves
4. Risk mitigation strategies
5. KPIs to track
6. Monthly milestones and checkpoints"""
                }
            ]
        
        @self.mcp.prompt()
        def technical_analysis_prompt(metric: str = "revenue") -> List[Dict]:
            """Template for technical data analysis."""
            return [
                {
                    "role": "system",
                    "content": f"""You are a technical data analyst.
Analyze the {metric} metric using statistical methods and provide insights.
Include:
- Descriptive statistics
- Trend analysis
- Anomaly detection
- Correlation analysis
- Predictive insights"""
                },
                {
                    "role": "user",
                    "content": f"""Perform a comprehensive technical analysis of {metric}:
1. Statistical summary
2. Trend identification
3. Outlier analysis
4. Pattern recognition
5. Predictive model suggestions
6. Visualization recommendations"""
                }
            ]
    
    def run(self):
        """Start the MCP server"""
        logger.info("Starting MCP server...")
        self.mcp.run(transport="stdio")


if __name__ == "__main__":
    server = DataAnalyticsServer()
    server.run()
