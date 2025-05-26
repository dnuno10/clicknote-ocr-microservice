import os
import resend
from ..core.config import settings

# Configura tu API Key al iniciar
resend.api_key = settings.RESEND_API_KEY

def send_prediction_email(to_email: str, filename: str, prediction: str):

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height:1.6;">
            <h2>Click Note OCR Result</h2>
            <p>The prediction for <strong>{filename}</strong> is:</p>
            <div style="background:#f4f4f4; padding:15px; border-left:4px solid #4CAF50;">
                <pre style="font-size:1.1em; color:#333;">{prediction}</pre>
            </div>
            <p>Best regards,<br>ClickNote OCR System</p>
        </body>
    </html>
    """

    try:
        params = {
            "from": settings.RESEND_SENDER_EMAIL,
            "to": [to_email],
            "subject": "OCR Prediction Result",
            "html": html_body,
        }

        response = resend.Emails.send(params)
        print("[DEBUG] Email sent successfully via Resend:", response)
    except Exception as e:
        print(f"[ERROR] Failed to send email via Resend: {e}")
