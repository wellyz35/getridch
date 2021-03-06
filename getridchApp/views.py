from builtins import type

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from . import apiMl
from . import apiApp
import json
import requests
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction, PostbackTemplateAction, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
# parser = WebhookParser('1e7ab9437dc85f54d08cf117425398ca')
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id=event.message.package_id,
                                                                     sticker_id=event.message.sticker_id)
                               )


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if text == 'Hello':
        line_bot_api.reply_message(event.reply_token, TextSendMessage('Hi There!!'))
    elif text.lower() == 'getridch':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='What you can do', title='Seller', actions=[CameraAction(label='Take a photo'),
                                                                            # CameraRollAction(label='Choose a photo'),
                                                                            ]),
            CarouselColumn(text='What you can do', title='Buyer', actions=[
                PostbackAction(label='Get near by trash', data='getNearbyLocation', text='Show location'),
                # MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'menu':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Quick reply',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="getridch", data="getridch")
                        ),
                        QuickReplyButton(
                            action=CameraAction(label="Camera")
                        ),
                        QuickReplyButton(
                            action=CameraRollAction(label="Camera Roll")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="Location")
                        ),
                        QuickReplyButton(
                            action=DatetimePickerAction(label="Date",
                                                        data="data3",
                                                        mode="date")
                        ),
                    ])))
    elif text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Display name: ' + profile.user_id)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == 'flex':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[MessageAction(label='Yes', text='Yes!'),
                                                                   MessageAction(label='No', text='No!')])
        template_message = TemplateSendMessage(alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'list':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='What you can do', title='Seller', actions=[
                CameraAction(label='Take a photo'),
                PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='Options', title='Buyer', actions=[
                PostbackAction(label='Test ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'KBTG':
        confirm_template = ConfirmTemplate(text='Confirm Address : KBTG ?',
                                           actions=[PostbackAction(label='Confirm', data='cfaddress'),
                                                    PostbackAction(label='cancel', data='getridch',
                                                                   text='cancel'),
                                                    ])
        template_message = TemplateSendMessage(alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    # else:
    #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))
    elif event.postback.data == 'getNearbyLocation':
        data = apiApp.getNearbyAddress()
        text_message_list = [TextSendMessage(text='Line Id : ' + row[0] + ' Address : ' + row[1]) for row in data]
        line_bot_api.reply_message(
            event.reply_token, text_message_list)
    elif event.postback.data == 'location':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Please enter your location'))
    elif event.postback.data == 'getridch':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='What you can do', title='Seller', actions=[
                CameraAction(label='Take a photo'),
                # PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='What you can do', title='Buyer', actions=[
                PostbackAction(label='Get near by trash', data='getNearbyLocation', text='Show location'),
                # MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif event.postback.data == 'cfaddress':
        # apiApp.setSellerAddress('KBTG', 'well', '0970909591', 'KBTG')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Your order in queue!!'))


@handler.default()
def default(event):
    print(event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Currently Not Support None Text Message')
    )


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    data = apiMl.getObjectDetection(message_content.content)
    textStr = ''
    if data['qty_bottle'] > 0:
        textStr += 'Bottle : \n'
        textStr += '    Amount ' + str(data['qty_bottle']) + '\n'
        textStr += '    Price ' + str(data['prc_bottle']) + '\n'
    if data['qty_can'] > 0:
        textStr += 'Can : \n'
        textStr += '    Amount ' + str(data['qty_can']) + '\n'
        textStr += '    Price ' + str(data['prc_can']) + ' Baht\n'
    if data['qty_glass'] > 0:
        textStr += 'Glass : \n'
        textStr += '    Amount ' + str(data['qty_glass']) + '\n'
        textStr += '    Price ' + str(data['prc_glass']) + ' Baht\n'
    textStr += 'Total Price : ' + str(data['Total']) + ' Baht \n'
    textStr += '\n Confirm order? '
    print(textStr)

    confirm_template = ConfirmTemplate(text=textStr, actions=[PostbackAction(label='Confirm', data='location'),
                                                              PostbackAction(label='cancel', data='getridch',
                                                                             text='cancel'),
                                                              ])
    template_message = TemplateSendMessage(alt_text='Confirm alt text', template=confirm_template)
    line_bot_api.reply_message(event.reply_token, template_message)

    #
    # buttons_template = ButtonsTemplate(title='My stuff', text=textStr,
    #                                    actions=[PostbackAction(label='Confirm', data='location'),
    #                                             PostbackAction(label='cancel', data='cancel', text='cancel'),
    #                                             ])
    # template_message = TemplateSendMessage(alt_text='Buttons alt text', template=buttons_template)
    # line_bot_api.reply_message(event.reply_token, template_message)


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(title=event.message.title, address=event.message.address, latitude=event.message.latitude,
                            longitude=event.message.longitude
                            )
    )


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            print(LineBotApiError.message)
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
