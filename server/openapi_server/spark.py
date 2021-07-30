import json
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, monotonically_increasing_id, explode, arrays_zip  # noqa: E501
from sparknlp.annotator import NerConverter, NerDLModel, SentenceDetector, Tokenizer, WordEmbeddingsModel  # noqa: E501
from sparknlp.base import DocumentAssembler
from openapi_server.config import config


class Spark:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("Spark NLP") \
            .master("local[*]") \
            .config("spark.driver.memory", "16G") \
            .config("spark.driver.maxResultSize", "0") \
            .config("spark.kryoserializer.buffer.max", "2000M") \
            .config("spark.jars", f"/opt/spark/spark-nlp-assembly-{config.spark_jsl_version}.jar") \
            .getOrCreate()

        # WARN level returns too much logging messages
        self.spark.sparkContext.setLogLevel("ERROR")

    def get_base_pipeline(self, embeddings):
        document_assembler = DocumentAssembler() \
            .setInputCol("text")\
            .setOutputCol("document")

        # Sentence Detector annotator, processes various sentences per line
        sentence_detector = SentenceDetector() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")

        # Tokenizer splits words in a relevant format for NLP
        tokenizer = Tokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")

        # Clinical word embeddings trained on PubMED dataset
        word_embeddings = WordEmbeddingsModel.load(embeddings)\
            .setInputCols(["sentence", "token"])\
            .setOutputCol("embeddings")

        base_pipeline = Pipeline(stages=[
            document_assembler,
            sentence_detector,
            tokenizer,
            word_embeddings
        ])

        return base_pipeline

    def get_clinical_entities(self, spark_df, embeddings_model_path, ner_model_path):  # noqa: E501
        base_pipeline = self.get_base_pipeline(embeddings_model_path)

        ner_model = NerDLModel.load(ner_model_path) \
            .setInputCols(["sentence", "token", "embeddings"]) \
            .setOutputCol("ner")

        ner_converter = NerConverter() \
            .setInputCols(["sentence", "token", "ner"]) \
            .setOutputCol("ner_chunk")

        nlp_pipeline = Pipeline(stages=[
            base_pipeline,
            ner_model,
            ner_converter])

        empty_data = self.spark.createDataFrame([[""]]).toDF("text")
        model = nlp_pipeline.fit(empty_data)

        result = model.transform(spark_df)
        result = result.withColumn("id", monotonically_increasing_id())

        result_df = result.select('id', explode(arrays_zip('ner_chunk.result', 'ner_chunk.begin',  # noqa: E501
                                  'ner_chunk.end', 'ner_chunk.metadata')).alias("cols")) \
            .select('id', expr("cols['3']['sentence']").alias("sentence_id"),
                    expr("cols['0']").alias("chunk"),
                    expr("cols['1']").alias("begin"),
                    expr("cols['2']").alias("end"),
                    expr("cols['3']['entity']").alias("ner_label")) \
            .filter("ner_label!='O'")

        return result_df.toPandas()

    def annotate(self, text, ner_label):
        spark_df = self.spark.createDataFrame([[text]], ["text"])
        # spark_df.show(truncate=70)

        embeddings_model_path = 'models/' + config.embeddings_model
        ner_model_path = 'models/' + config.ner_model

        ner_df = self.get_clinical_entities(spark_df, embeddings_model_path, ner_model_path)  # noqa: E501
        ner_df = ner_df.loc[ner_df['ner_label'] == ner_label]
        date_json = ner_df.reset_index().to_json(orient='records')
        return json.loads(date_json)


spark = Spark()
