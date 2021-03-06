<!-- omit in toc -->
# Introduction
How are tasks executed in a specific order?

<br />

<!-- omit in toc -->
# Table of Contents
- [Fundamental Concepts](#fundamental-concepts)
  - [1. fan-out dependency](#1-fan-out-dependency)
  - [2. fan-in dependency](#2-fan-in-dependency)
  - [3. BranchPythonOperator](#3-branchpythonoperator)
  - [4. AirflowSkipException](#4-airflowskipexception)
- [Commands](#commands)
  - [1. BranchPythonOperator](#1-branchpythonoperator)
  - [2. Case: only uses the latest data to deploy models. Avoid backfilling data leads to deploying the wrong models](#2-case-only-uses-the-latest-data-to-deploy-models-avoid-backfilling-data-leads-to-deploying-the-wrong-models)

<br />

# Fundamental Concepts

<br />

## 1. fan-out dependency 
* one to multiple dependencies
  
        start >> [task1, task2]

<br />

## 2. fan-in dependency
* multiple to one dependency
    
        [task1, task2] >> start

<br />

## 3. BranchPythonOperator
* Conditions decide which task to be run
  * develop distinct sets of tasks 
  * let DAG choose which one to execute
* return the ID (the list of ID) of a downstream task
* Cooperate with **trigger_rule** of PythonOperator
  * trigger_rule: none_failed, all_failed, all_done, all_success(default) ...

<br />

## 4. AirflowSkipException
* Raise when the task should be skipped
  
<br />

# Commands

<br />

## 1. BranchPythonOperator

```python
    def _pick_erp_system(**context):
            if context["execution_date"] < ERP_CHANGE_DATE:
                    return "fetch_sales_old"
            else:
                    return "fetch_sales_new"

    pick_erp_system = BranchPythonOperator(
            task_id="pick_erp_system", python_callable=_pick_erp_system
    )


    fetch_sales_old = PythonOperator(
            task_id="fetch_sales_old", python_callable=_fetch_sales_old
    )

    fetch_sales_new = PythonOperator(
            task_id="fetch_sales_new", python_callable=_fetch_sales_new
    )

    get_sales = DummyOperator(
            task_id="join_datasets", trigger_rule="none_failed"
    )

    pick_erp_system >> [fetch_sales_old, fetch_sales_new]

    fetch_sales_old >> clean_sales_old

    fetch_sales_new >> clean_sales_new

    [clean_sales_old, clean_sales_new] >> get_sales
```

<br />

## 2. Case: only uses the latest data to deploy models. Avoid backfilling data leads to deploying the wrong models


```python
    def _is_latest_run(**context):
        now = pendulum.now("UTC")
        left_window = context["dag"].following_schedule(context["execution_date"])
        right_window = context["dag"].following_schedule(left_window)
        if not left_window < now <= right_window:
                raise AirflowSkipException()
        
```      