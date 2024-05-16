import re
import json

from dateutil import tz
from datetime import datetime, timedelta
from django.utils import timezone


# from .backends import EmailBackend
from django.db import connections
from django.shortcuts import render, redirect
from django.http.response import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as login_django, logout as logout_django
from django.contrib.auth.hashers import make_password

from .models import Model_tb_imposto_de_renda, Model_tb_clients, Model_tb_imposto_de_renda_comments, Model_tb_users
from .models import Model_tb_apontamento_horas_matriz, Model_tb_subtasks_apont_horas
from .models import customuser

from django.contrib.auth import get_user_model
User = get_user_model()



from prepare_data.prepare_data import PrepareData, ConvertToDataFrame
import pandas as pd

with open("config.json", "r") as f:
    configs = json.loads(f.read())



def criptografar_senha(senha):
    senha_criptografada = make_password(senha)
    return senha_criptografada

def validar_email(email):
    try:
        # regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        regex = re.compile(r'^[a-zA-Z0-9_.+-]+@contabilgaulke\.com\.br$')
        if re.match(regex, email):
            return True
        else:
            return False
    except:
        return False

def login(request):
    next_url = request.GET.get("next")
    if request.method == "GET":
        print(request)
        print(next_url)
        if next_url:
            context = {
                "next": True,
                "next_url": next_url
            }
            return render(request, "app/login.html", context=context)
        return render(request, "app/login.html")
    
    elif request.method == "POST":

        # print("\n\n\n ---------------------- POST LOGIN  ---------------------- ")
        # print(request.POST)
        # print(request)

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            print("\n\n ----------------------- USER ----------------------- ")
            user = authenticate(request, username=username, password=password)

            if user:
                login_django(request, user, backend='django.contrib.auth.backends.ModelBackend')
                print("usuário logado com sucesso")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect("home")            

            context = {
                "username": username,
                "password": password,
                "error_login_user": True
            }
            
            return render(request, "app/login.html", context=context)
        except Exception as e:
            print(f"\n\n #### ERROR LOGIN | ERROR: {e}")
            if next_url:
                context = {
                    "next": True,
                    "next_url": next_url,
                    "username": username,
                    "password": password,
                }
                return render(request, "app/login.html", context=context)
            return render(request, "app/login.html", context={
                "username": username,
                "password": password,
            })

def logout(request):
    logout_django(request)
    return redirect("login")

@login_required
def accounts(request):
    if request.method == "GET":
        return render(request, "app/register.html")
    
    elif request.method == "POST":

        # -------------------------------------------------------------------------------------------------------------
        # --------------------------------------------- create - new user ---------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        username    = request.POST.get("username")
        first_name  = request.POST.get("first_name")
        last_name   = request.POST.get("last_name")
        password    = request.POST.get("password")
        password_2  = request.POST.get("password_2")
        # --------------------------------------------------------------------
        sector                      = request.POST.get("sector")
        sessao_atividades           = request.POST.get("sessao_atividades")
        sessao_relatorios           = request.POST.get("sessao_relatorios")
        sessao_imposto_de_renda     = request.POST.get("sessao_imposto_de_renda")
        sessao_config_users         = request.POST.get("sessao_config_users")

        password_cript = criptografar_senha(senha=password)


        db = customuser()

        db.is_staff = False
        db.is_active = True
        db.is_superuser = False
        # db.is_anonymous = ?

        db.email = username
        db.first_name = first_name
        db.last_name = last_name
        db.sector = sector
        db.password = password_cript
                
        if sessao_atividades == "on":
            db.sessao_atividades = 1
        else:
            db.sessao_atividades = 0
        # ----
        if sessao_relatorios == "on":
            db.sessao_relatorios = 1
        else:
            db.sessao_relatorios = 0
        # ----
        if sessao_imposto_de_renda == "on":
            db.sessao_imposto_de_renda = 1
        else:
            db.sessao_imposto_de_renda = 0
        # ----
        if sessao_config_users == "on":
            db.sessao_config_users = 1
        else:
            db.sessao_config_users = 0

        db.save()
        return redirect("accounts")
    
    return redirect("accounts")

@login_required
def accounts_edit_user(request):

    if request.method == "POST":

        # -------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------ edit - user ------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        
        user_id_edit                = request.POST.get("user_id_edit")
        first_name                  = request.POST.get("edit_first_name")
        last_name                     = request.POST.get("edit_last_name")
        username                    = request.POST.get("edit_username")
        password                    = request.POST.get("edit_password")
        sector                      = request.POST.get("edit_sector")
        sessao_atividades           = request.POST.get("edit_sessao_atividades")
        sessao_relatorios           = request.POST.get("edit_sessao_relatorios")
        sessao_imposto_de_renda     = request.POST.get("edit_sessao_imposto_de_renda")
        sessao_config_users         = request.POST.get("edit_sessao_config_users")
        password_cript = criptografar_senha(senha=password)

        print(f"""
            --------------------------------------------------
            >> user_id_edit: {user_id_edit}
            >> first_name: {first_name}
            >> last_name: {last_name}
            >> username: {username}
            >> password: {password}
            >> sector: {sector}
            >> sessao_atividades: {sessao_atividades}
            >> sessao_relatorios: {sessao_relatorios}
            >> sessao_imposto_de_renda: {sessao_imposto_de_renda}
            >> sessao_config_users: {sessao_config_users}
            >> password_cript: {password_cript}
        """)
        
        db = customuser.objects.get(pk=user_id_edit)

        # db.is_staff = False
        # db.is_active = True
        # db.is_superuser = False
        # db.is_anonymous = ?

        db.first_name = first_name
        db.last_name = last_name
        db.email = username
        db.sector = sector
        db.password = password_cript
                
        if sessao_atividades == "on":
            db.sessao_atividades = 1
        else:
            db.sessao_atividades = 0
        # ----
        if sessao_relatorios == "on":
            db.sessao_relatorios = 1
        else:
            db.sessao_relatorios = 0
        # ----
        if sessao_imposto_de_renda == "on":
            db.sessao_imposto_de_renda = 1
        else:
            db.sessao_imposto_de_renda = 0
        # ----
        if sessao_config_users == "on":
            db.sessao_config_users = 1
        else:
            db.sessao_config_users = 0

        db.save()
        return redirect("accounts")
    
    elif request.method == "DELETE":
        try:
            # -------------------------------------------------------------------------------------------------------------
            # ----------------------------------------------- delete - user -----------------------------------------------
            # -------------------------------------------------------------------------------------------------------------
            body = json.loads(request.body)
            user_id = body["user_id"]
            
            print(f"""
                --------------------------------------------------
                >> user_id: {user_id}
            """)
            
            db = customuser.objects.get(pk=user_id).delete()

            print(f"\n\n SUCCESS DELETE USER | USER: {user_id}")
            return JsonResponse({
                "code": 200,
                "msg": "success"
            })
     
        except Exception as e:
            print(f"\n\n ERROR DELETE USER | ERROR: {e}")
        
            return JsonResponse({
                "code": 400,
                "error": str(e) 
            })
    
    return redirect("accounts")

def check_user(request):
    try:
        if request.method == "POST":

            body = json.loads(request.body)
            print("\n\n --------------------------------------- BODY --------------------------------------- ")
            print(body)

            username = body["username"]
            validEmail = validar_email(email=username)
            if validEmail == False:
                return JsonResponse({
                    "code": 200,
                    "msg": "email invalid",
                    "validEmail": validEmail
                })

            query_user = customuser.objects.all().filter(
                email = username
            )
            print("\n\n --------------------------------------- query_user --------------------------------------- ")
            print(query_user)


            if(len(query_user) > 0):
                return JsonResponse({
                    "code": 203,
                    "msg": "este e-mail já foi cadastrado",
                    "validEmail": False
                })

            return JsonResponse({
                "code": 200,
                "msg": "success",
                "validEmail": True
            })
        
        return JsonResponse({
            "code": 400,
            "msg": "no-content",
            "validEmail": False
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": str(e)
        })

