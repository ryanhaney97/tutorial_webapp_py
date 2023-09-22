from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from aws_cdk import Stack, SecretValue, Stage
from cdk_pipeline_eb_demo_py.eb_appln_stack import EbApplnStack

class CdkEBStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        service = EbApplnStack(self, "WebService",
                               min_size="1",
                               max_size="2",
                               **kwargs)

class CdkPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        pipeline = CodePipeline(self, "Pipeline",
                                pipeline_name="MyServicePipeline",
                                synth=ShellStep("Synth",
                                                input=CodePipelineSource.git_hub("yoshiquest/tutorial_webapp_py",
                                                                                 "master",
                                                                                 authentication=SecretValue.secrets_manager(
                                                                                     "github-oauth-token"
                                                                                 )),
                                                install_commands=["pip install -r requirements.txt",
                                                                  "npm install -g aws_cdk"],
                                                commands=["cdk synth"]
                                                )
                                )
        deploy = CdkEBStage(self, "Pre-Prod")
        deploy_stage = pipeline.add_stage(deploy)