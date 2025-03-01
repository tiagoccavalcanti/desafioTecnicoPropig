from rest_framework import serializers
from .models import Funcionario, Departamento, Group

class FuncionarioSerializer(serializers.ModelSerializer):
    departamento = serializers.PrimaryKeyRelatedField(queryset=Departamento.objects.all())
    grupo = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Funcionario
        fields = ['id', 'email', 'first_name', 'last_name', 'departamento', 'grupo', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        funcionario = Funcionario(**validated_data)

        if password:
            funcionario.set_password(password)

        funcionario.save()

        return funcionario