def manager_users(request):
    try:
        
        if request.method == "GET":

            query_users = customuser.objects.all().order_by("email") # "sector"
            data = list()
            for user in query_users:
                value = {
                    "id": user.pk,
                    "last_login": user.last_login,
                    "is_superuser": user.is_superuser,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined,
                    "sector": user.sector,
                    "sessao_atividades": user.sessao_atividades,
                    "sessao_relatorios": user.sessao_relatorios,
                    "sessao_imposto_de_renda": user.sessao_imposto_de_renda,
                    "sessao_config_users": user.sessao_config_users,
                }
                data.append(value)

            return JsonResponse({
                "code": 200,
                "msg": "success",
                "data": data
            })
        
        elif request.method == "POST":

            # ------------------------------------------------------------------------------------------------------------
            # ------------------------ retorna informações do usuáro em edit register (edit user) ------------------------
            # ------------------------------------------------------------------------------------------------------------

            body = json.loads(request.body)
            user_id = body["user_id"]

            query_user = customuser.objects.get(pk=user_id)
            data = {
                "id": query_user.pk,
                "password": query_user.password,
                "last_login": query_user.last_login,
                "is_superuser": query_user.is_superuser,
                "username": query_user.username,
                "first_name": query_user.first_name,
                "last_name": query_user.last_name,
                "email": query_user.email,
                "is_staff": query_user.is_staff,
                "is_active": query_user.is_active,
                "date_joined": query_user.date_joined,
                "sector": query_user.sector,
                "sessao_atividades": query_user.sessao_atividades,
                "sessao_relatorios": query_user.sessao_relatorios,
                "sessao_imposto_de_renda": query_user.sessao_imposto_de_renda,
                "sessao_config_users": query_user.sessao_config_users,
            }
            return JsonResponse({
                "code": 200,
                "msg": "success",
                "data": data
            })
        
        elif request.method == "PATCH":
            data = json.loads(request.body)
            user_id     = data["user_id"]
            field_name  = data["field_name"]
            value       = data["value"]

            print(json.dumps(data, indent=4))
          
            user = customuser.objects.get(pk=user_id)
            customuser.objects.filter(pk=user_id).update(**{field_name : value})
            
            return JsonResponse({
                "code": 200,
                "msg": "success",
            })
        
        return JsonResponse({
            "code": 400,
            "msg": "no-content",
            "validEmail": False
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": str(e)
        })



@login_required
def home(request):

    pk = request.user.pk
    user = User.objects.all().filter(pk=pk)
    print(len(user))

    print(user[0].is_superuser)

    
    if request.method == "GET":
        context = {
            "get_all_companies": True,
            "url_get_all_companies": configs["base_url"]["url_get_all_companies"],
            "url_update_company_code_JB": configs["base_url"]["url_update_company_code_JB"],
        }
        return render(request, "app/home.html", context=context)

@login_required
def deliveries_IR(request):
    if request.method == "GET":
        context = {
            "get_all_companies": False,
            "url_get_all_companies": configs["base_url"]["url_get_all_companies"],
            "url_update_lote_IR": configs["base_url"]["url_update_lote_IR"]
        }
        return render(request, "app/deliveries_IR.html", context=context)
    elif request.method == "POST":
        try:

            print("\n\n -------------------- DATA UPDATE IR -------------------- ")
            data = json.loads(request.body)
            print(data)

            data_cod_sistema = data["cod_sistema"]
            data_valor_valor_ano_atual = data["valor_ano_atual"]

            # ------------------- ATUALIZAÇÃO DOS VALORES DE cod_sistema NA TABELA DE CLIENTE DO IMPORTO DE RENDA -------------------

            update_at = datetime.now() - timedelta(hours=3)
            for k,v in data_cod_sistema.items():
                db = Model_tb_clients.objects.get(pk=k)
                db.cod_sistema = v
                db.update_at = update_at
                db.save()
                print(f"""
                    --------------- aletrações salvas ---------------
                    {k}: {v}
                """)

            # ------------------- ATUALIZAÇÃO DOS VALORES DE valor_ano_atual NA TABELA DE IMPORTO DE RENDA -------------------

            for k,v in data_valor_valor_ano_atual.items():
                db = Model_tb_imposto_de_renda.objects.get(pk=k)
                db.valor_ano_atual = v
                db.update_at = update_at
                db.save()
                print(f"""
                    --------------- aletrações salvas | {k} ---------------
                    {k}: {v}
                """)
                

            return JsonResponse({
                "code": 200,
                "mag": "success"
            })
        except Exception as e:
            return JsonResponse({
                "code": 400,
                "error": str(e)
            })


@login_required
def clients(request):
    if request.method == "GET":
        context = {
            "get_all_companies": False,
            "url_get_all_companies": configs["base_url"]["url_get_all_companies"]
        }
        return render(request, "app/clients.html", context=context)

@login_required
def configuracoes(request):
    if request.method == "GET":
        context = {
            "get_all_companies": True,
            "url_get_all_companies": configs["base_url"]["url_get_all_companies"]
        }
        return render(request, "app/configurations.html", context=context)

def get_all_companies():
    data_apont_hours = list()
    data = Model_tb_apontamento_horas_matriz.objects.all().order_by("data_apont", "razao_social")
    for row in data:
        if row.tempo == "-":
            class_row = "apont-pending"
            class_row_btn_check = ""
        else:
            class_row = "apont-done"
            class_row_btn_check = "active"


        razao_social_aux = row.razao_social
        regime_aux = row.regime
        if (len(razao_social_aux) >= 24):
            razao_social_aux = razao_social_aux[:24] + "..."
        if (len(regime_aux) >= 24):
            regime_aux = regime_aux[:24] + "..."

        data_apont_hours.append({
            "id": str(row.pk),
            "data_apont": row.data_apont,
            "horario_inicio": row.horario_inicio,
            "horario_fim": row.horario_fim,
            "competencia": row.competencia,
            "codigo_empresa": str(row.codigo_empresa),
            "razao_social": row.razao_social,
            "razao_social_aux": razao_social_aux,
            "atividade": row.atividade,
            "observacao": row.observacao,
            "username": row.username,
            "setor": row.setor,
            "mes": row.mes,
            "ano": str(row.ano),
            "tempo": row.tempo,
            "regime": row.regime,
            "regime_agrup": row.regime_agrup,
            "regime_aux": regime_aux,
            "tipo_empresa": row.tipo_empresa,
            "class_row": class_row,
            "class_row_btn_check": class_row_btn_check,
        })
    print("\n\n --------------------- DATA GET | data_apont_hours --------------------- ")
    df = pd.DataFrame(data_apont_hours)
    
    df["DT_APONT"] = df["data_apont"]
    for i in df.index:
        dt = df["data_apont"][i]
        horario_inicio = df["horario_inicio"][i]
        df["DT_APONT"][i] = f"{dt} {horario_inicio}:00"
        
        print(f"""
        -------------------------
        >>>> dt: {df["DT_APONT"][i]}
        """)


    df["DT_APONT"] = pd.to_datetime(df["DT_APONT"], format="%d/%m/%Y %H:%M:%S")

    df.sort_values(by=["DT_APONT", "razao_social"], ascending=False, inplace=True)
    df.index = list(range(0, len(df.index)))
    print(df)
    print(df.info())

    data_apont_hours = list()
    for i in df.index:
        data_apont_hours.append({
            "id": df["id"][i],
            "data_apont": df["data_apont"][i],
            "horario_inicio": df["horario_inicio"][i],
            "horario_fim": df["horario_fim"][i],
            "competencia": df["competencia"][i],
            "codigo_empresa": df["codigo_empresa"][i],
            "razao_social": df["razao_social"][i],
            "razao_social_aux": df["razao_social_aux"][i],
            "atividade": df["atividade"][i],
            "observacao": df["observacao"][i],
            "username": df["username"][i],
            "setor": df["setor"][i],
            "mes": df["mes"][i],
            "ano": df["ano"][i],
            "tempo": df["tempo"][i],
            "regime": df["regime"][i],
            "regime_aux": df["regime_aux"][i],
            "regime_agrup": df["regime_agrup"][i],
            "tipo_empresa": df["tipo_empresa"][i],
            "class_row": df["class_row"][i],
            "class_row_btn_check": df["class_row_btn_check"][i],
        })
    return data_apont_hours

