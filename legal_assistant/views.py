# views.py
import os
import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import dotenv
from openai import OpenAI  
from payment.models import Balance
from decimal import Decimal
from django.conf import settings
from .serializers import TemplateDocumentSerializer
REQUEST_FEE = getattr(settings, 'REQUEST_FEE', Decimal('3932.00'))

from .models import ChatDialog, ChatMessage,TemplateDocument

SYSTEM_PROMPT = """
Ты — юридический ассистент, специализирующийся на законодательстве Республики Казахстан. 
    Отвечай строго по действующим нормам гражданского, трудового, семейного и налогового права РК, 
    проверяя актуальность актов исключительно через официальные системы Adilet.zan.kz, Online.zakon.kz, 
    Parlam.kz, портал eGov.kz в разделе «Правовая информация» и сайт Министерства юстиции Казахстана. 
    Используй данные, актуальные на 30 марта 2025 года, не опирайся на нормы других государств. 
    Пиши понятным, юридически точным языком; если информация недоступна, честно сообщай об этом. 
    В ответах не вставляй ссылки на источники, не упоминай, что ты являешься ИИ, и не говори, 
    что не можешь давать юридические советы — предоставляй готовые консультации.
"""
from django.shortcuts import render

def home(request):
    return render(request, "home.html")

