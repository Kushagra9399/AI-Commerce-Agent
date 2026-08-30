import uuid

from app.db.session import db_session
from app.services.recommendation_service import (
    RecommendationService
)
from app.services.product_search_service import ProductSearchService

from app.services.order_service import create_order as create_order_service

from app.services.upsell_service import UpsellService

from app.db.models import Cart
from app.services.cart_service import (
    create_cart as create_cart_service,
    add_product_to_cart,
    get_cart_details,
    approve_cart
)


product_search_service = ProductSearchService()
recommendation_service = RecommendationService()
upsell_service = UpsellService()


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
    """
    Retrieve the complete information for one product.

    This is used after the user selects a product.
    """

    for product in product_search_service.metadata:

        if product["product_id"] == product_id:

            return {
                "found": True,
                "product": product
            }

    return {
        "found": False,
        "product": None
    }


def recommend_addons(
    product_id: str,
    budget_remaining: float | None = None,
    limit: int = 3
):

    with db_session() as db:

        products = (
            recommendation_service
            .get_cross_sell_products(
                db=db,
                product_id=product_id,
                budget_remaining=budget_remaining,
                limit=limit
            )
        )

        return {
            "product_id": product_id,
            "budget_remaining": budget_remaining,
            "count": len(products),
            "recommendations": [
                {
                    "product_id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "sale_price": float(
                        product.sale_price
                    ),
                    "discount_percent": float(
                        product.discount_percent
                    ),
                    "stock": product.stock
                }
                for product in products
            ]
        }


def recommend_upgrade(
    product_id: str
):
    """
    Find a suitable higher-value product upgrade.

    Used by the AI agent after a product has been selected.
    """

    with db_session() as db:

        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {
                "found": False,
                "message": "Product not found."
            }

        upgrade = upsell_service.find_upgrade(
            db=db,
            product=product
        )

        if not upgrade:
            return {
                "found": False,
                "product_id": product_id,
                "message": "No suitable upgrade found."
            }

        additional_cost = (
            float(upgrade.sale_price)
            - float(product.sale_price)
        )

        return {
            "found": True,

            "current_product": {
                "product_id": product.id,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "sale_price": float(
                    product.sale_price
                )
            },

            "upgrade": {
                "product_id": upgrade.id,
                "name": upgrade.name,
                "brand": upgrade.brand,
                "category": upgrade.category,
                "sale_price": float(
                    upgrade.sale_price
                ),
                "discount_percent": float(
                    upgrade.discount_percent
                ),
                "stock": upgrade.stock
            },

            "additional_cost": round(
                additional_cost,
                2
            )
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

            return {
                "success": True,
                "cart_item_id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "message": (
                    "Product added to cart."
                )
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