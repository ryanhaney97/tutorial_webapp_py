#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_pipeline_eb_demo_py.cdk_pipeline_stack import CdkPipelineStack


app = cdk.App()
CdkPipelineStack(app, "EbApplnStack",
                 env=cdk.Environment(account='574036699711', region='us-east-2')
                 )

app.synth()
