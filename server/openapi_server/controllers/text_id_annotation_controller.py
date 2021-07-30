import connexion
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_id_annotation_request import TextIdAnnotationRequest  # noqa: E501
from openapi_server.models.text_id_annotation import TextIdAnnotation
from openapi_server.models.text_id_annotation_response import TextIdAnnotationResponse  # noqa: E501
from openapi_server.spark import spark


def create_text_id_annotations():  # noqa: E501
    """Annotate IDs in a clinical note

    Return the ID annotations found in a clinical note # noqa: E501

    :rtype: TextIdAnnotationResponse
    """
    if connexion.request.is_json:
        try:
            annotation_request = TextIdAnnotationRequest.from_dict(connexion.request.get_json())  # noqa: E501
            note = annotation_request._note
            spark_annotations = spark.annotate(note._text, 'ID')

            annotations = []
            add_id_annotations(annotations, spark_annotations)
            res = TextIdAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            print(str(error))
            status = 500
            res = Error("Internal error", status, str(error))
    return res, status


def add_id_annotations(annotations, id_annotations):
    """
    Converts matches to TextIdAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in id_annotations:
        annotations.append(TextIdAnnotation(
            start=match['begin'],
            length=len(match['chunk']),
            text=match['chunk'],
            id_type="other",
            confidence=95.5
        ))
