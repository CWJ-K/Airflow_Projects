<!-- omit in toc -->
# Introduction
Take notes of parameters involved in Airflow.

<br />

<!-- omit in toc -->
# Table of Contents
- [Fundamental Concepts](#fundamental-concepts)
- [API](#api)
- [XCom](#xcom)
  - [Operators](#operators)
    - [PythonOperator](#pythonoperator)
    - [EmptyOperator](#emptyoperator)
    - [TriggerDagRunOperator](#triggerdagrunoperator)
    - [SimpleHttpOperator](#simplehttpoperator)
    - [Operators for Cloud Servers](#operators-for-cloud-servers)
    - [Operators for running a heavy work](#operators-for-running-a-heavy-work)
    - [DockerOperator](#dockeroperator)
      - [auto_remove](#auto_remove)
      - [docker_url](#docker_url)
  - [Rules of Tasks](#rules-of-tasks)
    - [atomicity](#atomicity)
    - [Idempotent](#idempotent)
      - [How to achieve it?](#how-to-achieve-it)
- [Technical Plans](#technical-plans)
    - [1. Is the data processed again at some other time in the future?](#1-is-the-data-processed-again-at-some-other-time-in-the-future)
    - [2. How do I receive the data? Frequency, size, format, source type](#2-how-do-i-receive-the-data-frequency-size-format-source-type)
    - [3. What are we going to build with the data](#3-what-are-we-going-to-build-with-the-data)

<br />

# Fundamental Concepts

# API
* an interface to connect and send requests to other services
* e.g. API of cloud servers in Python
  |Cloud Server| API|
  |:---:|:---:|
  |AWS|boto3|
  |GCP|Cloud SDK|
  |Azure|Azure SDK for Python|

# XCom
* in a live Airflow setup, any objects returned by an operator are automatically pushed to XCom

<br />

## Operators
* most operators are **installed** by separate **pip packages**
  > apache-airflow-providers-*
* can internally handle the technical implementation
  > that is why many features using operators 

<br />

### PythonOperator
* python_callable <br />
python function which is callable
* template_fields= ['templates_dict', 'op_args', 'op_kwargs']
  
  holds a list of attributes that can be templated. So that, Airflow arguments, e.g. ds, next_ds, can be passed to the templates

  * templates_dict
  * op_args
  * op_kwargs

<br />

### EmptyOperator
* An Operator does nothing

<br />

### TriggerDagRunOperator
```mermaid
flowchart LR
    subgraph DAG 1
    etl1 <-.trigger.-> trigger1_dag4
    end

    subgraph DAG 2 

    etl2 <-.trigger.-> trigger2_dag4
    end

    subgraph DAG 3
    etl3 <-.trigger.-> trigger3_dag4
    end

    subgraph DAG 4
    trigger1_dag4 --> produce_report
    trigger2_dag4 --> produce_report
    trigger3_dag4 --> produce_report
    end

```

* trigger the next dag to run 
* if backfill, clearing TriggerDagRunOperators does not clear tasks in the triggered DAG, but a new DAG runs
  
<br />

### SimpleHttpOperator
* request http and get the response

<br />

### Operators for Cloud Servers
* an Airflow operator can communicate with the Cloud SDK by giving arguments
* required packages to be installed
  |Cloud|Install|
  |:---:|:---:|
  |AWS| pip install apache-airflow-providers-amazon |
  |GCP| pip install apache-airflow-providers-google |
  |Azure| pip install apache-airflow-providers-microsoft-azure |
  > The implementation of the AWS operator calls copy_object() on boto3

<br />

### Operators for running a heavy work
* Use Spark
  * SparkSubmitOperator
  * SSHOperator
  * SimpleHTTPOperator

### DockerOperator
#### auto_remove
* remove the container after completion
#### docker_url
* set to Unix socket: requires Docker running on the local machine



## Rules of Tasks
### atomicity
* should follow atomicity to make sure a task will not produce half work if the task failed. 
  
  <br />
  e.g. a task includes writing data and sending mails if sending mails fails, but data already is stored in the local directory. 

* Solution
  split tasks into multiple tasks => make sure each task has only one purpose 

<br />

### Idempotent
* if a task is called several times, its output should be identical every time 

#### How to achieve it?
* set a flag to **overwrite** destination files
```
Process of overwrite: 
e.g. date columns
1. delete existing data with current date
2. insert data with current date
```
<br />

# Technical Plans
before building a pipeline, having a technical plan is required. Questions of Technical Plans are provided below:

### 1. Is the data processed again at some other time in the future?
### 2. How do I receive the data? Frequency, size, format, source type
### 3. What are we going to build with the data 