@login_required
def apont_hours(request):
    if request.method == "GET":
        data_apont_hours = list()
        today = datetime.now().strftime("%Y-%m-%d")
        data_apont_hours = get_all_companies()
        context = {
            "today": today,
            "get_all_companies": True,
            "url_get_all_companies": configs["base_url"]["url_get_all_companies"],
            "data_apont_hours": data_apont_hours,
        }
        return render(request, "apont_hours/apont_hours.html", context=context)
    elif request.method == "POST":

        print("\n\n\n ------------- BODY POST ------------- ")


        body = json.loads(request.body)
        username_pk = body["username_pk"]
        username_name = body["username_name"]
        date_init = body["date_init"]
        hour_init = body["hour_init"]
        hour_final = body["hour_final"]
        competencia = body["competencia"]
        company_name = body["company_name"]
        activity = body["activity"]
        username_db = User.objects.all().filter(pk=username_pk)[0].email
        id_acessorias = company_name.split("] -")[0].replace("[", "").strip()

        db_temp = connections["db_gaulke_contabil"]
        with db_temp.cursor() as cursor:
            cols_name = ["id_acessorias", "razao_social", "regime"]
            comand_query = f'SELECT {",".join(cols_name)} FROM all_companies WHERE id_acessorias = "{id_acessorias}";'
            print(comand_query)
            cursor.execute(comand_query)
            rows = cursor.fetchall()

            df_company = PrepareData().convert_query_to_dataframe(data=rows, cols_name=cols_name)
            print(df_company)
            print(df_company.info())

        user_info = Model_tb_users.objects.all().filter(
            email = int(username_pk)
        )
        print(" ---------------------- user_info ---------------------- ")
        print(user_info)
        username_name = user_info[0].full_name
        setor = user_info[0].sector

        data_create_apont = PrepareData().prepare_data_to_create_new_apont_hour(
            username_pk,
            date_init=date_init, hour_init=hour_init, hour_final=hour_final,
            atividade=activity, setor=setor, competencia=competencia, username=username_name,
            df_company=df_company)
        
        print(json.dumps(data_create_apont, indent=4))

        if data_create_apont["code"] == 200:
            db = Model_tb_apontamento_horas_matriz()
            db.data_apont = data_create_apont["data_apont"]
            db.horario_inicio = data_create_apont["horario_inicio"]
            db.horario_fim = data_create_apont["horario_fim"]
            db.competencia = data_create_apont["competencia"]
            db.codigo_empresa = data_create_apont["codigo_empresa"]
            db.razao_social = data_create_apont["razao_social"]
            db.atividade = data_create_apont["atividade"]
            db.observacao = data_create_apont["observacao"]
            db.username = data_create_apont["username"]
            db.setor = data_create_apont["setor"]
            db.mes = data_create_apont["mes"]
            db.ano = data_create_apont["ano"]
            db.tempo = data_create_apont["tempo"]
            db.regime = data_create_apont["regime"]
            db.regime_agrup = data_create_apont["regime_agrup"]
            db.tipo_empresa = data_create_apont["tipo_empresa"]
            db.save()
            
            today = datetime.now().strftime("%Y-%m-%d")
            data_apont_hours = get_all_companies()
            context = {
                "today": today,
                "code": 200,
                "data_apont_hours": data_apont_hours,
            }
            return JsonResponse(context)
        else:
            return JsonResponse(data_create_apont)
    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            db = Model_tb_apontamento_horas_matriz.objects.get(pk=data["id"])
            if db is not None:
                db.delete()
            
            print(f"""
                data: {data}
            """)
            return JsonResponse({
                "code": 200,
                "msg": "success"
            })
        except Exception as e:
            print(f"\n\n #### ERROR DELETE APONT HOUR | ERROR: {e}")
            return JsonResponse({
                "code": 400,
                "msg": "error delete"
            })
    elif request.method == "PATCH":
        try:
            data = json.loads(request.body)

            id          = data["id"]
            field_name  = data["field_name"]
            db = Model_tb_apontamento_horas_matriz.objects.get(pk=id)

            if field_name == "observacao":

                observacao   = data["observacao"]
                db.observacao = observacao
                db.save()
                return JsonResponse({
                    "code": 200,
                    "mgs": "success update obsavations apont hours"
                })
            
            elif field_name == "final_hour":
                init_hour   = data["init_hour"]
                final_hour  = data["final_hour"]

                if final_hour == "":
                    db.tempo = "-"
                    db.horario_fim = ""
                    db.save()

                    today = datetime.now().strftime("%Y-%m-%d")
                    context = {
                        "code": 200,
                        "msg": "success",
                        "calc_apont_hour": "",
                        "class_effect": "apont-pending",
                        "class_row_btn_check": "",
                    }
                    return JsonResponse(context)
                
                _dt_init    = datetime.strptime(f"{db.data_apont} {init_hour}:00", "%d/%m/%Y %H:%M:%S")
                _dt_final   = datetime.strptime(f"{db.data_apont} {final_hour}:00", "%d/%m/%Y %H:%M:%S")
                
                if _dt_final >= _dt_init:
                    calc_apont_hour = _dt_final - _dt_init
                    calc_apont_hour = PrepareData().segundos_para_tempo(calc_apont_hour.seconds)
                    db.horario_fim = final_hour
                    db.tempo = calc_apont_hour
                    db.save()
                    print(" ----------------- SUCCESS UPDATE TIME FINAL VALUES ----------------- ")
                    print(f"""
                        >> _dt_init: {_dt_init}
                        >> _dt_final: {_dt_final}
                        >> calc_apont_hour: {calc_apont_hour}
                    """)
                    today = datetime.now().strftime("%Y-%m-%d")
                    context = {
                        "code": 200,
                        "calc_apont_hour": calc_apont_hour,
                        "class_effect": "apont-done",
                        "class_row_btn_check": "active",
                    }
                    return JsonResponse(context)
                
            return JsonResponse({
                "code": 204,
                "msg": "no-content",
                "class_effect": "apont-pending",
                "class_row_btn_check": "",
                "calc_apont_hour": "",
            })
        except Exception as e:
            print(f"\n\n #### ERROR UPDATE APONT HOUR | ERROR: {e}")
            return JsonResponse({
                "code": 500,
                "msg": "error delete"
            })

