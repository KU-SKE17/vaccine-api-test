""" Test Registration API endpoint of World Class Government """
import unittest
import datetime
import requests

HOST = "https://wcg-apis-test.herokuapp.com"
URL = HOST + "/registration"
FEEDBACK = {
    'success':              'registration success!',
    'missing_key':          'registration failed: missing some attribute',
    'registered':           'registration failed: this person already registered',
    'invalid_id':           'registration failed: invalid citizen ID',
    'invalid_birthdate':    'registration failed: invalid birth date format',
    'invalid_age':          'registration failed: not archived minimum age',
    'other':                'registration failed: something go wrong, please contact admin'
}


class RegistrationTest(unittest.TestCase):
    """
    Unit tests for Registration API from web wcg-apis-test.herokuapp.com

    @author Nanthakarn Limkool
    """
    def setUp(self):
        # default payload to register a person
        self.person = self.create_payload()

        # del if citizen exist
        requests.delete(URL+'/'+self.person["citizen_id"])
        
        # same id, but difference name
        self.person_same_id = self.create_payload(firstname='John', lastname='Smith')

        # missing some attribute value
        self.missing_key_payloads = [
            self.create_payload(citizen_id=""),
            self.create_payload(firstname=""),
            self.create_payload(lastname=""),
            self.create_payload(birthdate=""),
            self.create_payload(occupation=""),
            self.create_payload(phone_number=""),
            self.create_payload(is_risk=""),
            self.create_payload(address="")
        ]

        # citizen_id is not the number of 13 digits
        self.invalid_citizen_id_payloads = [
            self.create_payload(citizen_id="123"),                  # 3 digits
            self.create_payload(citizen_id="123456789012345678"),   # 18 digits
            self.create_payload(citizen_id="111aaa222bbb3"),        # contain alphabets
            self.create_payload(citizen_id="1112223334445.55")      # float like string
        ]

        birthdate = datetime.date(2001, 7, 3)  # 20 years old

        # using valid birth_date formats
        self.valid_birthdate_formats = [
            self.create_payload(birthdate=birthdate.strftime("%d %b %Y")),  # 03 Jul 2001
            self.create_payload(birthdate=birthdate.strftime("%d-%m-%Y")),  # 03-07-2001
            self.create_payload(birthdate=birthdate.strftime("%Y-%m-%d")),  # 2001-07-03
            self.create_payload(birthdate=birthdate.strftime("%d/%m/%Y")),  # 03/07/2001
            self.create_payload(birthdate=birthdate.strftime("%Y/%m/%d")),  # 2001/07/03
        ]

        # using invalid birth_date formats
        self.invalid_birthdate_formats = [
            self.create_payload(birthdate=birthdate.strftime("%Y-%m-%d %H:%M:%S.%f")),  # 2001-07-03 00:00:00.000000
            self.create_payload(birthdate=birthdate.strftime("%Y %B, %d")),             # 2001 July, 3
            self.create_payload(birthdate=birthdate.strftime("%d %B %Y")),              # 03 July 2001
        ]

        # payload of citizen under 13 years old
        self.invalid_age = [
            self.create_payload(birthdate=datetime.date(2009, 7, 3).strftime("%d %b %Y")),  # 12 years old
            self.create_payload(birthdate=datetime.date(2015, 7, 3).strftime("%d %b %Y")),  # 6 years old
            self.create_payload(birthdate=datetime.date.today().strftime("%d %b %Y")),      # 0 years old
        ]

    def tearDown(self):
        # del created citizen
        requests.delete(URL+'/'+self.person["citizen_id"])

    def create_payload(
            self,
            citizen_id="1103900084081",
            firstname="Nanthakarn",
            lastname="Limkool",
            birthdate="3 Jul 2001",
            occupation="Student",
            phone_number="0900900990",
            is_risk="false",
            address="315/5 Phlabphla, Wang Thonglang, Bangkok 10312"):
        """Return new dict of API requested attributes.

        Args:
            citizen_id (str, optional): Identity Number of Citizen, Defaults to "1103900084081"
            firstname (str, optional): Firstname of the Citizen, Defaults to "Nanthakarn"
            lastname (str, optional): Lastname of the Citizen, Defaults to "Limkool"
            birthdate (str, optional): Birthdate of the Citizen, Defaults to "3 Jul 2001"
            occupation (str, optional): Occupation of the Citizen, Defaults to "Student"
            phone_number(str, optional): Phone number of the Citizen, Defaults to "0900900990",
            is_risk(str, optional): 7 COVID-risks medical conditions status of the Citizen, Defaults to "false",
            address (str, optional): Address of the Citizen, Defaults to "315/5 Phlabphla, Wang Thonglang, Bangkok 10312"

        Returns:
            Dict: payload of Registration API
        """
        return {
            'citizen_id': citizen_id,
            'name': firstname,
            'surname': lastname,
            'birth_date': birthdate,
            'occupation': occupation,
            'phone_number': phone_number,
            'is_risk': is_risk,
            'address': address
        }

    def get_feedback(self, response):
        """Return feedback of the response

        Args:
            response (Response): response returned from a request

        Returns:
            str: feedback
        """
        return response.json()['feedback']

    def test_register_a_person(self):
        """Test register a person with all valid attributes
        """
        # send request
        response = requests.post(URL, data=self.person)
        # check status code
        self.assertEqual(response.status_code, 201)
        # check feedback
        self.assertEqual(self.get_feedback(response), FEEDBACK['success'])

    def test_register_missing_key(self):
        """Test register a person with a missing attribute
        """
        for payload in self.missing_key_payloads:
            # send request
            response = requests.post(URL, data=payload)
            # check feedback
            self.assertEqual(self.get_feedback(response), FEEDBACK['missing_key'])

    def test_register_twice(self):
        """Test register same person twice
        """
        # send requests
        response1 = requests.post(URL, data=self.person)
        response2 = requests.post(URL, data=self.person)
        # check feedback
        self.assertEqual(self.get_feedback(response1), FEEDBACK['success'])
        self.assertEqual(self.get_feedback(response2), FEEDBACK['registered'])

    def test_register_exist_citizen_id(self):
        """Test register two persons with the same citizen_id
        """
        # send requests
        response1 = requests.post(URL, data=self.person)
        response2 = requests.post(URL, data=self.person_same_id)
        # check feedback
        self.assertEqual(self.get_feedback(response1), FEEDBACK['success'])
        self.assertEqual(self.get_feedback(response2), FEEDBACK['registered'])

    def test_register_invalid_citizen_id(self):
        """Test register a person with invalid citizen_id
        """
        for payload in self.invalid_citizen_id_payloads:
            # send request
            response = requests.post(URL, data=payload)
            # check feedback
            self.assertEqual(self.get_feedback(response), FEEDBACK['invalid_id'])

    def test_register_valid_birthdate_formats(self):
        """Test register a person with all available birthdate formats
        """
        for payload in self.valid_birthdate_formats:
            # send request
            response = requests.post(URL, data=payload)
            # check feedback
            self.assertEqual(self.get_feedback(response), FEEDBACK['success'])
            # del the citizen
            requests.delete(URL+'/'+payload["citizen_id"])

    def test_register_invalid_birthdate_formats(self):
        """Test register a person with invalid birthdate formats
        """
        for payload in self.invalid_birthdate_formats:
            # send request
            response = requests.post(URL, data=payload)
            # check feedback
            self.assertEqual(self.get_feedback(response), FEEDBACK['invalid_birthdate'])

    def test_register_variance_age(self):
        """Test register a person with variance age
        """
        # check people under 13 years old
        for payload in self.invalid_age:
            # send request
            response = requests.post(URL, data=payload)
            # check feedback
            self.assertEqual(self.get_feedback(response), FEEDBACK['invalid_age'])

        # person of age 13 years old
        person = self.create_payload(birthdate=datetime.date(2008, 7, 3).strftime("%d %b %Y"))
        # send request
        response = requests.post(URL, data=person)
        # check feedback
        self.assertEqual(self.get_feedback(response), FEEDBACK['success'])


if __name__ == '__main__':
    unittest.main()
