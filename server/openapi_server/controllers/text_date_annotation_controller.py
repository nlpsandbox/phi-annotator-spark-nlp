import connexion
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_date_annotation_request import \
    TextDateAnnotationRequest  # noqa: E501
from openapi_server.models.text_date_annotation import TextDateAnnotation
from openapi_server.models.text_date_annotation_response import \
    TextDateAnnotationResponse  # noqa: E501
from openapi_server.spark import spark


def create_text_date_annotations():  # noqa: E501
    """Annotate dates in a clinical note

    Return the date annotations found in a clinical note # noqa: E501

    :rtype: TextDateAnnotations
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextDateAnnotationRequest.from_dict(
                connexion.request.get_json())  # noqa: E501
            note = annotation_request._note
            spark_annotations = spark.annotate(note._text, 'DATE')

            annotations = []
            add_date_annotation(annotations, spark_annotations)
            res = TextDateAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(str(error))
            res = Error("Internal error", status, str(error))
    return res, status


def add_date_annotation(annotations, date_annotations):
    """
    Converts matches to TextDateAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in date_annotations:
        annotations.append(TextDateAnnotation(
            start=match['begin'],
            text=match['chunk'],
            length=len(match['chunk']),
            # date_format=get_date_format(match['chunk']),
            confidence=95.5
        ))
