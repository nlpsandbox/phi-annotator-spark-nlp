import connexion
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_person_name_annotation_request import TextPersonNameAnnotationRequest  # noqa: E501
from openapi_server.models.text_person_name_annotation import TextPersonNameAnnotation  # noqa: E501
from openapi_server.models.text_person_name_annotation_response import TextPersonNameAnnotationResponse  # noqa: E501
from openapi_server.spark import spark


def create_text_person_name_annotations():  # noqa: E501
    """Annotate person names in a clinical note

    Return the person name annotations found in a clinical note # noqa: E501

    :rtype: TextPersonNameAnnotationResponse
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextPersonNameAnnotationRequest.from_dict(connexion.request.get_json())  # noqa: E501
            note = annotation_request._note  # noqa: E501
            spark_annotations = spark.annotate(note._text, 'NAME')

            annotations = []
            add_person_name_annotations(annotations, spark_annotations)
            res = TextPersonNameAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(str(error))
            res = Error("Internal error", status, str(error))
    return res, status


def add_person_name_annotations(annotations, person_name_annnotations):
    """
    Converts matches to TextPersonNameAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in person_name_annnotations:
        annotations.append(TextPersonNameAnnotation(
            start=match['begin'],
            length=len(match['chunk']),
            text=match['chunk'],
            confidence=50
        ))
