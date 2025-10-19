# Guide: Configuring AWS Secrets Manager

## 📋 Overview

This project uses **AWS Secrets Manager** in production for secure secret management, and `.env` files for local development.

---

## 🏠 Local Development (using .env)

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   ENVIRONMENT=development
   AWS_REGION=us-east-1
   
   # DynamoDB Tables
   DYNAMO_CHATS_TABLE_NAME=deep-market-analyzer-chats
   DYNAMO_USERS_TABLE_NAME=deep-market-analyzer-users
   DYNAMO_USERNAMES_TABLE_NAME=deep-market-analyzer-usernames
   DYNAMO_MESSAGES_TABLE_NAME=deep-market-analyzer-messages
   DYNAMO_DOCUMENTS_TABLE_NAME=deep-market-analyzer-documents
   DYNAMO_IMAGES_TABLE_NAME=deep-market-analyzer-images
   
   # Bedrock Agent Core
   MEMORY_ID_BEDROCK_AGENT_CORE=your-memory-id
   ARN_BEDROCK_AGENTCORE=arn:aws:bedrock:us-east-1:account-id:agent-alias/agent-id/alias-id
   
   # S3 Storage
   S3_BUCKET_NAME=your-bucket-name
   ```

3. The application will automatically load from `.env`

---

## ☁️ Production (using AWS Secrets Manager)

### Step 1: Create the Secret in AWS

**Option A: Using AWS Console**

1. Go to AWS Secrets Manager in the console
2. Click "Store a new secret"
3. Select "Other type of secret"
4. In "Key/value pairs", add your secrets in JSON or key-value format:
   ```json
   {
     "AWS_REGION": "us-east-1",
     "DYNAMO_CHATS_TABLE_NAME": "prod-chats-table",
     "DYNAMO_USERS_TABLE_NAME": "prod-users-table",
     "DYNAMO_USERNAMES_TABLE_NAME": "prod-usernames-table",
     "DYNAMO_MESSAGES_TABLE_NAME": "prod-messages-table",
     "DYNAMO_DOCUMENTS_TABLE_NAME": "prod-documents-table",
     "DYNAMO_IMAGES_TABLE_NAME": "prod-images-table",
     "MEMORY_ID_BEDROCK_AGENT_CORE": "your-memory-id",
     "ARN_BEDROCK_AGENTCORE": "arn:aws:bedrock:us-east-1:account-id:agent-alias/agent-id/alias-id",
     "S3_BUCKET_NAME": "your-production-bucket"
   }
   ```
5. Secret name: `hackaton-api-secrets` (or as defined in AWS_SECRET_NAME)
6. Configure rotation (optional)
7. Save the secret

**Option B: Using AWS CLI**

```bash
aws secretsmanager create-secret \
    --name hackaton-api-secrets \
    --description "Secrets for Deep Market Analyzer API" \
    --secret-string '{
      "AWS_REGION": "us-east-1",
      "DYNAMO_CHATS_TABLE_NAME": "prod-chats-table",
      "DYNAMO_USERS_TABLE_NAME": "prod-users-table",
      "DYNAMO_USERNAMES_TABLE_NAME": "prod-usernames-table",
      "DYNAMO_MESSAGES_TABLE_NAME": "prod-messages-table",
      "DYNAMO_DOCUMENTS_TABLE_NAME": "prod-documents-table",
      "DYNAMO_IMAGES_TABLE_NAME": "prod-images-table",
      "MEMORY_ID_BEDROCK_AGENT_CORE": "your-memory-id",
      "ARN_BEDROCK_AGENTCORE": "arn:aws:bedrock:us-east-1:account-id:agent-alias/agent-id/alias-id",
      "S3_BUCKET_NAME": "your-production-bucket"
    }' \
    --region us-east-1
```

### Step 2: Configure IAM Permissions

Your Lambda or EC2 instance needs permissions to read the secret:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:hackaton-api-secrets-*"
    }
  ]
}
```

### Step 3: Configure Environment Variables in Lambda/EC2

You only need these two environment variables:

```bash
ENVIRONMENT=production
AWS_SECRET_NAME=hackaton-api-secrets
```

The application will automatically:
- Detect it's in production
- Connect to Secrets Manager
- Load all secrets from the JSON

---

## 🔄 Updating Secrets in Production

**Using AWS Console:**
1. Go to Secrets Manager
2. Select your secret
3. Click "Retrieve secret value"
4. Click "Edit"
5. Modify the values
6. Save

**Using AWS CLI:**
```bash
aws secretsmanager update-secret \
    --secret-id hackaton-api-secrets \
    --secret-string '{
      "AWS_REGION": "us-east-1",
      "DYNAMO_CHATS_TABLE_NAME": "new-value",
      ...
    }'
```

**Restart your application** to load the new values.

---

## 🔐 Best Practices

✅ **DO:**
- Use Secrets Manager for production
- Use `.env` only for local development
- Add `.env` to `.gitignore`
- Use IAM roles with minimum necessary permissions
- Enable automatic secret rotation when possible
- Use different secrets for dev/staging/prod

❌ **DON'T:**
- Commit `.env` files to the repository
- Hardcode secrets in code
- Use the same secret across multiple environments
- Give excessive IAM permissions

---

## 🧪 Testing Locally with Secrets Manager

If you want to test loading from Secrets Manager locally:

1. Configure AWS CLI with valid credentials:
   ```bash
   aws configure
   ```

2. Update your `.env`:
   ```bash
   ENVIRONMENT=production
   AWS_SECRET_NAME=hackaton-api-secrets
   ```

3. Run the application - it will load from Secrets Manager

---

## 📝 Adding New Secrets

1. Add the field in `config.py` within `_load_from_secrets_manager()` and `_load_from_env()`:
   ```python
   # In _load_from_secrets_manager
   self.NEW_SECRET = secret.get('NEW_SECRET')
   
   # In _load_from_env
   self.NEW_SECRET = os.getenv('NEW_SECRET')
   ```

2. Update `.env.example`:
   ```bash
   NEW_SECRET=example-value
   ```

3. Update the secret in AWS Secrets Manager with the new field

---

## 🆘 Troubleshooting

**Error: "Secret not found"**
- Verify the secret name is correct
- Verify you're in the correct region
- Check IAM permissions

**Error: "Access Denied"**
- Review IAM permissions for your Lambda/EC2
- Ensure you have `secretsmanager:GetSecretValue`

**Application doesn't load secrets**
- Verify `ENVIRONMENT=production`
- Check application logs
- Verify network connection to AWS

---

## 📚 References

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Boto3 Secrets Manager](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)

---

**Developed for AWS Hackathon 2025** 🚀
