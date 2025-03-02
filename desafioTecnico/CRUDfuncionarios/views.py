from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied

from .models import Departamento, Funcionario
from .serializer import FuncionarioSerializer


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = Funcionario.objects.get(username=username)
    except Funcionario.DoesNotExist:
        return Response({"detail": "user not found"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password) and user.password != password:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


def is_superuser(user):
    return user.grupo and user.grupo.name == 'SUPER'


def is_gestor(user):
    return user.grupo and user.grupo.name == 'GESTOR'


def can_edit_funcionario(user, funcionario):
    if is_superuser(user):
        return True
    if is_gestor(user) and user.departamento == funcionario.departamento:
        return True
    return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_funcionarios(request):
    if request.method == 'GET':
        if is_superuser(request.user):
            funcionarios = Funcionario.objects.all()
        elif is_gestor(request.user):
            funcionarios = Funcionario.objects.filter(departamento=request.user.departamento)
        else:
            raise PermissionDenied("Você não tem permissão para visualizar os funcionários.")

        serializer = FuncionarioSerializer(funcionarios, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def funcionario_manager(request):
    if request.method == 'POST':
        if not (is_superuser(request.user) or is_gestor(request.user)):
            raise PermissionDenied("Você não tem permissão para criar funcionários.")
        
        new_funcionario = request.data
        serializer = FuncionarioSerializer(data=new_funcionario)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        id = request.data['id']
        try:
            updated_funcionario = Funcionario.objects.get(pk=id)
        except Funcionario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not can_edit_funcionario(request.user, updated_funcionario):
            raise PermissionDenied("Você não tem permissão para editar este funcionário.")
        
        serializer = FuncionarioSerializer(updated_funcionario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        id = request.data.get('id')
        if not id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            funcionario_to_delete = Funcionario.objects.get(pk=id)
        except Funcionario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not can_edit_funcionario(request.user, funcionario_to_delete):
            raise PermissionDenied("Você não tem permissão para deletar este funcionário.")

        funcionario_to_delete.delete()
        return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def funcionario_by_id(request, id):
    if request.method == 'GET':
        try:
            funcionario = Funcionario.objects.get(pk=id)
        except Funcionario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = FuncionarioSerializer(funcionario)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            updated_funcionario = Funcionario.objects.get(pk=id)
        except Funcionario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not can_edit_funcionario(request.user, updated_funcionario):
            raise PermissionDenied("Você não tem permissão para editar este funcionário.")
        
        serializer = FuncionarioSerializer(updated_funcionario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            funcionario_to_delete = Funcionario.objects.get(pk=id)
        except Funcionario.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not can_edit_funcionario(request.user, funcionario_to_delete):
            raise PermissionDenied("Você não tem permissão para deletar este funcionário.")

        funcionario_to_delete.delete()
        return Response(status=status.HTTP_202_ACCEPTED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_departamento(request):
    if not is_superuser(request.user):
        raise PermissionDenied("Você não tem permissão para criar departamentos.")
    
    nome = request.data.get('nome')

    if not nome:
        return Response({"detail": "O nome do departamento é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    if Departamento.objects.filter(nome=nome).exists():
        return Response({"detail": "Já existe um departamento com este nome."}, status=status.HTTP_400_BAD_REQUEST)

    departamento = Departamento.objects.create(nome=nome)
    return Response({"id": departamento.id, "nome": departamento.nome}, status=status.HTTP_201_CREATED)