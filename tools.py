from langchain.tools import Tool
from mock_data import get_order, update_order, get_product, search_products, get_customer, update_customer_preferences, get_loyalty_points
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return {"error": "API key not found in .env file"}
    
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "city": f"{data['location']['name']}, {data['location']['country']}",
            "weather": data['current']['condition']['text'],
            "temp_c": data['current']['temp_c'],
            "temp_f": data['current']['temp_f'],
            "feelslike_c": data['current']['feelslike_c'],
            "feelslike_f": data['current']['feelslike_f'],
            "humidity": data['current']['humidity'],
            "wind_kph": data['current']['wind_kph'],
            "last_updated": data['current']['last_updated']
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except KeyError as e:
        return {"error": f"Invalid data received from API - missing key: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def weather_based_recommendation(weather_condition: str):
    """Recommend clothing based on weather conditions."""
    weather_condition = weather_condition.lower()
    if "rain" in weather_condition or "drizzle" in weather_condition:
        return "I recommend wearing waterproof clothing like a raincoat and quick-dry pants. Don’t forget an umbrella! ☔"
    elif "cloudy" in weather_condition:
        return "Wear lightweight, breathable clothes like a cotton t-shirt and shorts. A light jacket might be handy in case of rain. 😊"
    elif "sunny" in weather_condition:
        return "Go for light, airy clothes like a linen shirt and shorts. Sunglasses and sunscreen are a must! ☀️"
    elif "clear" in weather_condition:
        return "Opt for comfortable, breathable clothing like a cotton dress or t-shirt with shorts. Stay hydrated! 😎"
    else:
        return "I suggest lightweight and comfortable clothes, like a cotton t-shirt and pants, suitable for most weather conditions. 😊"

# Define tools for LangChain agent
tools = [
    Tool(
        name="CheckOrderStatus",
        func=get_order,
        description="Check the status of an order by order ID."
    ),
    Tool(
        name="CancelOrder",
        func=lambda order_id: update_order(order_id, "canceled"),
        description="Cancel an order by order ID if it is pending."
    ),
    Tool(
        name="ProcessReturn",
        func=lambda order_id: update_order(order_id, "returned"),
        description="Process a return for an order by order ID if eligible."
    ),
    Tool(
        name="SearchProducts",
        func=search_products,
        description="Search products by name or category."
    ),
    Tool(
        name="GetProductDetails",
        func=get_product,
        description="Get details of a product by product ID."
    ),
    Tool(
        name="RecommendProducts",
        func=lambda category: search_products(category),
        description="Recommend products based on a category."
    ),
    Tool(
        name="GetCustomerInfo",
        func=get_customer,
        description="Retrieve customer information by customer ID."
    ),
    Tool(
        name="UpdateCustomerPreferences",
        func=update_customer_preferences,
        description="Update customer preferences by customer ID and preference."
    ),
    Tool(
        name="CheckLoyaltyPoints",
        func=get_loyalty_points,
        description="Check loyalty points for a customer by customer ID."
    ),
    Tool(
        name="GetWeather",
        func=get_weather,
        description="Get current weather for a city."
    ),
    Tool(
        name="WeatherBasedRecommendation",
        func=weather_based_recommendation,
        description="Recommend clothing based on weather conditions."
    )
]
