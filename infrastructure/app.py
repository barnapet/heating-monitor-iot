#!/usr/bin/env python3
import os
import aws_cdk as cdk

from stacks.heating_monitor_stack import HeatingMonitorStack

app = cdk.App()

HeatingMonitorStack(app, "HeatingMonitorStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()