#!/usr/bin/env python3

from aws_cdk import core

from ebs_gp3_perf.ebs_gp3_perf_stack import EbsGp3PerfStack


app = core.App()
EbsGp3PerfStack(app, "ebs-gp3-perf")

app.synth()