@api_view(['POST','OPTIONS'])
@permission_classes([IsAuthenticated])
def chat_message_view(request):
    """
    Пример эндпоинта, где для генерации ответа ассистента используется новая схема:
      client = OpenAI(...)
      client.responses.create(...)
    """
    
    user = request.user
    dialog_id = request.data.get('dialog_id')
    content = request.data.get('content')
    file = request.FILES.get('file')  # если фронт может прислать файл

    # Проверяем входные данные
    if not content and not file:
        return Response(
            {'error': 'Поле "content" или файл обязательно.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Если у вас ключ уже лежит в settings, можно взять его оттуда
    api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
    if not api_key:
        return Response(
            {'error': 'OPENAI_API_KEY не задан в настройках.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Инициализируем клиент OpenAI
    client = OpenAI(api_key=api_key)

    # --- Шаг 1: Создание или получение диалога ---
    if not dialog_id:
        try:
            balance = request.user.balance
        except Balance.DoesNotExist:
            balance = Balance.objects.create(user=request.user)
        if balance.amount < REQUEST_FEE:
            return Response(
                {'detail': 'Недостаточно средств для выполнения запроса'},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )
        balance.deduct(REQUEST_FEE)
        dialog_id = str(uuid.uuid4())  # Если не пришёл, генерируем
        dialog = ChatDialog.objects.create(
            id=dialog_id,
            user=user,
            name="Новый юридический диалог"  # Можно дальше сгенерировать короткое название (см. ниже)
        )
        try:
                response = client.responses.create(
                    model="gpt-4o",                  # Как указано в примере
                    input=f"назави имя диалога  2-5 словом если запрос : {content}",
                    temperature=1,
                    # max_tokens=50,
                )
                dialog.name = response.output_text
                dialog.save()
        except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Пытаемся получить диалог текущего пользователя
        dialog, created = ChatDialog.objects.get_or_create(
        id=dialog_id,
        user=user,
        defaults={'name': 'Новый юридический диалог'}
    )   
        if created:
            try:
                response = client.responses.create(
                    model="gpt-4o",                  # Как указано в примере
                    input=f"назави имя диалога  2-5 словом если запрос : {content}",
                    temperature=1,
                    # max_tokens=50,
                )
                dialog.name = response.output_text
                dialog.save()
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    # --- Шаг 2: Сохраняем сообщение пользователя ---
    user_message = ChatMessage.objects.create(
        id=uuid.uuid4(),
        dialog=dialog,
        user=user,
        role='user',
        content=content if content else ''
    )
    if file:
        user_message.file = file
        user_message.save()

    # --- Шаг 3: Формируем «промпт» для нового API ---
    # Здесь нет разделения на `role: user/assistant/system` — 
    # вы можете склеить всё в одну строку (или несколько), либо 
    # как-то иначе формировать текст, который вы отправите в `input`.
    # Обязательно добавляем ключ "type": "web_search_preview" в `tools`.

    # 3.1 Склеиваем system-промпт + историю диалога
    # Например, делаем общий текст. 
    # (Можно изощрённее форматировать, например, "System:\n..., User:\n..., Assistant:\n...".)
    conversation_text = "СИСТЕМНОЕ СООБЩЕНИЕ:\n" + SYSTEM_PROMPT + "\n\n"

    messages_in_db = dialog.messages.order_by('created_at')
    for msg in messages_in_db:
        if msg.role == 'user':
            conversation_text += f"ПОЛЬЗОВАТЕЛЬ:\n{msg.content}\n\n"
        else:
            conversation_text += f"АССИСТЕНТ:\n{msg.content}\n\n"

    try:
        response = client.responses.create(
            model="gpt-4o",                  # Как указано в примере
            input=conversation_text,         # Весь «промпт» — включая системное сообщение и историю
            tools=[{"type": "web_search_preview","domains": [
            "adilet.zan.kz",
            "online.zakon.kz",
            "parlam.kz",
            "egov.kz",
            "gov.kz"
        ],}],
            temperature=0.7,
            # max_tokens=1000,
        )
        
        assistant_text = response.output_text
        if not assistant_text:
            assistant_text = "Техниеские не поладки обратитесь в поддежку."
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- Шаг 4: Сохраняем ответ ассистента ---
    assistant_message = ChatMessage.objects.create(
        id=uuid.uuid4(),
        dialog=dialog,
        user=user,  # или отдельный пользователь-ассистент
        role='assistant',
        content=assistant_text
    )

    # --- Шаг 5: Возвращаем структуру ответа ---
    data = {
        'dialog_id': str(dialog.id),
        'dialog_name': dialog.name,
        'user_message': {
            'id': str(user_message.id),
            'content': user_message.content,
        },
        'assistant_message': {
            'id': str(assistant_message.id),
            'content': assistant_message.content,
        },
    }
    return Response(data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_dialogs(request):
    """
    Эндпоинт для получения списка диалогов пользователя.
    """
    user = request.user
    dialogs = ChatDialog.objects.filter(user=user).values('id', 'name', 'created_at', 'updated_at')
    
    return Response(dialogs, status=status.HTTP_200_OK)

# @api_view(['DELETE'])
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_dialog(request, dialog_id):
    """
    Эндпоинт для удаления диалога.
    """
    user = request.user
    dialog = get_object_or_404(ChatDialog, id=dialog_id, user=user)
    dialog.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dialog(request, dialog_id):
    """
    Эндпоинт для получения конкретного диалога.
    """
    user = request.user
    dialog = get_object_or_404(ChatDialog, id=dialog_id, user=user)
    
    messages = dialog.messages.values('id', 'role', 'content', 'file', 'created_at')
    
    return Response({
        'dialog_id': str(dialog.id),
        'dialog_name': dialog.name,
        'messages': list(messages),
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_template(request):
    """
    Эндпоинт для загрузки шаблона документа.
    """
    user = request.user
    if not user.is_superuser:
        return Response({'error': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    title = request.data.get('title')
    file = request.FILES.get('file')
    content = request.data.get('content')
    template=TemplateDocument.objects.create(
        title=title,
        tempfile=file,
        content=content,
    )
    template.save()
    return Response({
        'template_id': str(template.id),
        'title': template.title,
        'file_url': template.tempfile.url if template.tempfile else None,
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])#не нужно быть автори
@permission_classes([AllowAny])
def list_templates(request):
    """
    Эндпоинт для получения списка шаблонов документов.
    """
    templates = TemplateDocument.objects.all()
    serializer = TemplateDocumentSerializer(templates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_template(request, template_id):
    """
    Эндпоинт для получения конкретного шаблона документа.
    """
    user = request.user
    if not user.is_superuser:
        return Response({'error': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    
    template = get_object_or_404(TemplateDocument, id=template_id)
    
    return Response({
        'template_id': str(template.id),
        'title': template.title,
        'content': template.content,
        'file_url': template.tempfile.url if template.tempfile else None,
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_template(request, template_id):
    """
    Эндпоинт для удаления шаблона документа.
    """
    user = request.user
    if not user.is_superuser:
        return Response({'error': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    
    template = get_object_or_404(TemplateDocument, id=template_id, user=user)
    template.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)

