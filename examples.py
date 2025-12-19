"""
MCP Client Usage Examples
==========================

This file demonstrates 6 real-world usage patterns for the MCP client:
1. Sales Data Analysis Workflow
2. Resource Access Patterns
3. Prompt Template Usage
4. Batch Operations
5. Complex Analysis Workflow
6. Error Handling & Recovery

Each example shows best practices and common patterns.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_sales_analysis():
    """
    Example 1: Sales Data Analysis Workflow

    Demonstrates:
    - Basic client connection
    - Calling a tool with parameters
    - Processing and displaying results
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Sales Data Analysis Workflow")
    print("="*60)

    # Create client (no arguments needed)
    client = MCPClient()

    try:
        # Connect to server (launches server.py internally)
        await client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Fetch sales data for APAC region
        logger.info("Fetching sales data for APAC region...")
        result = await client.call_tool(
            "fetch_sales_data",
            {"region": "APAC", "year": 2024}
        )

        # Parse the result
        data = json.loads(result.content[0].text)

        # Display results
        print("\n📊 Sales Data for APAC (2024):")
        revenue = data.get("total_revenue", 0)
        growth_rate = data.get("growth_rate", 0)
        active_customers = data.get("active_customers", 0)
        region = data.get("region", "N/A")
        print(f"  • Total Revenue: ${revenue:,}")
        print(f"  • Growth Rate: {growth_rate*100:.1f}%")
        print(f"  • Active Customers: {active_customers:,}")
        print(f"  • Region: {region}")

        logger.info("✓ Sales analysis complete")

    except Exception as e:
        logger.error(f"❌ Error in sales analysis: {e}")
        raise
    finally:
        await client.cleanup()


async def example_resource_access():
    """
    Example 2: Resource Access Patterns

    Demonstrates:
    - Reading static resources
    - Reading dynamic resources with parameters
    - Handling resource URIs
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Resource Access Patterns")
    print("="*60)

    client = MCPClient()

    try:
        await client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Read static resource
        logger.info("Reading company configuration...")
        config_result = await client.get_resource("resource://company/config")
        config = json.loads(config_result.contents[0].text)

        print("\n🏢 Company Configuration:")
        print(f"  • Company: {config.get('company', 'N/A')}")
        print(f"  • Founded: {config.get('founded', 'N/A')}")
        print(f"  • Employees: {config.get('employees', 0):,}")
        print(f"  • Departments: {', '.join(config.get('departments', []))}")

        # Read dynamic resource
        logger.info("Generating quarterly report...")
        report_result = await client.get_resource("report://quarterly")

        print("\n📄 Quarterly Report:")
        print(f"  • Content: {report_result.contents[0].text[:200]}...")
        print(f"  • Type: Quarterly Report")
        print(f"  • Generated: {report_result.contents[0].uri or 'N/A'}")
        print(f"  • Status: Available")

        logger.info("✓ Resource access complete")

    except Exception as e:
        logger.error(f"❌ Error accessing resources: {e}")
        raise
    finally:
        await client.cleanup()


async def example_prompt_usage():
    """
    Example 3: Prompt Template Usage

    Demonstrates:
    - Retrieving prompt templates
    - Using prompts with different parameters
    - Formatting for LLM usage
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Prompt Template Usage")
    print("="*60)

    client = MCPClient()

    try:
        await client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Get sales analysis prompt
        logger.info("Retrieving sales analysis prompt template...")
        prompt = await client.get_prompt(
            "sales_analysis_prompt",
            {"region": "APAC"}
        )

        print("\n📝 Sales Analysis Prompt Template:")
        for message in prompt:
            role = getattr(message, 'role', 'unknown')
            content_obj = getattr(message, 'content', None)
            content = ""
            if content_obj and hasattr(content_obj, 'text'):
                content = content_obj.text
                # Parse if JSON
                try:
                    parsed = json.loads(content)
                    role = parsed.get("role", role)
                    content = parsed.get("content", content)
                except json.JSONDecodeError:
                    pass
            print(f"\n  [{role.upper()}]")
            print(f"  {content[:200]}..." if len(content) > 200 else f"  {content}")

        # Get budget planning prompt
        logger.info("Retrieving budget planning prompt...")
        budget_prompt = await client.get_prompt(
            "budget_planning_prompt",
            {"department": "Engineering", "year": "2025"}
        )

        print("\n📝 Budget Planning Prompt:")
        if budget_prompt:
            print(f"  • Messages: {len(budget_prompt)}")
            print(f"  • For: Engineering Department, 2025")
        else:
            print(f"  • Failed to retrieve prompt")

        logger.info("✓ Prompt retrieval complete")

    except Exception as e:
        logger.error(f"❌ Error retrieving prompts: {e}")
        raise
    finally:
        await client.cleanup()


