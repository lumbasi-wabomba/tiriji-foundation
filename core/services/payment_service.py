import uuid

from django.utils import timezone


class PaymentService:
    METHOD_CONFIG = {
        'card': {
            'label': 'Card',
            'provider': 'Stripe Checkout',
            'action': 'Continue to card checkout',
            'instructions': [
                'Use this option for Visa, Mastercard, and other supported cards.',
                'Demo mode records the transaction and simulates gateway confirmation.',
            ],
        },
        'stripe': {
            'label': 'Stripe',
            'provider': 'Stripe Checkout',
            'action': 'Continue to Stripe',
            'instructions': [
                'Use this option for card payments through Stripe.',
                'Demo mode records the transaction and simulates gateway confirmation.',
            ],
        },
        'mpesa': {
            'label': 'M-Pesa',
            'provider': 'M-Pesa STK Push',
            'action': 'Send STK push',
            'instructions': [
                'The donor receives an M-Pesa prompt on their phone.',
                'Demo mode records the request and lets you confirm payment manually.',
            ],
        },
        'paypal': {
            'label': 'PayPal',
            'provider': 'PayPal Checkout',
            'action': 'Continue to PayPal',
            'instructions': [
                'Use this option for PayPal wallet and supported international payments.',
                'Demo mode records the transaction and simulates PayPal approval.',
            ],
        },
        'bank': {
            'label': 'Bank Transfer',
            'provider': 'Manual Bank Transfer',
            'action': 'Record bank transfer',
            'instructions': [
                'Transfer to Tiriji Foundation bank account using the reference shown below.',
                'Finance can reconcile the transfer from the admin portal.',
            ],
        },
    }

    @classmethod
    def reference(cls, prefix='TIR'):
        return f'{prefix}-{uuid.uuid4().hex[:10].upper()}'

    @classmethod
    def method_config(cls, method):
        return cls.METHOD_CONFIG.get(method) or cls.METHOD_CONFIG['card']

    @classmethod
    def donation_session(cls, donation):
        method = donation.payment_method or 'mpesa'
        config = cls.method_config(method)
        reference = donation.payment_reference or cls.reference('PAY')

        if donation.transaction and not donation.transaction.transaction_reference:
            donation.transaction.transaction_reference = reference
            donation.transaction.save(update_fields=['transaction_reference'])

        if not donation.payment_reference:
            donation.payment_reference = reference
            donation.save(update_fields=['payment_reference'])

        return {
            'kind': 'donation',
            'method': method,
            'config': config,
            'reference': reference,
            'amount': donation.amount,
            'currency': donation.currency,
            'is_subscription': donation.is_monthly,
        }

    @classmethod
    def volunteer_session(cls, volunteer_payment, method='mpesa'):
        config = cls.method_config(method)
        reference = volunteer_payment.payment_reference or cls.reference('VOL')

        if not volunteer_payment.payment_reference:
            volunteer_payment.payment_reference = reference
            volunteer_payment.save(update_fields=['payment_reference'])

        if volunteer_payment.transaction:
            update_fields = []
            if volunteer_payment.transaction.payment_method != method:
                volunteer_payment.transaction.payment_method = method
                update_fields.append('payment_method')
            if not volunteer_payment.transaction.transaction_reference:
                volunteer_payment.transaction.transaction_reference = reference
                update_fields.append('transaction_reference')
            if update_fields:
                volunteer_payment.transaction.save(update_fields=update_fields)

        return {
            'kind': 'volunteer',
            'method': method,
            'config': config,
            'reference': reference,
            'amount': volunteer_payment.amount,
            'currency': 'USD',
            'is_subscription': False,
        }

    @classmethod
    def complete_donation(cls, donation):
        donation.status = 'completed'
        donation.amount_paid = donation.amount
        donation.payment_date = timezone.now()
        if not donation.payment_reference:
            donation.payment_reference = cls.reference('PAY')
        donation.save(update_fields=['status', 'amount_paid', 'payment_date', 'payment_reference'])

        if donation.transaction:
            donation.transaction.status = 'paid'
            donation.transaction.transaction_reference = donation.payment_reference
            donation.transaction.save(update_fields=['status', 'transaction_reference'])

    @classmethod
    def complete_volunteer_payment(cls, volunteer_payment):
        volunteer_payment.paid = True
        if not volunteer_payment.payment_reference:
            volunteer_payment.payment_reference = cls.reference('VOL')
        volunteer_payment.save(update_fields=['paid', 'payment_reference'])

        volunteer_payment.transaction.status = 'paid'
        volunteer_payment.transaction.transaction_reference = volunteer_payment.payment_reference
        volunteer_payment.transaction.save(update_fields=['status', 'transaction_reference'])

        volunteer_payment.volunteer.status = 'paid'
        volunteer_payment.volunteer.save(update_fields=['status'])
