import connexion
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_location_annotation import TextLocationAnnotation  # noqa: E501
from openapi_server.models.text_location_annotation_request import TextLocationAnnotationRequest  # noqa: E501
from openapi_server.models.text_location_annotation_response import TextLocationAnnotationResponse  # noqa: E501
from openapi_server.spark import spark


def create_text_location_annotations():  # noqa: E501
    """Annotate locations in a clinical note

    Return the location annotations found in a clinical note # noqa: E501

    :rtype: TextLocationAnnotationResponse
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextLocationAnnotationRequest.from_dict(connexion.request.get_json())  # noqa: E501
            note = annotation_request._note
            spark_annotations = spark.annotate(note._text, 'LOCATION')

            annotations = []
            add_location_annotations(annotations, spark_annotations)
            res = TextLocationAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(str(error))
            res = Error("Internal error", status, str(error))
    return res, status


def add_location_annotations(annotations, location_annotations):
    """
    Converts matches to TextLocationAnnotation objects and adds them
    to the annotations array specified.
    """
    for match in location_annotations:
        annotations.append(
            TextLocationAnnotation(
                start=match['begin'],
                length=len(match['chunk']),
                text=match['chunk'],
                location_type='',
                confidence=50
            ))