async def example_batch_operations():
    """
    Example 4: Batch Operations

    Demonstrates:
    - Concurrent tool calls
    - Using asyncio.gather for parallel execution
    - Processing multiple results efficiently
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Operations")
    print("="*60)

    client = MCPClient()

    try:
        await client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Fetch sales data for multiple regions concurrently
        logger.info("Fetching sales data for multiple regions...")
        regions = ["APAC", "EMEA", "AMERICAS"]

        # Create tasks for concurrent execution
        tasks = [
            client.call_tool(
                "fetch_sales_data",
                {"region": region, "year": 2024}
            )
            for region in regions
        ]

        # Execute all tasks concurrently
        tool_results = await asyncio.gather(*tasks)

        print("\n🌍 Sales Data Comparison (2024):")
        print("-" * 60)

        results = []
        for region, tool_result in zip(regions, tool_results):
            data = json.loads(tool_result.content[0].text)
            results.append(data)
            revenue = data.get("total_revenue", 0)
            growth = data.get("growth_rate", 0) * 100
            print(f"\n  {region}:")
            print(f"    Revenue: ${revenue:,}")
            print(f"    Growth:  {growth:.1f}%")

        # Calculate totals
        total_revenue = sum(r.get("total_revenue", 0) for r in results)
        print(f"\n  TOTAL REVENUE: ${total_revenue:,}")

        logger.info("✓ Batch operations complete")

    except Exception as e:
        logger.error(f"❌ Error in batch operations: {e}")
        raise
    finally:
        await client.cleanup()


async def example_complex_workflow():
    """
    Example 5: Complex Analysis Workflow

    Demonstrates:
    - Chaining multiple tool calls
    - Combining results from different tools
    - Building complete business workflows
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Complex Analysis Workflow")
    print("="*60)

    client = MCPClient()

    try:
        await client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Step 1: Fetch sales data
        logger.info("Step 1: Fetching sales data...")
        sales_result = await client.call_tool(
            "fetch_sales_data",
            {"region": "APAC", "year": 2024}
        )
        sales_data = json.loads(sales_result.content[0].text)

        revenue = sales_data.get("total_revenue", 0)
        print(f"\n📊 Step 1 - Sales Data Retrieved:")
        print(f"  • Revenue: ${revenue:,}")

        # Step 2: Calculate metrics
        logger.info("Step 2: Calculating profitability metrics...")
        expenses = revenue * 0.65  # Assume 65% expenses
        metrics_result = await client.call_tool(
            "calculate_metrics",
            {"revenue": revenue, "expenses": expenses}
        )
        metrics = json.loads(metrics_result.content[0].text)

        profit = metrics.get("profit", 0)
        margin = metrics.get("profit_margin_percentage", 0)
        print(f"\n💰 Step 2 - Metrics Calculated:")
        print(f"  • Profit: ${profit:,}")
        print(f"  • Margin: {margin:.1f}%")

        # Step 3: Generate forecast
        logger.info("Step 3: Generating forecast...")
        forecast_result = await client.call_tool(
            "forecast_trend",
            {"region": "APAC", "months_ahead": 6}
        )
        forecast = json.loads(forecast_result.content[0].text)

        predicted_revenue = forecast.get("predicted_revenue", 0)
        confidence = forecast.get("confidence_level", 0) * 100
        print(f"\n📈 Step 3 - Forecast Generated:")
        print(f"  • Predicted Revenue (6 months): ${predicted_revenue:,}")
        print(f"  • Confidence: {confidence:.1f}%")

        # Final analysis
        print(f"\n✅ Complete Analysis:")
        print(f"  • Current Revenue: ${revenue:,}")
        print(f"  • Current Profit: ${profit:,}")
        print(f"  • Forecasted Revenue: ${predicted_revenue:,}")
        print(f"  • Potential Profit: ${predicted_revenue * (margin/100):,.0f}")

        logger.info("✓ Complex workflow complete")

    except Exception as e:
        logger.error(f"❌ Error in workflow: {e}")
        raise
    finally:
        await client.cleanup()


