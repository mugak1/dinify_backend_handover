import requests, datetime
import xml.etree.ElementTree as ET
from decouple import config
from finance_app.models import DinifyTransaction
from dataclasses import dataclass


@dataclass
class DpoIntegration:

    amount: int
    currency: str
    msisdn: str
    transaction_reference: str
    timestamp: str
    dpo_transaction_token: str

    API_URL = 'https://secure.3gdirectpay.com/API/v6/'
    PAYMENT_URL = 'https://secure.3gdirectpay.com/payv3.php?ID='
    COMPANY_TOKEN = config('DPO_COMPANY_TOKEN')
    SERVICE_TYPE = config('DPO_SERVICE_TYPE')
    REDIRECT_URL = 'https://dinify-web'

    def create_token(self):
        """
        - Creates a token with DPO to enable a user make a payment for their order
        """
        print(self.timestamp)
        api3g = ET.Element('API3G')
        request = ET.SubElement(api3g, 'Request')
        request.text = 'createToken'
        company_token = ET.SubElement(api3g, 'CompanyToken')
        company_token.text = self.COMPANY_TOKEN
        # the transaction details
        transaction = ET.SubElement(api3g, 'Transaction')
        payment_amount = ET.SubElement(transaction, 'PaymentAmount')
        payment_amount.text = str(self.amount)
        payment_currency = ET.SubElement(transaction, 'PaymentCurrency')
        payment_currency.text = self.currency
        company_ref_unique = ET.SubElement(transaction, 'CompanyRefUnique')
        company_ref_unique.text = '1'  # confirm that we are not doing payments
        company_ref = ET.SubElement(transaction, 'CompanyRef')
        company_ref.text = self.transaction_reference
        redirect_url = ET.SubElement(transaction, 'RedirectURL')
        redirect_url.text = self.REDIRECT_URL
        # the service details
        services = ET.SubElement(api3g, 'Services')
        service = ET.SubElement(services, 'Service')
        service_type = ET.SubElement(service, 'ServiceType')
        service_type.text = self.SERVICE_TYPE
        service_description = ET.SubElement(service, 'ServiceDescription')
        service_description.text = 'Dinify Order Payment'
        service_date = ET.SubElement(service, 'ServiceDate')
        new_time = datetime.datetime.strptime(str(self.timestamp[:-13]), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
        # new_time = self.timestamp
        service_date.text = new_time

        REQUEST_HEADERS = {
            'Content-Type': 'text/xml',
            'Content-transfer-encoding': 'text'
        }

        post_data = ET.tostring(api3g, xml_declaration=True, encoding='utf-8')
        dpo_token_request = requests.post(
            self.API_URL,
            data=post_data,
            headers=REQUEST_HEADERS
        )
        response_xml_object = ET.fromstring(dpo_token_request.text)
        print('the string response from dpo is ', str(response_xml_object))

        """
        <API3G>
        <Result>000</Result>
        <ResultExplanation>Transaction created</ResultExplanation>
        <TransToken>D0F24D8E-193F-4F65-9418-7A3420FEBB48</TransToken>
        <TransRef>R21349961</TransRef>
        </API3G>
        """

        # <API3G><Result>000</Result><ResultExplanation>Transaction created</ResultExplanation><TransToken>A217F49D-2E92-4F11-8A50-CD43C9C269EC</TransToken><TransRef>R21350043</TransRef></API3G>'
        dpo_transaction_result = response_xml_object.find('Result')
        dpo_transaction_result_explanation = response_xml_object.find('ResultExplanation')
        dpo_transaction_token = response_xml_object.find('TransToken')
        dpo_transaction_ref = response_xml_object.find('TransRef')

        print(
            dpo_transaction_result.text,
            dpo_transaction_result_explanation.text,
            dpo_transaction_token.text,
            dpo_transaction_ref.text
        )

        # return None

        # update the transaction to have the new details
        txs = DinifyTransaction.objects.get(id=self.transaction_reference)
        txs.aggregator = 'DPO'
        txs.aggregator_misc_details = {
            'transaction_token': dpo_transaction_token.text,
            'transaction_reference': dpo_transaction_ref.text,
            'result': dpo_transaction_result.text,
            'result_explanation': dpo_transaction_result_explanation.text
        }
        if dpo_transaction_result.text == '000':
            txs.aggregator_reference = dpo_transaction_ref.text
        else:
            txs.transaction_status = 'Failed'
        txs.save()

        # return only the token
        if dpo_transaction_result.text == '000':
            # return dpo_transaction_token.text
            return f'{self.PAYMENT_URL}{dpo_transaction_token.text}'
        return None

    def verify_token(self):
        # <?xml version="1.0" encoding="utf-8"?>
        # <API3G>
        # <CompanyToken>57466282-EBD7-4ED5-B699-8659330A6996</CompanyToken>
        # <Request>verifyToken</Request>
        # <TransactionToken>72983CAC-5DB1-4C7F-BD88-352066B71592</TransactionToken>
        # </API3G>
        api3g = ET.Element('API3G')
        company_token = ET.SubElement(api3g, 'CompanyToken')
        company_token.text = self.COMPANY_TOKEN
        request = ET.SubElement(api3g, 'Request')
        request.text = 'verifyToken'
        transaction_token = ET.SubElement(api3g, 'TransactionToken')
        transaction_token.text = self.dpo_transaction_token

        REQUEST_HEADERS = {
            'Content-Type': 'text/xml',
            'Content-transfer-encoding': 'text'
        }

        post_data = ET.tostring(api3g, xml_declaration=True, encoding='utf-8')
        dpo_response = requests.post(
            self.API_URL,
            data=post_data,
            headers=REQUEST_HEADERS
        )
        print(dpo_response)
        response_xml_object = ET.fromstring(dpo_response.text)
        print('the string response from dpo is ', str(response_xml_object))

        # <?xml version="1.0" encoding="utf-8"?>
        # <API3G>
        # <Result>000</Result>
        # <ResultExplanation>Transaction paid</ResultExplanation>
        # <CustomerName >John Doe</CustomerName >
        # <CustomerCredit>4432</CustomerCredit>
        # <TransactionApproval>938204312</TransactionApproval>
        # <TransactionCurrency>USD</TransactionCurrency>
        # <TransactionAmount>950.00</TransactionAmount>
        # <FraudAlert>000</FraudAlert>
        # <FraudExplnation>No Fraud detected</FraudExplnation>
        # <TransactionNetAmount>945</TransactionNetAmount>
        # <TransactionSettlementDate>2013/12/31</TransactionSettlementDate>
        # <TransactionRollingReserveAmount>5</TransactionRollingReserveAmount>
        # <TransactionRollingReserveDate>2014/12/31</TransactionRollingReserveDate>
        # <CustomerPhone>254123456789</CustomerPhone>
        # <CustomerCountry>KE</CustomerCountry>
        # <CustomerAddress>Stranfe blvd.</CustomerAddress>
        # <CustomerCity>Nairobi</CustomerCity>
        # <CustomerZip>AH1</CustomerZip>
        # <MobilePaymentRequest>Sent</MobilePaymentRequest>
        # <AccRef>ABC123REF</AccRef>
        # </API3G>
        dpo_transaction_result = response_xml_object.find('Result')
        dpo_transaction_result_explanation = response_xml_object.find('ResultExplanation')
        dpo_transaction_customer_name = response_xml_object.find('CustomerName')
        dpo_customer_credit = response_xml_object.find('CustomerCredit')
        dpo_transaction_approval = response_xml_object.find('TransactionApproval')
        dpo_transaction_currency = response_xml_object.find('TransactionCurrency')
        dpo_transaction_amount = response_xml_object.find('TransactionAmount')
        dpo_fraud_alert = response_xml_object.find('FraudAlert')
        dpo_fraud_explanation = response_xml_object.find('FraudExplnation')
        dpo_transaction_net_amount = response_xml_object.find('TransactionNetAmount')
        dpo_transaction_settlement_date = response_xml_object.find('TransactionSettlementDate')
        dpo_transaction_rolling_reserve_amount = response_xml_object.find('TransactionRollingReserveAmount')
        dpo_transaction_rolling_reserve_date = response_xml_object.find('TransactionRollingReserveDate')
        dpo_customer_phone = response_xml_object.find('CustomerPhone')
        dpo_customer_country = response_xml_object.find('CustomerCountry')
        dpo_customer_address = response_xml_object.find('CustomerAddress')
        dpo_customer_city = response_xml_object.find('CustomerCity')
        dpo_customer_zip = response_xml_object.find('CustomerZip')
        dpo_mobile_payment_request = response_xml_object.find('MobilePaymentRequest')
        dpo_acc_ref = response_xml_object.find('AccRef')
        misc_details = {
            'dpo_transaction_token': self.dpo_transaction_token,
            'transaction_result': dpo_transaction_result.text if dpo_transaction_result is not None else None,
            'transaction_result_explanation': dpo_transaction_result_explanation.text if dpo_transaction_result_explanation is not None else None,
            'customer_name': dpo_transaction_customer_name.text if dpo_transaction_customer_name is not None else None,
            'customer_credit': dpo_customer_credit.text if dpo_customer_credit is not None else None,
            'transaction_approval': dpo_transaction_approval.text if dpo_transaction_approval is not None else None,
            'transaction_currency': dpo_transaction_currency.text if dpo_transaction_currency is not None else None,
            'transaction_amount': dpo_transaction_amount.text if dpo_transaction_amount is not None else None,
            'fraud_alert': dpo_fraud_alert.text if dpo_fraud_alert is not None else None,
            'fraud_explanation': dpo_fraud_explanation.text if dpo_fraud_explanation is not None else None,
            'transaction_net_amount': dpo_transaction_net_amount.text if dpo_transaction_net_amount is not None else None,
            'transaction_settlement_date': dpo_transaction_settlement_date.text if dpo_transaction_settlement_date is not None else None,
            'transaction_rolling_reserve_amount': dpo_transaction_rolling_reserve_amount.text if dpo_transaction_rolling_reserve_amount is not None else None,
            'transaction_rolling_reserve_date': dpo_transaction_rolling_reserve_date.text if dpo_transaction_rolling_reserve_date is not None else None,
            'customer_phone': dpo_customer_phone.text if dpo_customer_phone is not None else None,
            'customer_country': dpo_customer_country.text if dpo_customer_country is not None else None,
            'customer_address': dpo_customer_address.text if dpo_customer_address is not None else None,
            'customer_city': dpo_customer_city.text if dpo_customer_city is not None else None,
            'customer_zip': dpo_customer_zip.text if dpo_customer_zip is not None else None,
            'mobile_payment_request': dpo_mobile_payment_request.text if dpo_mobile_payment_request is not None else None,
            'acc_ref': dpo_acc_ref.text if dpo_acc_ref is not None else None
        }

        print(misc_details)

        return {
            'status': 200,
            'message': 'Token verified',
        }
