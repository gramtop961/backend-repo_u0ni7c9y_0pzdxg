import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
import smtplib

from schemas import Order
from database import create_document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/orders")
def create_order(order: Order):
    # Save order to database
    try:
        order_id = create_document("order", order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Try sending a notification email
    try:
        recipient = os.getenv("ORDER_NOTIFICATION_EMAIL", "andrearotundo3@gmail.com")
        subject = f"Nuovo ordine #{order_id} — {order.product_name} x{order.quantity}"
        body = (
            f"Nuovo ordine ricevuto\n\n"
            f"Prodotto: {order.product_name}\n"
            f"Quantità: {order.quantity}\n"
            f"Totale: €{order.total_price:.2f}\n\n"
            f"Cliente: {order.full_name}\n"
            f"Email: {order.email}\n"
            f"Telefono/WhatsApp: {order.phone}\n\n"
            f"Indirizzo:\n{order.address_line}\n{order.postal_code} {order.city} ({order.province or ''})\n\n"
            f"Note: {order.notes or '-'}\n"
            f"Newsletter: {'Sì' if order.newsletter_opt_in else 'No'}\n"
        )

        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        smtp_from = os.getenv("SMTP_FROM", smtp_user or recipient)

        if smtp_host and smtp_user and smtp_pass:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = recipient
            msg.set_content(body)

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            print("[Order Email Log] SMTP not configured. Printing email to console.")
            print("To:", recipient)
            print(subject)
            print(body)
    except Exception as e:
        print("[Email Error]", str(e))

    return {"status": "ok", "id": order_id}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