async def example_error_handling():
    """
    Example 6: Error Handling & Recovery

    Demonstrates:
    - Proper error handling patterns
    - Graceful degradation
    - Retry logic
    - Validation
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Error Handling & Recovery")
    print("="*60)

    client = MCPClient()

    try:
        await client.connect_to_server("server.py")
        logger.info("✓ Connected to MCP server")

        # Example 1: Handle invalid input
        print("\n📋 Test 1: Invalid Region")
        try:
            result = await client.call_tool(
                "fetch_sales_data",
                {"region": "INVALID_REGION", "year": 2024}
            )
        except Exception as e:
            print(f"  ⚠️  Caught error: {type(e).__name__}")
            print(f"  → Using fallback data for AMERICAS instead")
            result = await client.call_tool(
                "fetch_sales_data",
                {"region": "AMERICAS", "year": 2024}
            )
            data = json.loads(result.content[0].text)
            revenue = data.get("total_revenue", 0)
            print(f"  ✓ Fallback successful: ${revenue:,}")

        # Example 2: Handle missing resource
        print("\n📋 Test 2: Missing Resource")
        try:
            content = await client.get_resource("resource://nonexistent")
        except Exception as e:
            print(f"  ⚠️  Caught error: {type(e).__name__}")
            print(f"  → Using default configuration instead")
            content = {"status": "default", "message": "Using fallback config"}
            print(f"  ✓ Using fallback: {content['status']}")

        # Example 3: Validation before calling
        print("\n📋 Test 3: Input Validation")
        year = 1900  # Invalid year
        if year < 2020 or year > 2030:
            print(f"  ⚠️  Invalid year: {year}")
            year = 2024
            print(f"  → Corrected to: {year}")

        result = await client.call_tool(
            "fetch_sales_data",
            {"region": "APAC", "year": year}
        )
        data = json.loads(result.content[0].text)
        print(f"  ✓ Successfully fetched data for {year}")

        # Example 4: Timeout handling
        print("\n📋 Test 4: Timeout Protection")
        try:
            # This would timeout in real scenario
            result = await asyncio.wait_for(
                client.call_tool(
                    "fetch_sales_data",
                    {"region": "APAC", "year": 2024}
                ),
                timeout=10.0  # 10 second timeout
            )
            data = json.loads(result.content[0].text)
            print(f"  ✓ Completed within timeout")
        except asyncio.TimeoutError:
            print(f"  ⚠️  Operation timed out")
            print(f"  → Would retry or use cached data")

        logger.info("✓ Error handling examples complete")

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise
    finally:
        await client.cleanup()


async def main():
    """
    Run all examples in sequence
    """
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*16 + "MCP REAL-WORLD USAGE EXAMPLES" + " "*13 + "║")
    print("╚" + "="*58 + "╝")

    try:
        # Run all examples
        await example_sales_analysis()
        await example_resource_access()
        await example_prompt_usage()
        await example_batch_operations()
        await example_complex_workflow()
        await example_error_handling()

        # Summary
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext Steps:")
        print("  • Review the code in examples.py")
        print("  • Modify examples for your use case")
        print("  • Build your own MCP application")
        print("  • Reference client.py for advanced patterns")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Examples failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())