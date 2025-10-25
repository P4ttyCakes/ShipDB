class DeploymentError(Exception):
    """Base deployment exception"""
    pass


class CredentialsError(DeploymentError):
    """Invalid credentials"""
    pass


class ResourceLimitError(DeploymentError):
    """AWS resource limit reached"""
    pass


class TimeoutError(DeploymentError):
    """Deployment timeout"""
    pass
