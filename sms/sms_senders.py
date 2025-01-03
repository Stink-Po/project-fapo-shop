from sms_ir import SmsIr
from decouple import config

sms_ir = SmsIr(
    api_key=config('SMS_API_KEY'),
    linenumber="insrt your number",
)


def otp_sender(number, otp):
    sms_ir.send_verify_code(
        number=int(number),
        template_id=272942,
        parameters=[
            {
                "name": "code",
                "value": otp,
            },
        ],
    )


def successful_payment(number, order_id):
    sms_ir.send_verify_code(
        number=int(number),
        template_id=683028,
        parameters=[
            {
                "name": "NUMBER",
                "value": order_id,
            },
        ],
    )


def send_post_code(number, code):
    sms_ir.send_verify_code(
        number=int(number),
        template_id=658794,
        parameters=[
            {
                "name": "POST",
                "value": code,
            },
        ],
    )

def send_cart_warning(number):
    sms_ir.send_verify_code(
        number=int(number),
        template_id=713739,
        parameters=[
            {
                "name": "ID",
                "value": "",
            },
        ],
    )

def send_ticket_response(number, ticket_id):
    sms_ir.send_verify_code(
        number=int(number),
        template_id=379195,
        parameters=[
            {
                "name": "ID",
                "value": ticket_id,
            },
        ],
    )


def event_sender(number:list, message):
    sms_ir.send_bulk_sms(
        numbers=number,
        linenumber=30007487124158,
        message=message,
    )