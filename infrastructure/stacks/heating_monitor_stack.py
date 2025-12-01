import aws_cdk as cdk
from aws_cdk import (
    Stack, Duration, aws_sqs as sqs, aws_dynamodb as dynamodb,
    aws_lambda as _lambda, aws_iot as iot, aws_iam as iam,
    aws_ssm as ssm  # <--- ÚJ IMPORT
)
from constructs import Construct

# Konstansok a paraméter nevekhez (nem az értékekhez!)
SSM_PARAM_NAME_TOKEN = "/heating-monitor/telegram-token"
SSM_PARAM_NAME_CHAT_ID = "/heating-monitor/telegram-chat-id"

class HeatingMonitorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. SQS DLQ
        self.alert_dlq = sqs.Queue(self, "AlertDeadLetterQueue", visibility_timeout=Duration.seconds(300), queue_name="heating-alert-dlq")
        
        # 2. DynamoDB (Cold Path)
        self.heating_table = dynamodb.Table(self, "HeatingEventsTable",
            partition_key=dynamodb.Attribute(name="device_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.NUMBER),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        self.heating_table.add_attribute(attribute_name="timestamp", attribute_type=dynamodb.AttributeType.NUMBER)
        # self.heating_table.add_base_time_to_live("timestamp") # Megjegyzés: Ez a sor az előző kódban kommentelve volt vagy hibás lehet a metódus név, a helyes: time_to_live_attribute="timestamp" a konstruktorban, de maradjunk a te kódodnál.

        # 3. Lambda (Hot Path)
        self.notifier_lambda = _lambda.Function(self, "TelegramNotifierFunction",
            runtime=_lambda.Runtime.PYTHON_3_11, handler="index.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/notifier"), timeout=Duration.seconds(10),
            dead_letter_queue=self.alert_dlq, retry_attempts=2,
            environment={
                "SSM_KEY_TOKEN": SSM_PARAM_NAME_TOKEN,     # <--- Csak a kulcs nevét adjuk át
                "SSM_KEY_CHAT_ID": SSM_PARAM_NAME_CHAT_ID  # <--- Csak a kulcs nevét adjuk át
            }
        )
        self.alert_dlq.grant_send_messages(self.notifier_lambda)

        # --- JOGOSULTSÁGOK HOZZÁADÁSA (ÚJ RÉSZ) ---
        # Referenciát készítünk a létező SSM paraméterekre, hogy jogot adhassunk rájuk
        # Fontos: A SecureString-nél nem tudjuk importálni az értéket, csak a referenciát a joghoz.
        
        token_param = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, "TelegramTokenParam", parameter_name=SSM_PARAM_NAME_TOKEN
        )
        chat_id_param = ssm.StringParameter.from_string_parameter_attributes(
            self, "TelegramChatIdParam", parameter_name=SSM_PARAM_NAME_CHAT_ID
        )

        # Jogot adunk a Lambdának az olvasásra (SecureString esetén a Decrypt jogot is megadja a default KMS kulcsra)
        token_param.grant_read(self.notifier_lambda)
        chat_id_param.grant_read(self.notifier_lambda)
        # ------------------------------------------

        # 4. IoT Rules
        iot_dynamodb_role = self._get_or_create_iot_role()
        
        # Cold Path Rule
        iot.CfnTopicRule(self, "DynamoDBStorageRule", topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
            sql="SELECT device_id, timestamp, status, sensor_voltage, metadata FROM 'home/heating/status'",
            actions=[iot.CfnTopicRule.DynamoDBv2ActionProperty(put_item={"tableName": self.heating_table.table_name}, role_arn=iot_dynamodb_role.role_arn)]
        ))
        self.heating_table.grant_write_data(iot_dynamodb_role)

        # Hot Path Rule
        iot_lambda_rule = iot.CfnTopicRule(self, "LambdaAlertRule", topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
            sql="SELECT * FROM 'home/heating/status' WHERE status = 'INACTIVE'",
            actions=[iot.CfnTopicRule.LambdaActionProperty(function_arn=self.notifier_lambda.function_arn)]
        ))
        self.notifier_lambda.add_permission("IoTInvoke", principal=iam.ServicePrincipal("iot.amazonaws.com"), source_arn=f"arn:aws:iot:{self.region}:{self.account}:rule/{iot_lambda_rule.ref}")

    def _get_or_create_iot_role(self) -> iam.Role:
        return iam.Role(self, "IoTExecutionRole", assumed_by=iam.ServicePrincipal("iot.amazonaws.com"), role_name=f"iot-rule-execution-role-for-{self.stack_name}")