import secrets
import string


def generate_secure_password(length: int = 16) -> str:
    """Generate secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def sanitize_resource_name(name: str) -> str:
    """Sanitize name for AWS resource naming"""
    return name.lower().replace('_', '-').replace(' ', '-')[:63]


def get_default_tags(project_id: str) -> list:
    """Get default AWS resource tags"""
    return [
        {'Key': 'Project', 'Value': project_id},
        {'Key': 'ManagedBy', 'Value': 'ShipDB'},
        {'Key': 'Environment', 'Value': 'hackathon'}
    ]
