import os
import json
from sparknlp.annotator import NerConverter, NerDLModel, SentenceDetector, Tokenizer, WordEmbeddingsModel  # noqa: E501
from sparknlp.base import DocumentAssembler
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
import pyspark.sql.functions as F
from pyspark.sql.functions import monotonically_increasing_id
from openapi_server.config import config


class Spark:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("Spark NLP") \
            .master("local[*]") \
            .config("spark.driver.memory","16G") \
            .config("spark.driver.maxResultSize", "0") \
            .config("spark.kryoserializer.buffer.max", "2000M") \
            .config("spark.jars", f"/opt/spark/spark-nlp-assembly-{config.spark_jsl_version}.jar") \
            .getOrCreate()

    def get_base_pipeline(self, embeddings):
        documentAssembler = DocumentAssembler()\
            .setInputCol("text")\
            .setOutputCol("document")

        # Sentence Detector annotator, processes various sentences per line
        sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")  # noqa: E501

        # Tokenizer splits words in a relevant format for NLP
        tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")  # noqa: E501

        # Clinical word embeddings trained on PubMED dataset
        word_embeddings = WordEmbeddingsModel.load(embeddings)\
            .setInputCols(["sentence", "token"])\
            .setOutputCol("embeddings")

        base_pipeline = Pipeline(stages=[
            documentAssembler,
            sentenceDetector,
            tokenizer,
            word_embeddings
        ])

        return base_pipeline

    def get_clinical_entities(self, spark_df, embeddings, model_name):

        # NER model trained on i2b2 (sampled from MIMIC) dataset
        loaded_ner_model = NerDLModel.load(model_name) \
            .setInputCols(["sentence", "token", "embeddings"]) \
            .setOutputCol("ner")

        ner_converter = NerConverter() \
            .setInputCols(["sentence", "token", "ner"]) \
            .setOutputCol("ner_chunk")

        base_pipeline = self.get_base_pipeline(embeddings)

        nlpPipeline = Pipeline(stages=[
            base_pipeline,
            loaded_ner_model,
            ner_converter])

        empty_data = self.spark.createDataFrame([[""]]).toDF("text")

        model = nlpPipeline.fit(empty_data)

        result = model.transform(spark_df)
        result = result.withColumn("id", monotonically_increasing_id())

        result_df = result.select('id', F.explode(F.arrays_zip('ner_chunk.result', 'ner_chunk.begin',  # noqa: E501
                                  'ner_chunk.end', 'ner_chunk.metadata')).alias("cols")) \
            .select('id', F.expr("cols['3']['sentence']").alias("sentence_id"),
                    F.expr("cols['0']").alias("chunk"),
                    F.expr("cols['1']").alias("begin"),
                    F.expr("cols['2']").alias("end"),
                    F.expr("cols['3']['entity']").alias("ner_label"))\
            .filter("ner_label!='O'")

        return result_df.toPandas()

    def annotate(self, text, ner_label):
        spark_df = self.spark.createDataFrame([[text]], ["text"])
        # spark_df.show(truncate=70)

        embeddings = 'models/' + os.environ['EMBEDDINGS']
        model_name = 'models/' + os.environ['NER_MODEL']

        ner_df = self.get_clinical_entities(spark_df, embeddings, model_name)
        ner_df = ner_df.loc[ner_df['ner_label'] == ner_label]
        date_json = ner_df.reset_index().to_json(orient='records')
        return json.loads(date_json)


spark = Spark()
