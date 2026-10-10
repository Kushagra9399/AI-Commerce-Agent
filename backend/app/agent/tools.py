from app.db.session import db_session
from app.services.product_search_service import ProductSearchService

from app.services.order_service import (
    create_order as create_order_service,
    get_orders as get_orders_service,
    get_order as get_order_service
)

from app.services.audit_service import log_event

from app.db.models import Product
from app.services.cart_service import (
    create_cart as create_cart_service,
    add_product_to_cart,
    get_cart_details,
    approve_cart,
    get_all_carts as get_all_carts_service
)

from app.agent.session import (
    get_session_metadata
)


product_search_service = ProductSearchService()


def search_products(
    query: str,
    max_price: float | None = None,
    min_price: float | None = None,
    brand: str | None = None,
    min_discount: float | None = None,
    top_k: int = 5
):
    results = product_search_service.search(
        query=query,
        top_k=top_k,
        max_price=max_price,
        min_price=min_price,
        brand=brand,
        min_discount=min_discount,
        in_stock_only=True
    )

    return {
        "query": query,
        "filters": {
            "max_price": max_price,
            "min_price": min_price,
            "brand": brand,
            "min_discount": min_discount
        },
        "count": len(results),
        "products": results
    }


def get_product(product_id: str):
    """Fetch a selected Amazon product's full details from SerpAPI."""
    product = product_search_service.get_product(product_id)
    if not product:
        return {"found": False, "product": None, "message": "Product not found."}
    return {"found": True, "product": product}


def recommend_addons(
    product_id: str,
    budget_remaining: float | None = None,
    limit: int = 3
):
    """Find complementary products using the selected product's SerpAPI title."""
    base = product_search_service.get_product(product_id)
    if not base:
        return {
            "product_id": product_id,
            "count": 0,
            "recommendations": [],
            "message": "Could not retrieve the selected product from Amazon."
        }

    query = f"{base.get('name', '')} accessories compatible add-ons"
    products = product_search_service.search(
        query=query,
        top_k=limit,
        max_price=budget_remaining
    )
    products = [p for p in products if p.get("id") != str(product_id)]
    return {
        "product_id": product_id,
        "base_product": base,
        "budget_remaining": budget_remaining,
        "count": len(products),
        "recommendations": [
            {**p, "why": f"Potential complementary item for {base.get('name', 'your selected product')}."}
            for p in products
        ]
    }


def recommend_upgrade(product_id: str):
    """Find a premium alternative using SerpAPI rather than local DB relations."""
    base = product_search_service.get_product(product_id)
    if not base:
        return {
            "found": False,
            "product_id": product_id,
            "message": "Could not retrieve the selected product from Amazon."
        }

    query = f"{base.get('name', '')} better premium upgraded alternative"
    current_price = base.get("sale_price")
    max_price = round(float(current_price) * 1.5, 2) if current_price is not None else None
    candidates = product_search_service.search(
        query=query,
        top_k=5,
        min_price=float(current_price) if current_price is not None else None,
        max_price=max_price
    )
    candidates = [p for p in candidates if p.get("id") != str(product_id)]
    if not candidates:
        return {
            "found": False,
            "product_id": product_id,
            "message": "No suitable upgrade found in SerpAPI results."
        }

    upgrade = candidates[0]
    additional_cost = None
    if current_price is not None and upgrade.get("sale_price") is not None:
        additional_cost = round(float(upgrade["sale_price"]) - float(current_price), 2)
    return {
        "found": True,
        "current_product": base,
        "upgrade": {
            **upgrade,
            "why": "A higher-priced alternative found from the live marketplace search."
        },
        "additional_cost": additional_cost
    }


def create_cart():

    with db_session() as db:

        cart = create_cart_service(db)

        return {
            "cart_id": cart.id,
            "merchant_id": cart.merchant_id,
            "status": cart.status,
            "message": "Cart created successfully."
        }


