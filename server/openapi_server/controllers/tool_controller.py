from openapi_server.models.tool import Tool  # noqa: E501
from openapi_server.models.tool_dependencies import ToolDependencies  # noqa: E501
from openapi_server.models.tool_type import ToolType  # noqa: E501
from openapi_server.models.license import License
from openapi_server.config import config


def get_tool():  # noqa: E501
    """Get tool information

    Get information about the tool # noqa: E501


    :rtype: Tool
    """
    tool = Tool(
        name=f"phi-annotator-spark-nlp-{config.config_name}",
        version="0.2.2",
        license=License.NONE,  # Spark NLP for Healthcare requires a license
        repository="github:nlpsandbox/phi-annotator-spark-nlp",
        description="Spark NLP-based PHI annotator (NER model: " +
                f"{config.ner_model}, embeddings model: {config.embeddings_model})",  # noqa: E501
        author="NLP Sandbox Team",
        author_email="team@nlpsandbox.io",
        url="https://github.com/nlpsandbox/phi-annotator-spark-nlp",
        type=ToolType.PHI_ANNOTATOR,
        api_version="1.2.0"
    )
    return tool, 200


def get_tool_dependencies():  # noqa: E501
    """Get tool dependencies

    Get the dependencies of this tool # noqa: E501


    :rtype: ToolDependencies
    """
    return ToolDependencies(tools=[]), 200
