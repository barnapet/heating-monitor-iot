import aws_cdk as cdk
from aws_cdk import (
    Stack, Duration, aws_sqs as sqs, aws_dynamodb as dynamodb,
    aws_lambda as _lambda, aws_iot as iot, aws_iam as iam,
    aws_ssm as ssm
)
from constructs import Construct

# Constants for Parameter Store keys (names only, NOT values!)
SSM_PARAM_NAME_TOKEN = "/heating-monitor/telegram-token"
SSM_PARAM_NAME_CHAT_ID = "/heating-monitor/telegram-chat-id"

class HeatingMonitorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. SQS Dead Letter Queue (DLQ) for handling failures
        self.alert_dlq = sqs.Queue(self, "AlertDeadLetterQueue", 
            visibility_timeout=Duration.seconds(300), 
            queue_name="heating-alert-dlq"
        )
        
        # 2. DynamoDB Table (Cold Path - Data Storage)
        self.heating_table = dynamodb.Table(self, "HeatingEventsTable",
            partition_key=dynamodb.Attribute(name="device_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.NUMBER),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # 3. Lambda Function (Hot Path - Alerting)
        self.notifier_lambda = _lambda.Function(self, "TelegramNotifierFunction",
            runtime=_lambda.Runtime.PYTHON_3_11, 
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/notifier"), 
            timeout=Duration.seconds(10),
            dead_letter_queue=self.alert_dlq, 
            retry_attempts=2,
            environment={
                "SSM_KEY_TOKEN": SSM_PARAM_NAME_TOKEN,     # Passing the parameter NAME, not value
                "SSM_KEY_CHAT_ID": SSM_PARAM_NAME_CHAT_ID  # Passing the parameter NAME, not value
            }
        )
        self.alert_dlq.grant_send_messages(self.notifier_lambda)

        # --- PERMISSIONS FOR SYSTEMS MANAGER (SSM) ---
        # Create references to the existing SSM parameters to grant permissions
        # Note: For SecureString, we cannot import the value here, only the reference.
        
        token_param = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, "TelegramTokenParam", parameter_name=SSM_PARAM_NAME_TOKEN
        )
        chat_id_param = ssm.StringParameter.from_string_parameter_attributes(
            self, "TelegramChatIdParam", parameter_name=SSM_PARAM_NAME_CHAT_ID
        )

        # Grant read permissions to the Lambda function
        # (For SecureString, grant_read also provides KMS Decrypt permissions)
        token_param.grant_read(self.notifier_lambda)
        chat_id_param.grant_read(self.notifier_lambda)
        # ---------------------------------------------

        # 4. IoT Rules
        iot_dynamodb_role = self._get_or_create_iot_role()
        
        # Cold Path Rule: Store all data in DynamoDB
        iot.CfnTopicRule(self, "DynamoDBStorageRule", topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
            sql="SELECT device_id, timestamp, status, sensor_voltage, metadata FROM 'home/heating/status'",
            actions=[iot.CfnTopicRule.DynamoDBv2ActionProperty(
                put_item={"tableName": self.heating_table.table_name}, 
                role_arn=iot_dynamodb_role.role_arn
            )]
        ))
        self.heating_table.grant_write_data(iot_dynamodb_role)

        # Hot Path Rule: Trigger Lambda if status is 'INACTIVE'
        iot_lambda_rule = iot.CfnTopicRule(self, "LambdaAlertRule", topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
            sql="SELECT * FROM 'home/heating/status' WHERE status = 'INACTIVE'",
            actions=[iot.CfnTopicRule.LambdaActionProperty(function_arn=self.notifier_lambda.function_arn)]
        ))
        
        # Grant IoT permission to invoke the Lambda function
        self.notifier_lambda.add_permission("IoTInvoke", 
            principal=iam.ServicePrincipal("iot.amazonaws.com"), 
            source_arn=f"arn:aws:iot:{self.region}:{self.account}:rule/{iot_lambda_rule.ref}"
        )

    def _get_or_create_iot_role(self) -> iam.Role:
        """Helper to create or get the IAM Role for IoT actions"""
        return iam.Role(self, "IoTExecutionRole", 
            assumed_by=iam.ServicePrincipal("iot.amazonaws.com"), 
            role_name=f"iot-rule-execution-role-for-{self.stack_name}"
        )