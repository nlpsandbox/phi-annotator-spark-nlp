import connexion
import json
import os
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_person_name_annotation_request import TextPersonNameAnnotationRequest  # noqa: E501
from openapi_server.models.text_person_name_annotation import TextPersonNameAnnotation  # noqa: E501
from openapi_server.models.text_person_name_annotation_response import TextPersonNameAnnotationResponse  # noqa: E501
from openapi_server import spark as cf


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
            annotations = []

            input_df = [note._text]
            spark_df = cf.spark.createDataFrame([input_df], ["text"])
            spark_df.show(truncate=70)

            embeddings = 'models/' + os.environ['EMBEDDINGS']
            model_name = 'models/' + os.environ['NER_MODEL']

            ner_df = cf.get_clinical_entities(cf.spark, embeddings, spark_df, model_name)
            df = ner_df.toPandas()
            df_name = df.loc[df['ner_label'] == 'NAME']
            name_json = df_name.reset_index().to_json(orient='records')
            name_annotations = json.loads(name_json)

            for match in name_annotations:
                annotations.append(TextPersonNameAnnotation(
                            start=match['begin'],
                            length=len(match['chunk']),
                            text=match['chunk'],
                            confidence=95.5
                        ))
            res = TextPersonNameAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(str(error))
            res = Error("Internal error", status, str(error))
    return res, status
