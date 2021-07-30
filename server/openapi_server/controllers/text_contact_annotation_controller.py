import connexion
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_contact_annotation_request import TextContactAnnotationRequest  # noqa: E501
from openapi_server.models.text_contact_annotation import TextContactAnnotation
from openapi_server.models.text_contact_annotation_response import TextContactAnnotationResponse  # noqa: E501
from openapi_server.spark import spark


def create_text_contact_annotations():  # noqa: E501
    """Annotate contacts in a clinical note

    Return the Contact annotations found in a clinical note # noqa: E501

    :rtype: TextContactAnnotationResponse
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextContactAnnotationRequest.from_dict(connexion.request.get_json())  # noqa: E501
            note = annotation_request._note
            spark_annotations = spark.annotate(note._text, 'CONTACT')

            annotations = []
            add_contact_annotations(annotations, spark_annotations)
            res = TextContactAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(str(error))
            res = Error("Internal error", status, str(error))
    return res, status


def add_contact_annotations(annotations, contact_annnotations):
    """
    Converts matches to TextContactAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in contact_annnotations:
        annotations.append(TextContactAnnotation(
            start=match['begin'],
            length=len(match['chunk']),
            text=match['chunk'],
            contact_type="other",
            confidence=50
        ))
