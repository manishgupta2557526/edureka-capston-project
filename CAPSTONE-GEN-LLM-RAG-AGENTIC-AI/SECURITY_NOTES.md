# Security notes for production deployment

- Replace the default login credentials in the auth layer.
- Store secrets in environment variables or AWS Systems Manager Parameter Store.
- Use HTTPS with Let’s Encrypt or AWS ACM.
- Restrict EC2 security group access to required ports only.
- Consider encrypted backups and controlled access for the Chroma persistence directory in production.