@login_required
def apont_hours_new_subtask(request):
    body = json.loads(request.body)
    print("\n\n -------------------------- body -------------------------- ")
    print(body)

    _id_task    = body["id_task"]
    _user       = body["user"]
    _date       = body["date"]
    _datetime   = body["datetime"]
    _month      = body["month"]
    _year       = body["year"]
    print(f"""
        ------------------------
        _user: {_user}
        _id_task: {_id_task}
        _date: {_date}
        _datetime: {_datetime}
    """)

    # -------------------------------------
    q_apont_hour = Model_tb_apontamento_horas_matriz.objects.get(
        pk=_id_task
    )
    print(q_apont_hour)
    # -------------------------------------
    q_user = Model_tb_users.objects.get(
        pk=_user
    )
    print(q_user)


    task            = _id_task
    data_apont      = _date  
    horario_inicio  = _datetime
    horario_fim     = ""
    atividade       = ""
    observacao      = ""
    username        = _user,
    setor           = q_user.sector
    mes             = _month      
    ano             =  _year
    tempo           = ""
    regime          = q_apont_hour.regime

    db  = Model_tb_subtasks_apont_horas()
    db.task = task
    db.data_apont = data_apont
    db.horario_inicio = horario_inicio
    db.horario_fim = horario_fim
    db.atividade = atividade
    db.observacao = observacao
    db.username = _user
    db.setor = setor
    db.mes = mes
    db.ano = ano
    db.tempo = tempo
    db.regime = regime
    db.save()

    print(f"""
        >>>> task: {task}
        >>>> data_apont: {data_apont}
        >>>> horario_inicio: {horario_inicio}
        >>>> horario_fim: {horario_fim}
        >>>> atividade: {atividade}
        >>>> observacao: {observacao}
        >>>> username: {_user} | {type(_user)}
        >>>> setor: {setor}
        >>>> mes: {mes}
        >>>> ano: {ano}
        >>>> tempo: {tempo}
        >>>> regime: {regime} 
    """)

    return JsonResponse({
        "code": 200,
        "msg": "success"
    })


@login_required    
def get_info_apont_hour(request):
    if request.method == "POST":
        id_row = json.loads(request.body)["id"]
        data = Model_tb_apontamento_horas_matriz.objects.all().filter(pk=id_row)
        data = {
            "username": data[0].username,
            "setor": data[0].setor,
            "codigo_empresa": data[0].codigo_empresa,
            "razao_social": data[0].razao_social,
            "regime": data[0].regime,
            "data_apont": data[0].data_apont,
            "horario_inicio": data[0].horario_inicio,
            "horario_fim": data[0].horario_fim,
            "atividade": data[0].atividade,
            "competencia": data[0].competencia,
            "observacao": data[0].observacao,
        }
        return JsonResponse({
            "code": 200,
            "data": data,
        })
    else:
        return JsonResponse({
            "code": 400,
            "msg": "bad request"
        })


@login_required
def report_01(request):
    if request.method == "GET":
        context = {
            "url_get_report_1": configs["base_url"]["url_get_report_1"]
        }
        return render(request, "reports/report_01.html", context=context)




# ------------------------------------------------------------------------------- IMPORTS JB -------------------------------------------------------------------------------
@login_required
def imports_JB(request):
    """
        return: template com opções de automações Gaulke Contábil x JB Software
    """
    if request.method == "GET":
        context = {
            "get_all_companies": True,
            "url_get_all_companies": configs["base_url"]["url_get_all_companies"],
            "url_update_company_code_JB": configs["base_url"]["url_update_company_code_JB"],
        }
        return render(request, "imports_JB/imports.html", context=context)

