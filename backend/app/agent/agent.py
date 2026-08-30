import os
import json
import time
from uuid import UUID
from decimal import Decimal
from datetime import date, datetime

from groq import Groq, RateLimitError

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
    create_order,
    get_all_carts,
    get_orders,
    get_order
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

GET_ALL_CARTS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_all_carts",
        "description": (
            "Retrieve the buyer's carts. "
            "Use this when the buyer asks to see "
            "their carts or wants information about "
            "previous or active carts."
        ),
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}

GET_ORDERS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_orders",
        "description": (
            "Retrieve the buyer's orders. "
            "Use this when the buyer asks about "
            "previous orders, order history, or "
            "the status of an order."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": (
                        "Optional order status filter, "
                        "such as pending_payment, paid, "
                        "completed, failed, or cancelled."
                    )
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of orders.",
                    "default": 10
                }
            }
        }
    }
}

GET_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_order",
        "description": (
            "Retrieve complete information about a specific "
            "order using its order ID. "
            "Use this whenever the buyer asks about a specific "
            "order, its status, products, amount, or payment state. "
            "Do not create a new order when an existing order "
            "may already exist. Check the existing order first."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Unique order ID."
                }
            },
            "required": ["order_id"]
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
    GET_ALL_CARTS_TOOL,
    APPROVE_CART_TOOL,
    CREATE_ORDER_TOOL,
    GET_ORDER_TOOL,
    GET_ORDERS_TOOL
]

MAX_TOOL_ROUNDS = 5
MAX_HISTORY_MESSAGES = 30

def call_llm(messages, tools):

    for attempt in range(3):

        try:
            return client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1000,
            )

        except RateLimitError as e:

            if attempt == 2:
                raise

            print(
                f"Groq rate limit hit. "
                f"Retrying in 5 seconds... "
                f"(attempt {attempt + 1}/3)"
            )

            time.sleep(5)


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

        response = call_llm(
            messages=history,
            tools=tools
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
                
                elif tool_name == "approve_purchase":

                    result = approve_purchase(
                        **arguments
                    )
                
                elif tool_name == "create_order":

                    result = create_order(
                        **arguments
                    )
                
                elif tool_name == "get_all_carts":

                    result = get_all_carts()

                elif tool_name == "get_orders":

                    result = get_orders(
                        **arguments
                    )
                
                elif tool_name == "get_order":

                    result = get_order(
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

            # If the tool created an order with payment details, return a structured
            # assistant response immediately so the frontend can render a Pay button
            # and initiate the Razorpay checkout flow.
            try:
                if tool_call.function.name == "create_order":
                    # result is expected to include keys: success, order, payment
                    if result and isinstance(result, dict) and result.get("success"):
                        order_obj = result.get("order") or {}
                        payment_obj = result.get("payment") or {}

                        # Ensure payment payload includes the internal order id
                        try:
                            payment_obj["order_id"] = payment_obj.get("order_id") or order_obj.get("id")
                        except Exception:
                            pass

                        assistant_payload = {
                            "message": (
                                f"Created order {order_obj.get('id')} for payment. "
                                "Click the Pay button to continue."
                            ),
                            "order": order_obj,
                            "payment": payment_obj
                        }

                        history.append({
                            "role": "assistant",
                            "content": json.dumps(
                                assistant_payload,
                                ensure_ascii=False,
                                default=json_serializer
                            )
                        })

                        return assistant_payload
            except Exception:
                # swallow and continue agent loop if anything unexpected occurs
                pass

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