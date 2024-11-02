from django.shortcuts import render

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

import aiohttp
from asgiref.sync import sync_to_async


@sync_to_async
def handle_message(sender_id, message_text):
    response_text = f"Salom! Siz yozdingiz: {message_text}"
    return send_message(sender_id, response_text)


async def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            return await response.json()


@csrf_exempt
async def messenger_webhook(request):
    if request.method == 'GET':
        if request.GET.get("hub.verify_token") == VERIFY_TOKEN:
            return HttpResponse(request.GET.get("hub.challenge"))
        return HttpResponse("Invalid verification token")

    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                sender_id = event['sender']['id']
                if 'message' in event:
                    message_text = event['message'].get('text')
                    await handle_message(sender_id, message_text)
        return JsonResponse({"status": "ok"})
