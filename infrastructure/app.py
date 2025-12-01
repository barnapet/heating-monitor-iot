#!/usr/bin/env python3
import os
import aws_cdk as cdk

# Import the stack from the new location and file name
from stacks.heating_monitor_stack import HeatingMonitorStack

app = cdk.App()

# Instantiate the HeatingMonitorStack
HeatingMonitorStack(app, "HeatingMonitorStack",
    # Set the environment to the current account and region configured in the AWS CLI.
    # This is necessary for lookups (like IoT endpoints) and ensures the stack 
    # deploys to the correct location.
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()