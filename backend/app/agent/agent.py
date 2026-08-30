import os
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from groq import Groq

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import (
    search_products, 
    get_product, 
    recommend_addons, 
    recommend_upgrade, 
    create_cart, 
    add_to_cart, 
    get_cart,
    approve_purchase,
    create_order
)
from app.core.config import settings
from app.agent.session import get_session


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, UUID):
        return str(obj)

    raise TypeError(
        f"Object of type {type(obj).__name__} "
        "is not JSON serializable"
    )


SEARCH_PRODUCTS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": (
            "Search the merchant's product catalog. "
            "Use this whenever the user asks to find "
            "or recommend products."
        ),
        "parameters": {
            "type": "object",
            "properties": {

                "query": {
                    "type": "string",
                    "description": (
                        "Semantic description of "
                        "the product the user wants."
                    )
                },

                "max_price": {
                    "type": "number",
                    "description": (
                        "Maximum acceptable sale price "
                        "in INR."
                    )
                },

                "min_price": {
                    "type": "number",
                    "description": (
                        "Minimum acceptable sale price "
                        "in INR."
                    )
                },

                "brand": {
                    "type": "string",
                    "description": (
                        "Brand requested by the user."
                    )
                },

                "min_discount": {
                    "type": "number",
                    "description": (
                        "Minimum discount percentage."
                    )
                },

                "top_k": {
                    "type": "integer",
                    "description": (
                        "Number of products to return."
                    ),
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

GET_PRODUCT_TOOL = {
    "type": "function",
    "function": {
        "name": "get_product",
        "description": (
            "Get complete information about a specific "
            "product after the user selects or refers "
            "to that product."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Unique product ID."
                }
            },
            "required": ["product_id"]
        }
    }
}


RECOMMEND_ADDONS_TOOL = {
    "type": "function",
    "function": {
        "name": "recommend_addons",
        "description": (
            "Recommend optional complementary products "
            "for a product the buyer has selected. "
            "Only use this after a product has been selected. "
            "Recommendations are optional and must never "
            "be treated as buyer approval."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": (
                        "ID of the selected product."
                    )
                },
                "budget_remaining": {
                    "type": "number",
                    "description": (
                        "Remaining buyer budget in INR."
                    )
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of recommendations."
                    ),
                    "default": 3
                }
            },
            "required": [
                "product_id"
            ]
        }
    }
}

UPSELL_PRODUCT_TOOL = {
    "type": "function",
    "function": {
        "name": "recommend_upgrade",
        "description": (
            "Find a better or higher-value upgrade "
            "for a product the buyer has selected. "
            "Use this when the buyer wants a better, "
            "larger, more powerful, or premium alternative."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": (
                        "The product ID of the currently "
                        "selected product."
                    )
                }
            },
            "required": ["product_id"]
        }
    }
}

CREATE_CART_TOOL = {
    "type": "function",
    "function": {
        "name": "create_cart",
        "description": (
            "Create a new shopping cart for the buyer. "
            "Use this when the buyer wants to start "
            "building a purchase."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


ADD_TO_CART_TOOL = {
    "type": "function",
    "function": {
        "name": "add_to_cart",
        "description": (
            "Add a specific selected product to the "
            "buyer's shopping cart. "
            "Only use this when the buyer has explicitly "
            "asked to add the product to the cart."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {
                    "type": "string",
                    "description": "Active shopping cart ID."
                },
                "product_id": {
                    "type": "string",
                    "description": "Selected product ID."
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to add.",
                    "default": 1
                }
            },
            "required": [
                "cart_id",
                "product_id"
            ]
        }
    }
}

GET_CART_TOOL = {
    "type": "function",
    "function": {
        "name": "get_cart",
        "description": (
            "Get the current contents, quantities, "
            "prices and total of a shopping cart."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {
                    "type": "string",
                    "description": "Shopping cart ID."
                }
            },
            "required": [
                "cart_id"
            ]
        }
    }
}

APPROVE_CART_TOOL = {
    "type": "function",
    "function": {
        "name": "approve_purchase",
        "description": (
            "Approve the buyer's current cart for purchase. "
            "ONLY call this when the buyer has explicitly "
            "confirmed that they approve the final cart total. "
            "Never infer approval from providing an address, "
            "payment method, or saying they want to checkout."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {
                    "type": "string",
                    "description": "The active cart ID."
                }
            },
            "required": ["cart_id"]
        }
    }
}

CREATE_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "create_order",
        "description": (
            "Create a payment-ready order from the buyer's "
            "approved cart. This tool may only be used after "
            "explicit buyer approval. It creates the internal "
            "order and Razorpay order. Never claim that payment "
            "has succeeded; this tool only prepares the payment."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {
                    "type": "string",
                    "description": (
                        "The active cart ID."
                    )
                }
            },
            "required": ["cart_id"]
        }
    }
}

tools = [
    SEARCH_PRODUCTS_TOOL,
    GET_PRODUCT_TOOL,
    RECOMMEND_ADDONS_TOOL,
    UPSELL_PRODUCT_TOOL,
    CREATE_CART_TOOL,
    ADD_TO_CART_TOOL,
    GET_CART_TOOL,
    APPROVE_CART_TOOL,
    CREATE_ORDER_TOOL
]

MAX_TOOL_ROUNDS = 5
MAX_HISTORY_MESSAGES = 30


def chat(session_id: str, user_message: str):

    history = get_session(session_id)

    if not history:
        history.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

    history.append({
        "role": "user",
        "content": user_message
    })

    # Prevent unbounded conversation history
    if len(history) > MAX_HISTORY_MESSAGES:
        system_message = history[0]

        history = [
            system_message,
            *history[-(MAX_HISTORY_MESSAGES - 1):]
        ]

    for round_number in range(MAX_TOOL_ROUNDS):

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=history,
            tools=tools,
            tool_choice="auto",
            max_tokens=1000,
        )

        message = response.choices[0].message

        # LLM produced final answer
        if not message.tool_calls:

            history.append({
                "role": "assistant",
                "content": message.content
            })

            return message.content

        # Store assistant tool call
        history.append(message)

        print(
            f"Tool round {round_number + 1}:",
            message.tool_calls
        )

        # Execute tools
        for tool_call in message.tool_calls:

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )

                tool_name = tool_call.function.name

                if tool_name == "search_products":

                    result = search_products(
                        **arguments
                    )

                elif tool_name == "get_product":

                    result = get_product(
                        **arguments
                    )

                elif tool_name == "recommend_addons":

                    result = recommend_addons(
                        **arguments
                    )

                elif tool_name == "recommend_upgrade":

                    result = recommend_upgrade(
                        **arguments
                    )

                elif tool_name == "create_cart":

                    result = create_cart()

                elif tool_name == "add_to_cart":

                    result = add_to_cart(
                        **arguments
                    )

                elif tool_name == "get_cart":

                    result = get_cart(
                        **arguments
                    )
                
                elif tool_call.function.name == "approve_purchase":

                    result = approve_purchase(
                        **arguments
                    )
                
                elif tool_call.function.name == "create_order":

                    result = create_order(
                        **arguments
                    )

                else:
                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

            except Exception as e:

                result = {
                    "error": f"Tool execution failed: {str(e)}"
                }
            
            if "error" in result:
                print(result)

            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False,
                    default=json_serializer
                )
            })

    # Agent exceeded tool limit
    history.append({
        "role": "assistant",
        "content": (
            "I wasn't able to complete the request "
            "within the allowed number of steps."
        )
    })

    return (
        "I wasn't able to complete the request "
        "within the allowed number of steps. "
        "Please try simplifying your request."
    )