def add_to_cart(
    cart_id: str,
    product_id: str,
    quantity: int = 1
):

    try:

        with db_session() as db:

            item = add_product_to_cart(
                db=db,
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity
            )

            # Return full cart details, not just the item
            cart_details = get_cart_details(
                db=db,
                cart_id=cart_id
            )

            return {
                "success": True,
                "cart_item_id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "message": "Product added to cart.",
                "cart": cart_details
            }

    except ValueError as e:

        return {
            "success": False,
            "error": str(e)
        }


def get_cart(cart_id: str):

    try:

        with db_session() as db:

            return get_cart_details(
                db=db,
                cart_id=cart_id
            )

    except ValueError as e:

        return {
            "found": False,
            "error": str(e)
        }


def check_cart_and_budget(
    cart_id: str,
    session_id: str | None = None
):
    """
    Check cart details and validate against user's budget.
    
    This is called BEFORE approval to allow explicit buyer confirmation.
    Logs "APPROVAL_REQUESTED" event.
    """

    try:

        with db_session() as db:

            cart_details = get_cart_details(
                db=db,
                cart_id=cart_id
            )

            total = cart_details.get("total", 0)
            
            # Check against user-stated budget if provided
            budget_check = {
                "budget_specified": False,
                "budget_limit": None,
                "within_budget": True,
                "warning": None
            }

            if session_id:
                metadata = get_session_metadata(session_id)
                budget = metadata.get("budget")
                
                if budget is not None:
                    budget_check["budget_specified"] = True
                    budget_check["budget_limit"] = budget
                    
                    if total > budget:
                        budget_check["within_budget"] = False
                        budget_check["warning"] = (
                            f"Cart total (₹{total}) exceeds your stated budget (₹{budget})"
                        )
                    
                    # Log budget check
                    log_event(
                        db=db,
                        action="BUDGET_CHECK",
                        actor="AI_AGENT",
                        order_id=None,
                        details={
                            "cart_id": cart_id,
                            "cart_total": total,
                            "budget_limit": budget,
                            "within_budget": budget_check["within_budget"]
                        }
                    )

                # Log approval request
                log_event(
                    db=db,
                    action="APPROVAL_REQUESTED",
                    actor="AI_AGENT",
                    order_id=None,
                    details={
                        "cart_id": cart_id,
                        "cart_total": total,
                        "item_count": len(cart_details.get("items", []))
                    }
                )

            return {
                "success": True,
                "cart_id": cart_id,
                "total": total,
                "items": cart_details.get("items", []),
                "budget_check": budget_check,
                "message": "Ready for approval. Please confirm to proceed to payment."
            }

    except ValueError as e:

        return {
            "success": False,
            "error": str(e)
        }


def approve_purchase(cart_id: str):

    try:

        with db_session() as db:

            result = approve_cart(
                db=db,
                cart_id=cart_id
            )

            return {
                "success": True,
                **result
            }

    except ValueError as e:

        return {
            "success": False,
            "error": str(e)
        }


def create_order(cart_id: str):

    with db_session() as db:

        try:

            result = create_order_service(
                db=db,
                cart_id=cart_id
            )

            return result

        except ValueError as e:

            return {
                "success": False,
                "error": str(e)
            }

        except Exception as e:

            return {
                "success": False,
                "error": (
                    # "Unable to create payment order."
                    str(e)
                )
            }
        

def get_all_carts():

    with db_session() as db:

        carts = get_all_carts_service(db)

        return {
            "count": len(carts),
            "carts": carts
        }
    

def get_orders(
    status: str | None = None,
    limit: int = 10
):

    with db_session() as db:

        orders = get_orders_service(
            db=db,
            status=status,
            limit=limit
        )

        return {
            "count": len(orders),
            "orders": orders
        }
    

def get_order(order_id: str):

    with db_session() as db:

        order = get_order_service(
            db=db,
            order_id=order_id
        )

        if not order:
            return {
                "found": False,
                "order": None,
                "message": "Order not found."
            }

        return {
            "found": True,
            "order": order
        }