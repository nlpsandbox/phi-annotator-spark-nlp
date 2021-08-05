FROM python:3.9.6-slim-buster

ARG CONFIG_NAME
ARG SPARK_NLP_LICENSE=""
ARG SPARK_AWS_ACCESS_KEY_ID=""
ARG SPARK_AWS_SECRET_ACCESS_KEY=""
ARG SPARK_JSL_VERSION="3.1.1"
ARG NER_MODEL
ARG EMBEDDINGS_MODEL

ENV APP_DIR=/opt/app \
    CONFIG_NAME=${CONFIG_NAME} \
    SPARK_NLP_LICENSE=${SPARK_NLP_LICENSE} \
    SPARK_AWS_ACCESS_KEY_ID=${SPARK_AWS_ACCESS_KEY_ID} \
    SPARK_AWS_SECRET_ACCESS_KEY=${SPARK_AWS_SECRET_ACCESS_KEY} \
    SPARK_JSL_VERSION=${SPARK_JSL_VERSION} \
    SPARK_HOME=/opt/spark \
    NER_MODEL=${NER_MODEL} \
    EMBEDDINGS_MODEL=${EMBEDDINGS_MODEL} \
    # Set Tensorflow log level (3: ERROR)
    TF_CPP_MIN_LOG_LEVEL="3" \
    JAVA_TOOL_OPTIONS="-Xmx4G -Dorg.bytedeco.javacpp.maxBytes=0"
ENV PATH="${PATH}:${SPARK_HOME}/bin:${SPARK_HOME}/sbin"

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update -qq -y \
    && mkdir -p /usr/share/man/man1 \
    && apt-get install --no-install-recommends -qq -y \
        build-essential \
        gosu \
        libpcre3 \
        libpcre3-dev \
        gnupg \
        software-properties-common \
        curl \
        procps \
        unar \
    && curl https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add - \
    && add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ \
    && apt-get update \
    && apt-get install --no-install-recommends -qq -y adoptopenjdk-8-hotspot \
    && apt-get -y autoclean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*

# Install Apache Spark and Spark NLP
WORKDIR ${SPARK_HOME}
# waiting for curl --output-dir [directory] that comes in curl 7.73.0
# hadolint ignore=DL3003
RUN curl -O https://archive.apache.org/dist/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz \
    && tar xvf spark-3.1.1-bin-hadoop3.2.tgz --strip-components 1 \
    && rm -fr spark-3.1.1-bin-hadoop3.2.tgz \
    # Install Spark NLP JSL library for Python
    && pip install --no-cache-dir -q spark-nlp-jsl==${SPARK_JSL_VERSION} \
        --extra-index-url https://pypi.johnsnowlabs.com/${SPARK_NLP_LICENSE} \
        --upgrade \
    # Download public and JSL fat JARs
    && cd ${SPARK_HOME}/jars \
    && curl -O https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/jars/spark-nlp-assembly-3.1.1.jar \
    && curl -O https://pypi.johnsnowlabs.com/${SPARK_NLP_LICENSE}/spark-nlp-jsl-${SPARK_JSL_VERSION}.jar

# Download Spark NLP models
WORKDIR /tmp/models
ENV AWS_ACCESS_KEY_ID=${SPARK_AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${SPARK_AWS_SECRET_ACCESS_KEY}
RUN pip install --no-cache-dir awscli==1.20.10 \
    && aws configure set default.region us-west-1 \
    && aws s3 cp s3://auxdata.johnsnowlabs.com/clinical/models/${NER_MODEL}.zip . \
    && aws s3 cp s3://auxdata.johnsnowlabs.com/clinical/models/${EMBEDDINGS_MODEL}.zip . \
    && unar -d ${NER_MODEL}.zip \
    && unar -d ${EMBEDDINGS_MODEL}.zip \
    && rm -fr ./*.zip

# Install NLP Sandbox tool
WORKDIR ${APP_DIR}
COPY requirements.txt prod-requirements.txt uwsgi.ini ./
RUN pip install --no-cache-dir \
        -r requirements.txt -r prod-requirements.txt
COPY openapi_server openapi_server/
# Create the user used by uWSGI to run the tool
RUN useradd --create-home --shell /bin/bash nlp \
    # Move Spark NLP models
    && mkdir models \
    && mv /tmp/models/* models/. \
    # Give user access to the app directory
    && chown -R nlp:nlp ${APP_DIR}

WORKDIR /
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8080 8081

ENTRYPOINT ["/docker-entrypoint.sh"]

# Run server in development mode
# CMD ["python", "-m", "openapi_server"]

# Run server in production mode
CMD ["uwsgi", "--ini", "uwsgi.ini", "--lazy", "--http", ":8080"]