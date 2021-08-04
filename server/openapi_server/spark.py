import json
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, monotonically_increasing_id, explode, arrays_zip  # noqa: E501
from sparknlp.annotator import NerConverter, NerDLModel, SentenceDetector, Tokenizer, WordEmbeddingsModel  # noqa: E501
from sparknlp.base import DocumentAssembler
from openapi_server.config import config

from sparknlp_jsl.annotator import NerConverter, NerDLModel, MedicalNerModel, SentenceDetector, Tokenizer, WordEmbeddingsModel  # noqa: E501

# https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/Certification_Trainings/Healthcare/2.Clinical_Assertion_Model.ipynb#scrollTo=kMtWWqFBAMVW
# from sparknlp.annotator import *
# from sparknlp_jsl.annotator import MedicalNerModel
# from sparknlp.base import *
# import sparknlp_jsl
# import sparknlp


class Spark:
    def __init__(self):
        self.spark = None
        self.model = None

    def initialize(self):
        # .config("spark.jars", f"/opt/spark/spark-nlp-assembly-{config.spark_jsl_version}.jar")\
        self.spark = SparkSession.builder\
            .appName("Spark NLP")\
            .master("local[*]")\
            .config("spark.executor.memory", "1G")\
            .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC")\
            .config("spark.driver.memory", "4G")\
            .config("spark.driver.maxResultSize", "0")\
            .config("spark.kryoserializer.buffer.max", "2000M")\
            .config("spark.jars", f"https://pypi.johnsnowlabs.com/{config.spark_jsl_license_secret}/spark-nlp-jsl-{config.spark_jsl_version}.jar")\
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")

        embeddings_model_path = 'models/' + config.embeddings_model
        ner_model_path = 'models/' + config.ner_model

        document_assembler = DocumentAssembler()\
            .setInputCol("text")\
            .setOutputCol("document")

        # Sentence Detector annotator, processes various sentences per line
        sentence_detector = SentenceDetector()\
            .setInputCols(["document"])\
            .setOutputCol("sentence")

        # Tokenizer splits words in a relevant format for NLP
        tokenizer = Tokenizer()\
            .setInputCols(["sentence"])\
            .setOutputCol("token")

        # Clinical word embeddings trained on PubMED dataset
        word_embeddings = WordEmbeddingsModel.load(embeddings_model_path)\
            .setInputCols(["sentence", "token"])\
            .setOutputCol("embeddings")

        base_pipeline = Pipeline(stages=[
            document_assembler,
            sentence_detector,
            tokenizer,
            word_embeddings
        ])

        # All the licensed clinical and biomedical pre-trained NER models will
        # now run with MedicalNerModel instead of its parent NerDLModel from
        # Spark NLP.
        #
        # ner_model = NerDLModel.pretrained("ner_deid_augmented","en","clinical/models")\
        # ner_model = NerDLModel.load(ner_model_path)\
        ner_model = MedicalNerModel.load("models/ner_deid_sd_en_3.0.0_3.0_1617260827858")\
            .setInputCols(["sentence", "token", "embeddings"])\
            .setOutputCol("ner")

        ner_converter = NerConverter()\
            .setInputCols(["sentence", "token", "ner"])\
            .setOutputCol("ner_chunk")

        nlp_pipeline = Pipeline(stages=[
            base_pipeline,
            ner_model,
            ner_converter])

        empty_data = self.spark.createDataFrame([[""]]).toDF("text")
        self.model = nlp_pipeline.fit(empty_data)

    def annotate(self, text, ner_label):
        if self.model is None:
            self.initialize()

        spark_df = self.spark.createDataFrame([[text]], ["text"])
        # spark_df.show(truncate=70)

        result = self.model.transform(spark_df)
        result = result.withColumn("id", monotonically_increasing_id())

        result_df = result.select('id', explode(arrays_zip('ner_chunk.result', 'ner_chunk.begin',  # noqa: E501
                                  'ner_chunk.end', 'ner_chunk.metadata')).alias("cols"))\
            .select('id', expr("cols['3']['sentence']").alias("sentence_id"),
                    expr("cols['0']").alias("chunk"),
                    expr("cols['1']").alias("begin"),
                    expr("cols['2']").alias("end"),
                    expr("cols['3']['entity']").alias("ner_label"))\
            .filter("ner_label!='O'")

        ner_df = result_df.toPandas()
        ner_df = ner_df.loc[ner_df['ner_label'] == ner_label]
        date_json = ner_df.reset_index().to_json(orient='records')
        return json.loads(date_json)


spark = Spark()
