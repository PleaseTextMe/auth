from prometheus_client import Counter

# Business metrics for Auth service
AUTH_LOGIN_ATTEMPTS = Counter(
    "auth_login_attempts_total",
    "Total number of login attempts",
    ["status"]  # "success" or "failed"
)

AUTH_REGISTRATIONS = Counter(
    "auth_registrations_total",
    "Total number of user registrations",
    ["status"]  # "success" or "failed"
)

AUTH_EMAIL_VERIFICATIONS = Counter(
    "auth_email_verifications_total",
    "Total number of email verification attempts",
    ["status"]  # "success" or "failed"
)

AUTH_CODES_GENERATED = Counter(
    "auth_verification_codes_generated_total",
    "Total number of email verification codes generated"
)
