"""
core/email.py — Email sending utility via Resend API
"""
import httpx
from backend.core.config import settings
from backend.core.logger import logger


async def send_password_reset_email(to_email: str, reset_url: str, full_name: str = "") -> bool:
    """
    Send a password reset email via Resend API.
    Returns True on success, False on failure.
    """
    if not settings.RESEND_API_KEY:
        logger.error("RESEND_API_KEY not configured — cannot send reset email")
        return False

    name_display = full_name.split()[0] if full_name else "there"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#16161f;border:1px solid rgba(139,92,246,0.2);
                      border-radius:20px;overflow:hidden;max-width:560px;width:100%">

          <!-- Header -->
          <tr>
            <td style="padding:32px 40px 24px;border-bottom:1px solid rgba(139,92,246,0.15);">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#7c3aed,#a855f7,#ec4899);
                             border-radius:10px;width:40px;height:40px;text-align:center;
                             vertical-align:middle;font-size:20px;">
                    🧠
                  </td>
                  <td style="padding-left:12px;font-size:1.1rem;font-weight:700;
                             color:#f1f0ff;letter-spacing:-0.02em;">
                    AI Document Classifier
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px 40px;">
              <h1 style="margin:0 0 8px;font-size:1.5rem;font-weight:700;color:#f1f0ff;
                         letter-spacing:-0.02em;">
                Reset your password
              </h1>
              <p style="margin:0 0 24px;color:#a09cb8;font-size:0.95rem;line-height:1.6;">
                Hi {name_display}, we received a request to reset the password
                for your account.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                <tr>
                  <td style="background:linear-gradient(135deg,#7c3aed,#a855f7,#ec4899);
                             border-radius:10px;">
                    <a href="{reset_url}"
                       style="display:inline-block;padding:14px 32px;color:#fff;
                              font-size:0.95rem;font-weight:600;text-decoration:none;
                              letter-spacing:0.01em;">
                      Reset Password →
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Warning -->
              <table cellpadding="0" cellspacing="0" width="100%"
                     style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                            border-radius:10px;margin-bottom:24px;">
                <tr>
                  <td style="padding:14px 18px;color:#fcd34d;font-size:0.85rem;line-height:1.6;">
                    ⏱️ <strong>This link expires in 15 minutes.</strong>
                    After that you will need to request a new reset link.
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;color:#a09cb8;font-size:0.85rem;line-height:1.6;">
                If you didn't request a password reset, you can safely ignore this email.
                Your password will not be changed.
              </p>

              <!-- URL fallback -->
              <p style="margin:16px 0 0;color:#6b6880;font-size:0.78rem;">
                If the button doesn't work, copy and paste this link into your browser:
              </p>
              <p style="margin:4px 0 0;color:#8b5cf6;font-size:0.78rem;word-break:break-all;">
                {reset_url}
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:1px solid rgba(139,92,246,0.1);">
              <p style="margin:0;color:#6b6880;font-size:0.78rem;text-align:center;">
                AI Document Classifier · Sent to {to_email}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    plain_text = f"""
Reset your password — AI Document Classifier

Hi {name_display},

We received a request to reset the password for your account.

Reset your password here: {reset_url}

This link expires in 15 minutes.

If you didn't request this, you can safely ignore this email.

— AI Document Classifier
"""

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type":  "application/json",
                },
                json={
                    "from":    settings.EMAIL_FROM,
                    "to":      [to_email],
                    "subject": "Reset your password — AI Document Classifier",
                    "html":    html_body,
                    "text":    plain_text,
                },
            )
            if response.status_code in (200, 201):
                logger.info(f"Password reset email sent to {to_email}")
                return True
            else:
                logger.error(f"Resend error {response.status_code}: {response.text}")
                return False

    except Exception as e:
        logger.error(f"Failed to send reset email to {to_email}: {e}")
        return False
