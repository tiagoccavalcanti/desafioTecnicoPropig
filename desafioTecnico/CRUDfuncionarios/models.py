from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Funcionario(AbstractUser):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name="funcionarios")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    grupo = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="funcionarios")
    username = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'departamento']
    
    groups = models.ManyToManyField(Group, related_name="funcionarios_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="funcionarios_permissions", blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.grupo})"