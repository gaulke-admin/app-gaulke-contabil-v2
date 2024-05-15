from dateutil import tz
from datetime import datetime

from django.db import models

from django.contrib.auth.models import AbstractUser, Permission

# from django.contrib.auth.models import AbstractUser
# class User(AbstractUser):
#     email_verified = models.BooleanField(default=False)


class Model_tb_clients(models.Model):
    cod_sistema             = models.CharField(max_length=8)
    contribuinte            = models.CharField(max_length=125)
    cpf_cnpj                = models.CharField(max_length=18)
    celular                 = models.CharField(max_length=18)
    telefone                = models.CharField(max_length=18)
    created_at = models.DateTimeField(default=datetime.now(tz=tz.gettz("America/Sao Paulo")))
    update_at = models.DateTimeField(default=datetime.now(tz=tz.gettz("America/Sao Paulo")))

class Model_tb_imposto_de_renda(models.Model):
    client = models.ForeignKey(Model_tb_clients, on_delete=models.CASCADE)
    ano                     = models.CharField(max_length=4)
    status_smart_IR         = models.CharField(max_length=25)
    dificuldade             = models.CharField(max_length=25)
    valor_ano_anterior      = models.CharField(max_length=25)
    valor_ano_atual         = models.CharField(max_length=25)
    situacao_ano_anterior   = models.CharField(max_length=55)
    status_pagamento_IR     = models.CharField(max_length=3)
    dt_pagamento_IR         = models.CharField(max_length=10)
    info_forma_pagamento    = models.CharField(max_length=25)
    created_at = models.DateTimeField(default=datetime.now(tz=tz.gettz("America/Sao Paulo")))
    update_at = models.DateTimeField(default=datetime.now(tz=tz.gettz("America/Sao Paulo")))

class Model_tb_imposto_de_renda_comments(models.Model):
    IR       = models.ForeignKey(Model_tb_imposto_de_renda, on_delete=models.CASCADE)
    username    = models.CharField(max_length=25)
    comment     = models.CharField(max_length=155)
    created_at  = models.DateTimeField(default=datetime.now(tz=tz.gettz("America/Sao Paulo")))
    update_at   = models.DateTimeField(default=datetime.now(tz=tz.gettz("America/Sao Paulo")))

class Model_tb_apontamento_horas_matriz(models.Model):
    data_apont      = models.CharField(max_length=10)  # varchar(10)
    horario_inicio  = models.CharField(max_length=5) # varchar(5)
    horario_fim     = models.CharField(max_length=5) # varchar(5)
    competencia     = models.CharField(max_length=15) # varchar(15)
    codigo_empresa  = models.CharField(max_length=15) # varchar(8)
    razao_social    = models.CharField(max_length=155) # varchar(155)
    atividade       = models.CharField(max_length=25) # varchar(25)
    observacao      = models.CharField(max_length=255) # varchar(255)
    username        = models.CharField(max_length=55) # varchar(55)
    setor           = models.CharField(max_length=15) #varchar(15)
    mes             = models.CharField(max_length=10) # varchar(10)
    ano             = models.SmallIntegerField() # smallint
    tempo           = models.CharField(max_length=18) # varchar(18)
    regime          = models.CharField(max_length=55) # varchar(55)
    regime_agrup    = models.CharField(max_length=55) # varchar(55)
    tipo_empresa    = models.CharField(max_length=25) # varchar(25)

class Model_tb_subtasks_apont_horas(models.Model):

    # campos semelhantes ao apont horas
    # -> servirá para análises independêntes, exemplo:
    # ---> caso atualize o tipo da empresa ou setor do usuário os dados não serão generalizados comprometendo a análise retroativa de seus respectivos objetos.

    task            = models.IntegerField()
    data_apont      = models.CharField(max_length=10)
    horario_inicio  = models.CharField(max_length=5)
    horario_fim     = models.CharField(max_length=5)
    atividade       = models.CharField(max_length=25)
    observacao      = models.CharField(max_length=255)
    username        = models.CharField(max_length=55)
    setor           = models.CharField(max_length=15)
    mes             = models.CharField(max_length=10)
    ano             = models.SmallIntegerField()
    tempo           = models.CharField(max_length=18)
    regime          = models.CharField(max_length=55)

class Model_tb_users(models.Model):
    email           = models.EmailField(max_length=254)
    first_name      = models.CharField(max_length=25)
    full_name       = models.CharField(max_length=155)
    sector          = models.CharField(max_length=55)
    password        = models.CharField(max_length=128)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    # ----
    sessao_atividades = models.SmallIntegerField()
    sessao_relatorios = models.SmallIntegerField()
    sessao_imposto_de_renda = models.SmallIntegerField()




class customuser(AbstractUser):
    # Campos adicionais
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=25, null=True, unique=False, default="-")
    sector = models.CharField(max_length=25)
    sessao_atividades = models.BooleanField(default=False)
    sessao_relatorios = models.BooleanField(default=False)
    sessao_imposto_de_renda = models.BooleanField(default=False)
    sessao_config_users = models.BooleanField(default=False)

    # Adicione outros campos conforme necessário
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_permissions"  # Nome personalizado
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.first_name  # exibe o nome de usuário como representação do objeto
    