@login_required
def post_file_to_import_JB(request):
    """
        return: json com dados processados de extratos bancários, contas a pagar/receber e demais processos do setor contábil.
    """
    try:
        if request.method == "POST":
            import_model = request.POST.get("import_model")
            modelo = None
            data_import_JB = None
            inputs_visible = []
            grupo_lancamento = request.POST.get("grupo_lancamento")
            session_company_code = request.POST.get("session_company_code")
            
            print(request.POST)
            print(request.FILES)

            code_process = 400
            if import_model == "#1.1 Folha de Pagamento":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_pdf_relacao_folha_por_empregado(file=file, grupo_lancamento=grupo_lancamento, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "date_lancamento", "account_code_credit", "account_code_debit"]
                code_process = 200
            # ----
            elif import_model == "#1.2 Relação GNRE":
                file = request.FILES.get("file_1")
                
                db_temp = connections["db_autonations_v1"]
                with db_temp.cursor() as cursor:
                    cursor.execute(f'SELECT * FROM app_payroll_relation_modelcontasgnre_estados_x_contas;')
                    rows = cursor.fetchall()

                    data_contas = dict()
                    for data in rows:
                        data_contas.update(
                            {
                                data[1]:{
                                    "conta_credito": data[2],
                                    "conta_debito": data[3],
                            }
                        })

                data_import_JB = ConvertToDataFrame.read_xlsx_relacao_gnre(file=file, data_contas=data_contas, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial"]
                code_process = 200
            # ----
            elif import_model == "#1.3 Entrada Tít. Desc. Sicoob":
                file = request.FILES.get("file_1")
                
                data_import_JB = ConvertToDataFrame.read_pdf_relacao_entrada_titulos_desc_sicoob(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial"]
                code_process = 200
            # ----
            elif import_model == "#1.4 Liquidação Tít. Desc. Sicoob":
                file = request.FILES.get("file_1")
                file_2 = request.FILES.get("file_2")
                
                data_import_JB = ConvertToDataFrame.read_pdf_relacao_liquidacao_titulos_desc_sicoob(file=file, file_2=file_2, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_debit"]
                code_process = 200
            
            # ------------------------------------------------------------------------------------------------------------------------------------
            # ---------------------------------------------------------- CONTAS A PAGAR ----------------------------------------------------------
            # ------------------------------------------------------------------------------------------------------------------------------------

            elif import_model == "#2.1 Cobranças Pagas (WBTelecom)":
                file = request.FILES.get("file_1")
                
                data_import_JB = ConvertToDataFrame.read_xlsx_relacao_cobrancas_pagas(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial","account_code_debit","account_code_credit","account_code_debit_juros","account_code_credit_desconto"]
                code_process = 200
            # ----
            elif import_model == "#2.2 Relação Decorise":
                file = request.FILES.get("file_1")
                
                data_import_JB = ConvertToDataFrame.read_xlsx_decorise(file=file, grupo_lancamento=grupo_lancamento, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit", "code_debit_recebivel", "code_debit_comissao"]
                code_process = 200
            # ----
            elif import_model == "#2.3 Arão dos Santos":
                file = request.FILES.get("file_1")
                file_2 = request.FILES.get("file_2")
                modelo = request.POST.get("modelo")
                
                data_import_JB = ConvertToDataFrame.read_xlsx_arao_dos_santos(file_consulta=file, file_contabil=file_2, modelo=modelo, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_debit"]
                code_process = 200
            # ----
            elif import_model == "#2.4 Grupo DAB":
                file = request.FILES.get("file_1")
                file_2 = request.FILES.get("file_2")
                
                data_import_JB = ConvertToDataFrame.read_xls_comprovante_grupo_DAB(file_suppliers=file, file_payments=file_2, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#2.5 Ponto Certo":
                file = request.FILES.get("file_1")
                file_2 = request.FILES.get("file_2")
                
                data_import_JB = ConvertToDataFrame.read_xlsx_contas_a_pagar_PONTO_CERTO(file=file, file_2=file_2, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#2.6 Grupo Garra":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_xlsx_contas_a_pagar_GARRA(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#2.7 TELL":
                file = request.FILES.get("file_1")
                
                data_import_JB = ConvertToDataFrame.read_xlsx_contas_a_pagar_TELL(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            
            # ------------------------------------------------------------------------------------------------------------------------------------
            # --------------------------------------------------------- CONTAS A RECEBER ---------------------------------------------------------
            # ------------------------------------------------------------------------------------------------------------------------------------

            elif import_model == "#3.1 Inova":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_xlsx_contas_a_receber_INOVA(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_debit"]
                code_process = 200
            # ----
            elif import_model == "#3.2 TELL":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_xlsx_contas_a_receber_TELL(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_debit"]
                code_process = 200

            # ------------------------------------------------------------------------------------------------------------------------------------
            # ---------------------------------------------------- COMPROVANTES DE PAGAMENTOS ----------------------------------------------------
            # ------------------------------------------------------------------------------------------------------------------------------------

            elif import_model == "#4.1 Banco do Brasil":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_pdf_comprovante_banco_do_brasil_v2(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit", "account_code_debit"]
                code_process = 200
            elif import_model == "#4.2 Bradesco":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_pdf_comprovante_banco_bradesco(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#4.3 Sicredi":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_pdf_comprovante_banco_sicredi(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#4.4 Sicoob":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_pdf_comprovante_banco_sicoob(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#4.5 Itaú":
                file = request.FILES.get("file_1")
                modelo = request.POST.get("modelo")
                
                if modelo == "modelo_1":
                    data_import_JB = ConvertToDataFrame.read_pdf_comprovante_banco_itau(file=file, company_session=session_company_code)
                elif modelo == "modelo_2":
                    data_import_JB = ConvertToDataFrame.read_xls_comprovante_banco_itau(file=file, company_session=session_company_code)

                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#4.6 Civia":
                file = request.FILES.get("file_1")
                data_import_JB = ConvertToDataFrame.read_pdf_comprovante_banco_civia(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200
            # ----
            elif import_model == "#4.7 Abbraccio":
                file = request.FILES
                print("\n\n ------------------- file ------------------- ")
                print(file)
                print(" ------------------------------------------------ \n\n")
                data_import_JB = ConvertToDataFrame.read_pdf_contas_a_pagar_ABBRACCIO(file=file, company_session=session_company_code)
                data_import_JB = data_import_JB["data_table"]
                inputs_visible = ["filial", "account_code_credit"]
                code_process = 200


            
            print(f"""
                --------------------------------------------------------------------------------------------
                >>>> import_model (model import): {import_model}
                >>>> modelo (input select): {modelo}
                >>>> session_company_code: {session_company_code}
                >>>> grupo_lancamento: {grupo_lancamento}
                >>>> inputs_visible: {inputs_visible}
            """)

            return JsonResponse({
                "code": code_process,
                "msg": "success",
                "data_import_JB": data_import_JB,
                "inputs_visible": inputs_visible,
            })

        else:
            return JsonResponse({
                "code": 501,
                "msg": "unsupported request",
                "error": "501 - unsupported request",
            })
    except Exception as e:
        print(f"\n\n ### ERROR POST FILE TO IMPORT JB | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "bad request",
            "error": str(e)
        })

# ---------------- GET AND POST DATA -- PROCESS FILES TO UPDATE DATA MYSQL ----------------
@login_required
def get_all_data_JB_smart_IR(request):
    """
        return: retorna json com dados dos I.R extraídas do sistema Smart JB Software
    """
    valor_porcent_add = 0.1
    try:
        data = {}
        data_pend_IR = {}
        data_filters = {
            "ano": ["Todos"],
            "dificuldade": ["Todos"],
            "status_smart_IR": ["Todos"],
            "status_pagamento": ["Todos"],
            "forma_pagamento": ["Todos"],
        }
        dados = Model_tb_imposto_de_renda.objects.select_related('client').all().order_by("client__contribuinte")
        cont = 0
        tt_pend = 0
        for dado in dados:

            if dado.ano not in data_filters["ano"]:
                if dado.ano != "":
                    data_filters["ano"].append(dado.ano)
            if dado.dificuldade not in data_filters["dificuldade"]:
                if dado.dificuldade != "":
                    data_filters["dificuldade"].append(dado.dificuldade)
            
            if dado.status_smart_IR not in data_filters["status_smart_IR"]:
                if dado.status_smart_IR != "":
                    data_filters["status_smart_IR"].append(dado.status_smart_IR)
            
            if dado.status_pagamento_IR not in data_filters["status_pagamento"]:
                if dado.status_pagamento_IR != "":
                    data_filters["status_pagamento"].append(dado.status_pagamento_IR)
            
            if dado.info_forma_pagamento not in data_filters["forma_pagamento"]:
                if dado.info_forma_pagamento != "":
                    data_filters["forma_pagamento"].append(dado.info_forma_pagamento)
                        
            valor_ano_anterior = dado.valor_ano_anterior
            valor_ano_atual = dado.valor_ano_atual

            value = {
                "id_table_CLIENT": dado.client.pk,
                "id_table_IR": dado.pk,
                "cod_sistema": dado.client.cod_sistema,
                "contribuinte": dado.client.contribuinte,
                "cpf_cnpj": dado.client.cpf_cnpj,
                "celular": dado.client.celular,
                "telefone": dado.client.telefone,
                "ano": dado.ano,
                "status_smart_IR": dado.status_smart_IR,
                "dificuldade": dado.dificuldade,
                "valor_ano_anterior": valor_ano_anterior,
                "valor_ano_atual": valor_ano_atual,
                "situacao_ano_anterior": dado.situacao_ano_anterior,
                "status_pagamento_IR": dado.status_pagamento_IR,
                "dt_pagamento_IR": dado.dt_pagamento_IR,
            }

            pend_valor_atual = False
            if valor_ano_anterior == "" or None and valor_ano_atual == "" or None:
                pend_valor_atual = True
            
            if valor_ano_anterior != "" and valor_ano_atual == "":
                valor_ano_anterior_aux = float(valor_ano_anterior.replace(".", "").replace(",", "."))
                calc_valor_atual_aux = str(round(valor_ano_anterior_aux + (valor_ano_anterior_aux * valor_porcent_add), 2))
                if calc_valor_atual_aux == "0":
                    calc_valor_atual_aux = "0,00"
                elif calc_valor_atual_aux[len(calc_valor_atual_aux)-2:len(calc_valor_atual_aux)-1] == ".":
                    calc_valor_atual_aux = f"{calc_valor_atual_aux}0".replace(".", ",")
                value["valor_ano_atual"] = calc_valor_atual_aux
                # print(f"\n ------------------------------- CPF: {dado.client.cpf_cnpj} | ID: {dado.pk}")
                # print(valor_ano_anterior, " | ", calc_valor_atual_aux)



            if dado.client.cod_sistema == "" or None or pend_valor_atual == True:
                tt_pend += 1
                data_pend_IR.update({tt_pend: value})
                print(f"""
                ----------------------------------
                >>>> pendência identificada: {dado.pk} | {dado.client.contribuinte}

                """)
              
            data.update({cont: value})
            cont += 1
        
        print(f"""
            ----------------------------
            Total IR encontrados: {len(dados)}
        """)


        return JsonResponse({
            "code": 200,
            "msg": "success get data",
            "data": data,
            "tt_pend": tt_pend,
            "data_pend_IR": data_pend_IR,
            "data_filters": data_filters,
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "error get data JB SmartIR"
        })

@login_required
def get_all_clients(request):
    """
        return: json com clientes do sistema de I.R
    """
    try:

        data = {}
        obj = Model_tb_clients.objects.all().order_by('contribuinte') # .order_by('-contribuinte')
        # print(obj)

        cont = 0
        for i in obj:
            value = {
                "id_table_client": i.pk,
                "cod_sistema": i.cod_sistema,
                "contribuinte": i.contribuinte,
                "cpf_cnpj": i.cpf_cnpj,
                "celular": i.celular,
                "telefone": i.telefone,
            }
            data.update({cont: value})
            cont += 1

        return JsonResponse({
            "code": 200,
            "msg": "success get data",
            "data": data
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "msg": "error get data JB SmartIR"
        })


@login_required
def post_file_JB_smart_IR(request):

    # -------------------------------------------------------------------------------------------------
    # -------------------------- ARQUIVO DE IMPOSTO DE RENDA - BASE SMART IR --------------------------
    # -------------------------------------------------------------------------------------------------

    file = request.FILES.get("file")
    print(file)
    ano_base_migracao_IR = 2023
    try:
        df = PrepareData().convert_xlsx_to_DataFrame(file=file)
        df["Ano"] = list(map(lambda x: int(x), df["Ano"].values))
        df = df[df["Ano"] >= ano_base_migracao_IR]
        print(df)
        print(df.info())
        
        if df is not None:

            try:
                update_clients = update_cliente_dataframe(dataframe=df)
                # print(update_clients)

                return update_clients
            except Exception as e:
                print(f"\n\n #### ERROR UPDATE BASE SMART IR JB | ERROR: {e}")
                print(e)
                return JsonResponse({
                    "code": 400,
                    "msg": "error process update I.R"
                })
        
        return JsonResponse({
            "code": 400,
            "msg": "error convert_xlsx_to_DataFrame"
        })
    except Exception as e:
        return JsonResponse({
            "code": 400,
            "msg": "error process DataFrame Smart IR JBSoftware"
        })

@login_required
def post_file_grid_declaracoes(request):
    file = request.FILES.get("file")
    try:
        df = PrepareData().convert_csv_to_DataFrame(file=file)
        print(df)
        if df is not None:

            update_data = update_IR_consulta_declaracoes_dataframe(dataframe=df)
            print(update_data)

            return update_data
        
        return JsonResponse({
            "code": 400,
            "msg": "error process DataFrame"
        })
    except Exception as e:
        return JsonResponse({
            "code": 400,
            "msg": "error process DataFrame"
        })
 
def update_cliente_dataframe(dataframe):
    try:
        for i in dataframe.index:
            print(f" >> ID: {i}")
            cpf             = str(dataframe["CPF"][i])
            contribuinte    = str(dataframe["Contribuinte"][i])
            celular         = str(dataframe["Celular"][i])
            telefone        = str(dataframe["Telefone"][i])
            # ----
            ano                     = str(dataframe["Ano"][i])
            status_smart_IR         = str(dataframe["Status SmartIR"][i])
            dificuldade             = str(dataframe["Dificuldade"][i])

            q_client = Model_tb_clients.objects.filter(cpf_cnpj=cpf)
            dt = datetime.now(tz=tz.gettz("America/Sao Paulo"))
            dt = timezone.make_aware(dt)
            print(f"""
                ----------------------------
                tt: {len(q_client)}
                ----------------------------
                cpf_cnpj: {cpf}
                contribuinte: {contribuinte}
                telefone: {telefone}
                celular: {celular}
                ano: {ano}
                status_smart_IR: {status_smart_IR}
                dificuldade: {dificuldade}
                dt: {dt} | {type(dt)}
            """)

            
            # ----------------------------------------------------------------------------------------------------------------------- UPDATE / CREATE CLIENT
            if len(q_client) == 1:

                q_client.update(
                    cpf_cnpj       = cpf,
                    contribuinte   = contribuinte,
                    telefone       = telefone,
                    celular        = celular,
                    update_at      = dt,
                )
                print(f"Registro atualizado com sucesso | CPF: {cpf}")
            elif len(q_client) == 0:
                Model_tb_clients.objects.create(
                    cpf_cnpj        = cpf,
                    contribuinte    = contribuinte,
                    telefone        = telefone,
                    celular         = celular,
                    created_at      = dt,
                    update_at      = dt,
                )
                print(f"Cliente criado com sucesso | CPF: {cpf}")

            # ----------------------------------------------------------------------------------------------------------------------- UPDATE / CREATE I.R
            q_client = Model_tb_clients.objects.get(cpf_cnpj=cpf)
            q_IR = Model_tb_imposto_de_renda.objects.filter(client=q_client, ano=ano)
            if len(q_IR) == 1:
                q_IR.update(
                    ano                     = ano,
                    status_smart_IR         = status_smart_IR,
                    dificuldade             = dificuldade,
                    update_at               = dt,
                )
                print(f"Registro I.R atualizado com sucesso | CPF: {cpf}")
            elif len(q_IR) == 0:
                Model_tb_imposto_de_renda.objects.create(
                    client                  = q_client,
                    ano                     = ano,
                    status_smart_IR         = status_smart_IR,
                    dificuldade             = dificuldade,
                    created_at              = dt,
                    update_at               = dt,
                )
                print(f"I.R criado com sucesso | CPF: {cpf}")
        
        return JsonResponse({
            "code": 200,
            "msg": "SUCCESS UPDATE CLIENTS LOTE"
        })

    except Exception as e:
        print(f" ### ERROR UPDATE CLIENTS LOTE | ERROR: {e}")
        return JsonResponse({
            "code": 500,
            "msg": "ERROR UPDATE CLIENTS LOTE"
        })

# @login_required
def update_IR_consulta_declaracoes_dataframe(dataframe):

    try:
        for i in dataframe.index:
            print(f" >> ID: {i}")
            ano             = str(dataframe[0][i]).replace(".", "")
            status          = str(dataframe[1][i])
            cod_dominio     = str(dataframe[2][i])
            cpf             = str(dataframe[3][i])
            contribuinte    = str(dataframe[4][i])
            valor           = str(dataframe[7][i])

            if valor.count(",") == 0:
                valor = f"{valor},00"
            elif len(valor.split(",")[1]) == 1:
                valor = f"{valor}0"
                        
            q_client = Model_tb_clients.objects.filter(
                cpf_cnpj=cpf)
            if len(q_client) > 0:
                q_IR = Model_tb_imposto_de_renda.objects.filter(
                    client_id=q_client[0].pk,
                    # ano=ano # ----------------------------------------------------------------------->>  verificar o impacto de manter ano no query. Fazer backup e restore.
                    )
                dt = datetime.now(tz=tz.gettz("America/Sao Paulo"))
                dt = timezone.make_aware(dt)
                # print(f"""
                #     ----------------------------
                #     tt: {len(q_IR)}
                #     ----------------------------
                #     ano: {ano}
                #     status: {status}
                #     cod_dominio: {cod_dominio}
                #     cpf: {cpf}
                #     contribuinte: {contribuinte}
                #     valor: {valor}
                # """)


                # -------------------------------------------------------------------------- UPDATE / CREATE CLIENT E I.R
                if len(q_IR) == 1:

                    if status == "PAGO":
                        status_pagamento_IR = "Sim"
                    else:
                        status_pagamento_IR = "Não"

                    q_IR.update(
                        # ano                 = ano,
                        valor_ano_anterior  = valor,
                        status_pagamento_IR = status_pagamento_IR,
                        update_at           = dt,
                    )

                    print(f"Registro IR atualizado com sucesso | CPF: {cpf}")
                    q_client.update(
                        cod_sistema = cod_dominio,
                        update_at   = dt,
                    )
                    print(f"Registro CLIENT atualizado com sucesso | CPF: {cpf}")


            
        
        return JsonResponse({
            "code": 200,
            "msg": "SUCCESS UPDATE IR LOTE"
        })

    except Exception as e:
        print(f" ### ERROR UPDATE IR LOTE | ERROR: {e}")
        return JsonResponse({
            "code": 500,
            "msg": "ERROR UPDATE IR LOTE"
        })

@login_required
def post_create_new_client(request):
    try:
        body = json.loads(request.body)
        # cod_sistema = body["cod_sistema"]
        cpf_cnpj = body["cpf_cnpj"]
        contribuinte = body["contribuinte"]
        telefone = body["telefone"]
        celular = body["celular"]

        q_client = Model_tb_clients.objects.filter(cpf_cnpj=cpf_cnpj)

        print(f"\n\n ---- body ----- ")
        print(body)

        print(f"""
            ----------------------------
            tt: {len(q_client)}
            ----------------------------
            cpf_cnpj: {cpf_cnpj}
            contribuinte: {contribuinte}
            telefone: {telefone}
            celular: {celular}
        """)


        if len(q_client) == 1:

            q_client.update(
                cpf_cnpj       = cpf_cnpj,
                contribuinte   = contribuinte,
                telefone       = telefone,
                celular        = celular,
                update_at      = datetime.now(tz=tz.gettz("America/Sao Paulo")),
            )
            
            return JsonResponse({
                "code": 200,
                "msg": "Registro atualizado com sucesso"
            })

        elif len(q_client) == 0:
            Model_tb_clients.objects.create(
                cpf_cnpj        = cpf_cnpj,
                contribuinte    = contribuinte,
                telefone        = telefone,
                celular         = celular,
            )
            return JsonResponse({
                "code": 200,
                "msg": "Cliente criado com sucesso"
            })

    except Exception as e:
        print(f"\n\n ### ERROR CREATE NEW CLIENT | ERROR: {e} ### ")
        return JsonResponse({
            "code": 200,
            "msg": "success create new client",
            "error": e,
        })

@login_required
def post_create_new_IR(request):
    try:
        body = json.loads(request.body)

        cpf_cnpj                = body["cpf_cnpj"]
        ano                     = body["ano"]
        dificuldade             = body["dificuldade"]
        situacao_ano_anterior   = body["situacao_ano_anterior"]
        valor_ano_anterior      = body["valor_ano_anterior"]
        valor_ano_atual         = body["valor_ano_atual"]
        status_smart_IR         = body["status_smart_IR"]
    


        print(f"\n\n ---- body ----- ")
        print(body)

        print(f"""
            ----------------------------
            cpf_cnpj: {cpf_cnpj} | {type(cpf_cnpj)}
            ano: {ano} | {type(ano)}
            dificuldade: {dificuldade} | {type(dificuldade)}
            status_smart_IR: {status_smart_IR} | {type(status_smart_IR)}
            situacao_ano_anterior: {situacao_ano_anterior} | {type(situacao_ano_anterior)}
            valor_ano_anterior: {valor_ano_anterior} | {type(valor_ano_anterior)}
            valor_ano_atual: {valor_ano_atual} | {type(valor_ano_atual)}
        """)


        try:
            q_client = Model_tb_clients.objects.get(cpf_cnpj=cpf_cnpj)
            print(" ------------------- q_client ------------------- ")
            print(q_client)

            new_IR = Model_tb_imposto_de_renda(
                client=q_client,
                ano=ano,
                status_smart_IR=status_smart_IR,
                dificuldade=dificuldade, 
                valor_ano_anterior=valor_ano_anterior,
                valor_ano_atual=valor_ano_atual,
                situacao_ano_anterior=situacao_ano_anterior,
                created_at=datetime.now(tz=tz.gettz("America/Sao Paulo")),
                update_at=datetime.now(tz=tz.gettz("America/Sao Paulo"))
            )
            new_IR.save()
            print(" -------- new_IR --------")
            print(new_IR)

            return JsonResponse({
                "code": 200,
                "msg": "Registro criado com sucesso"
            })
        except Exception as e:
            print(f"\n\n ### ERRO CREATE NEW IR #01 | ERROR: {e}")
            return JsonResponse({
                "code": 400,
                "msg": "Falha ao criar novo I.R",
                # "error": e,
            })

    except Exception as e:
        print(f"\n\n ### ERROR CREATE NEW IR #02 | ERROR: {e} ### ")
        return JsonResponse({
            "code": 500,
            "msg": "Falha ao criar novo I.R",
            # "error": e,
        })

@login_required
def post_create_new_comment(request):
    try:
        body = json.loads(request.body)

        username    = body["username"]
        id_table_IR = body["id_table_IR"]
        comment     = body["comment"]


        print(f"\n\n ---- body ----- ")
        print(body)

        print(f"""
            ----------------------------
            username: {username}
            id_table_IR: {id_table_IR}
            comment: {comment}
        """)

        obj_IR = Model_tb_imposto_de_renda(pk=id_table_IR)
        new_comment_IR = Model_tb_imposto_de_renda_comments(
                IR=obj_IR,
                username=username,
                comment=comment,
                created_at=datetime.now(tz=tz.gettz("America/Sao Paulo")),
                update_at=datetime.now(tz=tz.gettz("America/Sao Paulo"))
            )
        new_comment_IR.save()

        return JsonResponse({
            "code": 200,
            "msg": "Comentário criado com sucesso"
        })
    except Exception as e:
        print(f"\n\n ### ERROR CREATE COMMENT IR #02 | ERROR: {e} ### ")
        return JsonResponse({
            "code": 500,
            "msg": "Falha ao criar comentário",
        })

@login_required 
def get_comments(request):
    try:
        body = json.loads(request.body)
        id_table_IR = body["id_table_IR"]
        
        print(f"\n\n ---- body ----- ")
        print(body)

        print(f"""
            ----------------------------
            id_table_IR: {id_table_IR}
        """)

        all_comments = Model_tb_imposto_de_renda_comments.objects.all().filter(
            IR=id_table_IR
        )

        data = {}
        for comment in all_comments:
            dt_comment = datetime.strftime(comment.update_at - timedelta(hours=3), "%d/%m/%Y %H:%M:%S")
            value = {
                "id_table_comment_IR": comment.pk,
                "id_table_IR": comment.IR.pk,
                "username": comment.username,
                "comment": comment.comment,
                "dt_comment": dt_comment,
            }
            data.update({comment.pk: value})
            

        print("\n\n ------------- all_comments ------------- ")
        print(all_comments)


        return JsonResponse({
            "code": 200,
            "data": data
        })
    except Exception as e:
        print(f"\n\n ### ERROR GET COMMENTS IR #02 | ERROR: {e} ### ")
        return JsonResponse({
            "code": 500,
            "msg": "Falha ao obter comentários IR",
        })



@login_required
def post_delete_iR(request):
    try:
        body = json.loads(request.body)
        id_table_IR = body["id_table_IR"]

        print(" ----------- post_delete_iR ----------- ")
        print(body)


        Model_tb_imposto_de_renda.objects.get(pk=id_table_IR).delete()
        return JsonResponse({
            "code": 200,
            "msg": "success delete IR"
        }) 
    except Exception as e:
        print(f"\n\n ### ERROR DELETE IR BY id_table_IR | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error delete IR"
        })

@login_required
def post_delete_comment_IR(request):
    try:
        body = json.loads(request.body)
        id_table_comment_IR = body["id_table_comment_IR"]

        print(body)

        Model_tb_imposto_de_renda_comments.objects.get(pk=id_table_comment_IR).delete()
        return JsonResponse({
            "code": 200,
            "msg": "success delete comment IR"
        }) 
    except Exception as e:
        print(f"\n\n ### ERROR DELETE IR BY id_table_comment_IR | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error delete comment"
        })

@login_required
def post_delete_client(request):
    try:
        body = json.loads(request.body)
        id_table_client = body["id_table_client"]
        Model_tb_clients.objects.get(pk=id_table_client).delete()
        return JsonResponse({
            "code": 200,
            "msg": "success delete IR"
        }) 
    except Exception as e:
        print(f"\n\n ### ERROR DELETE IR BY id_table_client | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error delete client"
        })
    


@login_required
def post_edit_value_IR(request):
    try:

        body = json.loads(request.body)
        id_table_IR = body["id_table_IR"].split("-")[-1]
        field_name = body["field_name"]
        value = body["value"]

        print(f"""
            --------------------------
            id_table_IR: {id_table_IR}
            field_name: {field_name}
            value: {value}
        """)

        data = Model_tb_imposto_de_renda.objects.filter(pk=id_table_IR).update(**{
            field_name: value,
            "update_at": datetime.now(tz=tz.gettz("America/Sao Paulo")),
            })
        print(data)

        return JsonResponse({
            "code": 200,
            "msg": "success edit IR"
        }) 
    except Exception as e:
        print(f"\n\n ### ERROR EDIT IR BY id_table_IR | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error edit"
        })

@login_required
def post_edit_comment_IR(request):
    try:

        body = json.loads(request.body)
        id_table_comment_IR = body["id_table_comment_IR"]
        comment = body["comment"]

        print(f"""
            --------------------------
            id_table_comment_IR: {id_table_comment_IR}
            comment: {comment}
        """)

        data = Model_tb_imposto_de_renda_comments.objects.filter(pk=id_table_comment_IR).update(**{
            "comment": comment,
            "update_at": datetime.now(tz=tz.gettz("America/Sao Paulo")),
            })
        print(data)

        return JsonResponse({
            "code": 200,
            "msg": "success edit comment IR"
        }) 
    except Exception as e:
        print(f"\n\n ### ERROR EDIT COMMENT IR BY id_table_comment_IR | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error edit"
        })

@login_required  
def post_edit_value_data_pagamento(request):
    try:

        body = json.loads(request.body)
        print(" ---------------- body ---------------- ")
        print(body)
        id_table_IR         = str(body["id_table_IR"])
        status_pagamento_IR = str(body["status_pagamento_IR"])
        dafault_process = body["dafault_process"]

        update_at = datetime.now(tz=tz.gettz("America/Sao Paulo")).strftime("%Y-%m-%d %H:%M:%S")

        if dafault_process == False:
            if status_pagamento_IR == "Sim":
                dt_pagamento_IR = ""
                info_forma_pagamento = ""
                status_pagamento_IR = "Não"
            else:
                dt_pagamento_IR = str(body["dt_pagamento_IR"])
                info_forma_pagamento = str(body["info_forma_pagamento"])
                status_pagamento_IR = "Sim"
        else:
            dt_pagamento_IR = str(body["dt_pagamento_IR"])
            info_forma_pagamento = str(body["info_forma_pagamento"])


        print(f"""
            --------------------------
            id_table_IR: {id_table_IR}
            status_pagamento_IR: {status_pagamento_IR}
            dt_pagamento_IR: {dt_pagamento_IR}
            info_forma_pagamento: {info_forma_pagamento}
            dafault_process: {dafault_process}
            update_at: {update_at}
        """)

        data = Model_tb_imposto_de_renda.objects.filter(pk=id_table_IR)
        print(data)
        
        data.update(**{
            "status_pagamento_IR": status_pagamento_IR,
            "dt_pagamento_IR": dt_pagamento_IR,
            "info_forma_pagamento": info_forma_pagamento,
            # "update_at": update_at,
            })
        

        return JsonResponse({
            "code": 200,
            "msg": "success edit IR"
        }) 
    except Exception as e:
        print(f"\n\n ### ERROR EDIT IR BY id_table_IR | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error edit"
        })


@login_required
def post_edit_value_client(request):
    try:

        body = json.loads(request.body)
        id_table_client = body["id_table_client"].split("-")[-1]
        field_name = body["field_name"]
        value = body["value"]

        print(f"""
            --------------------------
            id_table_client: {id_table_client}
            field_name: {field_name}
            value: {value}
        """)
        if field_name == "cpf_cnpj":
            q = Model_tb_clients.objects.filter(cpf_cnpj=value)
            if len(q) == 0:
                Model_tb_clients.objects.filter(pk=id_table_client).update(**{
                    field_name: value,
                    "update_at": datetime.now(tz=tz.gettz("America/Sao Paulo")),
                    })
                return JsonResponse({
                    "code": 200,
                    "msg": "success edit client"
                })
            if len(q) == 1 and q[0].cpf_cnpj == value and str(q[0].pk) != id_table_client:
                return JsonResponse({
                    "code": 200,
                    "msg": "error update client"
                })
            else:
                return JsonResponse({
                    "code": 200,
                    "msg": "keep data"
                })

        else:
            Model_tb_clients.objects.filter(pk=id_table_client).update(**{
                field_name: value,
                "update_at": datetime.now(tz=tz.gettz("America/Sao Paulo")),
                })
            return JsonResponse({
                "code": 200,
                "msg": "success edit client"
            }) 
        
    except Exception as e:
        print(f"\n\n ### ERROR EDIT IR BY id_table_client | ERROR: {e}")
        return JsonResponse({
            "code": 400,
            "msg": "error edit"
        })

# ---------------- QUERIESBY FIELD NAME ----------------
@login_required
def post_query_by_field_cod_sistema(request):
    body = json.loads(request.body)
    field_name = body["field_name"]
    data_field = body["data_field"]

    
    print(f"""
        ------------------------
        field_name: {field_name}
        data_field: {data_field}
    """)

    try:

        obj = Model_tb_clients.objects.all().filter(
            cod_sistema=data_field
        ).order_by("contribuinte")

        print(obj)

        check = False
        data = None
        if len(obj) > 0:
            check = True

            # -1 para obter a situação do ano anterior
            data = {
                "cod_sistema": obj[0].cod_sistema,
                "contribuinte": obj[0].contribuinte,
                "cpf_cnpj": obj[0].cpf_cnpj,
                "celular": obj[0].celular,
                "telefone": obj[0].telefone,
            }

        print(" ------- data | check DocNumer ------- ")
        print(json.dumps(data, indent=4))

        return JsonResponse({
            "code": 200,
            "msg": "success get data clients",
            "check": check,
            "data": data,
        })
    except Exception as e:
        print(f"\n\n ### ERROR QUERY BY FIELD NAME | ERROR: {e} ### ")
        return JsonResponse({
            "code": 500,
            "msg": "error query by field | clients"
        })
# ----
@login_required
def post_query_by_cpf(request):
    """
        return dict: Verifica se existe algum cliente cadastrado com o "cpf_cnpj" informado e retornado os dados do cliente.
    """
    body = json.loads(request.body)
    field_name = body["field_name"]
    data_field = body["data_field"]

    
    print(f"""
        ------------------------
        field_name: {field_name}
        data_field: {data_field}
    """)

    try:

        obj = Model_tb_clients.objects.all().filter(
            cpf_cnpj=data_field
        ).order_by("contribuinte")

        print(obj)

        check = False
        data = None
        if len(obj) > 0:
            check = True

            # -1 para obter a situação do ano anterior
            data = {
                "cod_sistema": obj[0].cod_sistema,
                "contribuinte": obj[0].contribuinte,
                "cpf_cnpj": obj[0].cpf_cnpj,
                "celular": obj[0].celular,
                "telefone": obj[0].telefone,
            }

        print(" ------- data | check DocNumer ------- ")
        print(json.dumps(data, indent=4))

        return JsonResponse({
            "code": 200,
            "msg": "success get data clients",
            "check": check,
            "data": data,
        })
    except Exception as e:
        print(f"\n\n ### ERROR QUERY BY FIELD NAME | ERROR: {e} ### ")
        return JsonResponse({
            "code": 500,
            "msg": "error query by field | clients"
        })
