FROM python:3.9.5-slim-buster

ENV APP_DIR=/opt/app

ARG SPARK_LICENSE_KEY=""
ENV SPARK_LICENSE_KEY=${SPARK_LICENSE_KEY}

ARG SPARK_LICENSE_SECRET=""
ENV SPARK_LICENSE_SECRET=${SPARK_LICENSE_SECRET}

ARG SPARK_AWS_ACCESS_KEY_ID=""
ENV SPARK_AWS_ACCESS_KEY_ID=${SPARK_AWS_ACCESS_KEY_ID}

ARG SPARK_AWS_SECRET_ACCESS_KEY=""
ENV SPARK_AWS_SECRET_ACCESS_KEY=${SPARK_AWS_SECRET_ACCESS_KEY}

ARG SPARK_JSL_VERSION="3.1.2"
ENV SPARK_JSL_VERSION=${SPARK_JSL_VERSION}

ARG SPARK_PUBLIC_VERSION=""
ENV SPARK_PUBLIC_VERSION=${SPARK_PUBLIC_VERSION}

ENV SPARK_HOME=/opt/spark
ENV PATH="${PATH}:${SPARK_HOME}/bin:${SPARK_HOME}/sbin"

ARG NER_DEID_LARGE_EN
ENV NER_DEID_LARGE_EN=${NER_DEID_LARGE_EN}

ARG SENTENCE_DETECTOR_DL_HEALTHCARE_EN
ENV SENTENCE_DETECTOR_DL_HEALTHCARE_EN=${SENTENCE_DETECTOR_DL_HEALTHCARE_EN}

ARG EMBEDDINGS_CLINICAL_EN
ENV EMBEDDINGS_CLINICAL_EN=${EMBEDDINGS_CLINICAL_EN}

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update -qq -y \
    && mkdir -p /usr/share/man/man1 \
    && apt-get install --no-install-recommends -qq -y \
        build-essential \
        gosu \
        libpcre3 \
        libpcre3-dev \
        default-jre \
        curl \
        procps \
        unar \
    && apt-get -y autoclean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*

# Install Spark NLP
WORKDIR ${SPARK_HOME}
RUN curl -O https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz \
    && tar xvf spark-3.1.2-bin-hadoop3.2.tgz --strip-components 1 \
    && rm -fr spark-3.1.2-bin-hadoop3.2.tgz \
    # Install Spark NLP for Healthcare
    && pip install -q spark-nlp-jsl==${SPARK_JSL_VERSION} \
        --extra-index-url https://pypi.johnsnowlabs.com/${SPARK_LICENSE_SECRET} \
        --upgrade

# Download Spark NLP models
WORKDIR /tmp/models
ENV AWS_ACCESS_KEY_ID=${SPARK_AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${SPARK_AWS_SECRET_ACCESS_KEY}
RUN pip install awscli \
    && aws configure set default.region us-west-1 \
    && aws s3 cp s3://auxdata.johnsnowlabs.com/clinical/models/${NER_DEID_LARGE_EN}.zip . \
    && aws s3 cp s3://auxdata.johnsnowlabs.com/clinical/models/${SENTENCE_DETECTOR_DL_HEALTHCARE_EN}.zip . \
    && aws s3 cp s3://auxdata.johnsnowlabs.com/clinical/models/${EMBEDDINGS_CLINICAL_EN}.zip . \
    && unar -d ${NER_DEID_LARGE_EN}.zip \
    && unar -d ${SENTENCE_DETECTOR_DL_HEALTHCARE_EN}.zip \
    && unar -d ${EMBEDDINGS_CLINICAL_EN}.zip \
    && rm -fr *.zip

# Install NLP Sandbox tool
WORKDIR ${APP_DIR}
COPY openapi_server openapi_server/
COPY data data/
COPY models models/
COPY requirements.txt prod-requirements.txt uwsgi.ini ./
RUN pip install --no-cache-dir \
        -r requirements.txt -r prod-requirements.txt \
    # Create the user used by uWSGI to run the tool
    && useradd --create-home --shell /bin/bash nlp \
    # Move Spark NLP models
    && mv /tmp/models/* models/. \
    && chown -R nlp:nlp ${APP_DIR}

WORKDIR /
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8080 8081

ENTRYPOINT ["/docker-entrypoint.sh"]

# Run server in development mode
# CMD ["python", "-m", "openapi_server"]

# Run server in production mode
CMD ["uwsgi", "--ini", "uwsgi.ini", "--lazy", "--http", ":8081"]