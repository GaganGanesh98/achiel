def reset_password(name: str, reset_url: str) -> tuple[str, str, str]:
    subject = "Reset your CampusVoice password"
    text = (
        f"Hi {name},\n\n"
        f"Use this link to reset your password (expires in 15 minutes):\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email.\n"
    )
    html = f"""<!DOCTYPE html>
<html><body>
<p>Hi {name},</p>
<p><a href="{reset_url}">Reset your password</a> (expires in 15 minutes).</p>
<p>If you did not request this, you can ignore this email.</p>
</body></html>"""
    return subject, html, text


def verify_email(name: str, verify_url: str) -> tuple[str, str, str]:
    subject = "Confirm your CampusVoice email"
    text = (
        f"Hi {name},\n\n"
        f"Confirm your email address:\n{verify_url}\n\n"
        "This link expires in 24 hours.\n"
    )
    html = f"""<!DOCTYPE html>
<html><body>
<p>Hi {name},</p>
<p><a href="{verify_url}">Confirm your email address</a> (expires in 24 hours).</p>
</body></html>"""
    return subject, html, text
