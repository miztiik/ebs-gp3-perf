#!/usr/bin/env python3

from aws_cdk import core

from ebs_gp3_perf.stacks.back_end.vpc_stack import VpcStack
from ebs_gp3_perf.stacks.back_end.ebs_gp3_perf_stack import EbsGp3PerformanceTestStack


app = core.App()


# VPC Stack for hosting Secure API & Other resources
vpc_stack = VpcStack(
    app,
    f"{app.node.try_get_context('project')}-vpc-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: Custom Multi-AZ VPC"
)


# Deploy R5b EC2 instance with three gp3 and one io1 volumes of size 150GB
ebs_gp3_perf = EbsGp3PerformanceTestStack(
    app,
    f"{app.node.try_get_context('project')}-stack",
    vpc=vpc_stack.vpc,
    ec2_instance_type="r5b.large",
    stack_log_level="INFO",
    description="Miztiik Automation: Deploy R5b EC2 instance with three gp3 and one io1 volumes of size 150GB"
)


# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            core.Tags.of(app).add(k, v, apply_to_launched_instances=True)


app.synth()
