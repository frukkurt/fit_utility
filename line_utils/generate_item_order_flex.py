
from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float


class OrderFlexRequest(BaseModel):
    items: List[OrderItem] = [{
      "name": "ไก่",
      "quantity": 5,
      "price": 100
    },{
      "name": "หมู",
      "quantity": 5,
      "price": 100
    },
    ]
    total_items: int = 10
    total_price: float =1000.000
    transport_price: float = 50.00
    sum_total: float = 1050.00
    order_id: str  = "#260425&ght2&121110"
    address: str = "1234 home"
    store_name: str = "Well daily"
    store_address: str = "Marigold Lanna | Chiang Mai"
    button_url: str = "https://www.google.com/"
    button_label: str = "Transfer slip"


def generate_order_flex(
    items: list[dict],
    total_items: int | str,
    total_price: float | str,
    transport_price: float | str,
    sum_total: float | str,
    order_id: str,
    address: str = "-",
    store_name: str = "Well daily",
    store_address: str = "Marigold Lanna | Chiang Mai",
    button_url: str = "http://linecorp.com/",
    button_label: str = "Transfer slip",
) -> dict:

    def money_fmt(value) -> str:
        if isinstance(value, str):
            return value if "฿" in value else f"{value}฿"
        value = float(value)
        return f"{int(value)}฿" if value.is_integer() else f"{value:.2f}฿"

    item_contents = []

    for item in items:
        item_contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": str(item["name"]),
                    "size": "sm",
                    "color": "#555555",
                    "wrap": True,
                    "flex": 3,
                },
                {
                    "type": "text",
                    "text": money_fmt(item["price"]),
                    "size": "sm",
                    "color": "#111111",
                    "align": "end",
                    "flex": 1,
                },
                {
                    "type": "text",
                    "text": f'x{item["quantity"]}',
                    "size": "sm",
                    "color": "#111111",
                    "align": "end",
                    "flex": 1,
                },
            ],
            "margin": "sm",
        })

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "Invoice", "weight": "bold", "color": "#1DB446", "size": "sm"},
                {"type": "text", "text": store_name, "weight": "bold", "size": "xxl", "margin": "md"},
                {"type": "text", "text": store_address, "size": "xs", "color": "#aaaaaa", "wrap": True},
                {"type": "separator", "margin": "xl"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "menu", "flex": 3, "weight": "bold"},
                        {"type": "text", "text": "price", "align": "end", "margin": "xxl", "flex": 1, "weight": "bold"},
                        {"type": "text", "text": "qty", "align": "end", "flex": 1, "weight": "bold"},
                    ],
                },
                {"type": "separator", "margin": "none"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "xxl",
                    "spacing": "sm",
                    "contents": item_contents + [
                        {"type": "separator", "margin": "xxl"},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "xxl",
                            "contents": [
                                {"type": "text", "text": "Items", "size": "sm", "color": "#555555"},
                                {"type": "text", "text": str(total_items), "size": "sm", "color": "#111111", "align": "end"},
                            ],
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "Total", "size": "sm", "color": "#555555"},
                                {"type": "text", "text": money_fmt(total_price), "size": "sm", "color": "#111111", "align": "end"},
                            ],
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "Transport", "size": "sm", "color": "#555555"},
                                {"type": "text", "text": money_fmt(transport_price), "size": "sm", "color": "#111111", "align": "end"},
                            ],
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "Sum Total", "size": "sm", "color": "#555555"},
                                {"type": "text", "text": money_fmt(sum_total), "size": "sm", "color": "#111111", "align": "end"},
                            ],
                        },
                    ],
                },
                {"type": "separator", "margin": "xxl"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "Address", "size": "sm", "weight": "bold"},
                        {"type": "text", "text": address, "size": "xs", "margin": "xs", "wrap": True},
                    ],
                },
                {"type": "separator", "margin": "xxl"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                        {"type": "text", "text": "ORDER ID", "size": "xs", "color": "#aaaaaa", "flex": 0},
                        {
                            "type": "text",
                            "text": order_id,
                            "color": "#aaaaaa",
                            "size": "xs",
                            "align": "end",
                            "wrap": False,
                            "position": "relative",
                        },
                    ],
                },
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": button_label,
                        "uri": button_url,
                    },
                },
            ],
        },
        "styles": {"footer": {"separator": True}},
    }
