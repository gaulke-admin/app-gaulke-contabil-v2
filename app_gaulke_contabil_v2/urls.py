from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('accounts/', views.accounts, name="accounts"),
    path('accounts/adit/user/', views.accounts_edit_user, name="accounts_edit_user"),
    path('manager/users/check-user/', views.check_user, name="check_user"),
    path('manager/users/get-all-users/', views.manager_users, name="manager_users"),
    path('deliveries-IR/', views.deliveries_IR, name="deliveries_IR"),
    path('clientes/', views.clients, name="clients"),
    path('configurations/', views.configuracoes, name="configurations"),
    path('report-01/', views.report_01, name="report_01"),


    # ------------------- IMPORTS JB -------------------
    path('imports-JB/', views.imports_JB, name="imports_JB"),
    path('imports-JB/post-data-to-import/', views.post_file_to_import_JB, name="post_file_to_import_JB"),

    # ------------------- APONT HOUR -------------------
    path('apontamentos-de-horas/', views.apont_hours, name="apont_hours"),
    path('apontamentos-de-horas/new-task/', views.apont_hours_new_subtask, name="apont_hours_new_subtask"),
    path('apontamentos-de-horas/info/', views.get_info_apont_hour, name="get_info_apont_hour"),



    # -------------------- POST FILE UPDATE I.R --------------------
    # >> arquivo das declarações cadastradas no JB Software Smart <<

    path('post-file-JB-smart-IR/', views.post_file_JB_smart_IR, name="post_file_JB_smart_IR"),
    path('post-file-drid-declaracoes/', views.post_file_grid_declaracoes, name="post_file_grid_declaracoes"),


    # ------------------- CREATE CLIENT I.R -------------------

    path('post-create-new-client/', views.post_create_new_client, name="post_create_new_client"),

    # ------------------- CREATE I.R -------------------

    path('post-create-new-IR/', views.post_create_new_IR, name="post_create_new_IR"),
    path('post-create-new-comment/', views.post_create_new_comment, name="post_create_new_comment"),


    # ------------------- GET INFO I.R -------------------

    path('get-all-data-JB-smart-IR', views.get_all_data_JB_smart_IR, name="get_all_data_JB_smart_IR"),
    path('get-all-clients', views.get_all_clients, name="get_all_clients"),

    # ------------------- UPDATE INFO I.R -------------------

    path('update-values-lote-IR', views.post_edit_lote_IR, name="post_edit_lote_IR"),

    # ------------------- CREATE DETELE I.R, CLIENT AND COMMENT I.R  -------------------

    path('post-delete-IR/', views.post_delete_iR, name="post_delete_iR"),
    path('post-delete-client/', views.post_delete_client, name="post_delete_client"),
    path('post-delete-comment-IR/', views.post_delete_comment_IR, name="post_delete_comment_IR"),

    # ----

    path('post-edit-value-data-pagamento/', views.post_edit_value_data_pagamento, name="post_edit_value_data_pagamento"),
    path('post-edit-value-IR/', views.post_edit_value_IR, name="post_edit_value_IR"),
    path('post-edit-comment-IR/', views.post_edit_comment_IR, name="post_edit_comment_IR"),
    path('post-edit-value-client/', views.post_edit_value_client, name="post_edit_value_client"),
    path('get-comments/', views.get_comments, name="get_comments"),


    # ------------------- QUERIES -------------------
    path('post-query-by-field-cod-sistema/', views.post_query_by_field_cod_sistema, name="post_query_by_field_cod_sistema"),
    path('post-query-by-cpf/', views.post_query_by_cpf, name="post_query_by_cpf"),
    
]