import aws_cdk as core
import aws_cdk.assertions as assertions
from infrastructure.stacks.heating_monitor_stack import HeatingMonitorStack

# Helper function to instantiate the stack and return its synthesized template
def get_template():
    app = core.App()
    stack = HeatingMonitorStack(app, "HeatingMonitorStack")
    return assertions.Template.from_stack(stack)


def test_dynamodb_table_created_with_correct_schema():
    """
    Data Contract Test:
    Ensures that the DynamoDB table is created with the correct key schema.
    Any change here could break backward compatibility for stored data.
    """
    template = get_template()

    # 1. Check: Exactly one DynamoDB table should exist
    template.resource_count_is("AWS::DynamoDB::Table", 1)

    # 2. Check: Partition key and sort key must match the defined data contract
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "KeySchema": [
            {
                "AttributeName": "device_id",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "timestamp",
                "KeyType": "RANGE"
            }
        ],
        "BillingMode": "PAY_PER_REQUEST"
    })


def test_dynamodb_ttl_enabled():
    """
    Lifecycle Test:
    Ensures that TTL (Time To Live) is enabled on the 'ttl' attribute.
    This is important for cost optimization and long‑term data lifecycle management.
    """
    template = get_template()

    template.has_resource_properties("AWS::DynamoDB::Table", {
        "TimeToLiveSpecification": {
            "AttributeName": "ttl",
            "Enabled": True
        }
    })


def test_lambda_function_properties():
    """
    Compute Test:
    Validates core Lambda configuration such as runtime, timeout, and environment variables.
    These values are critical for correct execution and integration with SSM parameters.
    """
    template = get_template()

    template.has_resource_properties("AWS::Lambda::Function", {
        "Runtime": "python3.11",
        "Timeout": 10,
        "Environment": {
            "Variables": {
                "SSM_KEY_TOKEN": "/heating-monitor/telegram-token",
                "SSM_KEY_CHAT_ID": "/heating-monitor/telegram-chat-id"
            }
        }
    })


def test_iot_rules_created():
    """
    Integration Test:
    Ensures that the required IoT Topic Rules are created.
    The system uses two rules: one for DynamoDB ingestion and one for alerting.
    """
    template = get_template()

    # Two IoT rules must exist (one for DynamoDB writes, one for alert notifications)
    template.resource_count_is("AWS::IoT::TopicRule", 2)
