import connexion
import json
import os
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_contact_annotation_request import TextContactAnnotationRequest  # noqa: E501
from openapi_server.models.text_contact_annotation import TextContactAnnotation
from openapi_server.models.text_contact_annotation_response import TextContactAnnotationResponse  # noqa: E501
from openapi_server.spark import spark


def create_text_contact_annotations(text_contact_annotation_request=None):  # noqa: E501
    """Annotate contacts in a clinical note
    Return the Contact annotations found in a clinical note # noqa: E501
    :param text_contact_annotation_request:
    :type text_contact_annotation_request: dict | bytes
    :rtype: TextContactAnnotationResponse
    """
    annotations = []
    if connexion.request.is_json:
        try:
            annotation_request = TextContactAnnotationRequest.from_dict(connexion.request.get_json())  # noqa: E501
            note = annotation_request._note
            spark_df = spark.spark.createDataFrame([[note._text]], ["text"])
            spark_df.show(truncate=70)

            model_name = 'models/' + os.environ['NER_MODEL']
            embeddings = 'models/' + os.environ['EMBEDDINGS']

            # TODO Is there a way to tell Spark NLP to look only for CONTACT
            # annotation instead of having it spending time looking for other
            # types of annotations?
            ner_spark_df = spark.get_clinical_entities(spark_df, embeddings, model_name)  # noqa: E501
            print("ner_spark_df", ner_spark_df)
            ner_df = ner_spark_df.toPandas()
            print("ner_df", ner_df)
            ner_df_contact = ner_df.loc[ner_df['ner_label'] == 'CONTACT']
            print("ner_df_contact", ner_df_contact)

            # TODO Why convert to JSON?
            contact_json = ner_df_contact.reset_index().to_json(orient='records')  # noqa: E501
            contact_annotations = json.loads(contact_json)
            print(contact_annotations)

            add_contact_annotation(annotations, contact_annotations)
            res = TextContactAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(str(error))
            res = Error("Internal error", status, str(error))
    return res, status


def add_contact_annotation(annotations, contact_annnotations):
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
            confidence=95.5
        ))
