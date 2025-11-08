from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
from database import create_document
from schemas import Order as OrderSchema

load_dotenv()

app = FastAPI(title="Riserva Rotundo API")

# CORS (allow all during development; can be restricted by env later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderRequest(OrderSchema):
    pass


class OrderResponse(BaseModel):
    id: str
    message: str


def send_order_email(order: OrderSchema, inserted_id: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else 587
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("ORDER_NOTIFICATION_EMAIL") or os.getenv("SMTP_USER")

    if not smtp_host or not to_email:
        # No SMTP configured; skip silently
        return

    liters = order.quantity * 5  # each can is 5L

    subject = f"Nuovo ordine #{inserted_id[:6]} — {order.product_name} x{order.quantity}"
    body = (
        f"Nuovo ordine ricevuto\n\n"
        f"ID: {inserted_id}\n"
        f"Prodotto: {order.product_name}\n"
        f"Quantità: {order.quantity} lattine (totale {liters} L)\n"
        f"Totale: €{order.total_price:.2f}\n\n"
        f"Cliente: {order.full_name}\n"
        f"Email: {order.email}\n"
        f"Telefono: {order.phone}\n\n"
        f"Indirizzo:\n{order.address_line}\n{order.postal_code} {order.city} ({order.province or ''})\n\n"
        f"Note: {order.notes or '-'}\n"
        f"Newsletter opt-in: {'sì' if order.newsletter_opt_in else 'no'}\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user or to_email
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        # Log-only failure; do not block API
        print(f"SMTP send failed: {e}")


@app.get("/test")
async def test():
    return {"status": "ok"}


@app.post("/api/orders", response_model=OrderResponse)
async def create_order(order: OrderRequest):
    try:
        order_id = create_document("order", order)
        send_order_email(order, order_id)
        return OrderResponse(id=order_id, message="Order received")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
