import unittest
from models.entity import Person, Organization, Author, Editor, Publisher

class TestEntityModels(unittest.TestCase):

    def test_person_dict(self):
        person = Person(
            address="123 Example St",
            affiliation="Example Affiliation",
            birthDate="2000-01-01",
            birthPlace="Example City",
            deathDate="2070-01-01",
            deathPlace="Example City",
            email="johndoe@email.com",
            familyName="Doe",
            gender="Male",
            givenName="John",
            jobTitle="Developer",
            nationality="Example Nationality",
            name="John Doe",
            node_uri="node_uri"
        )
        expected_dict = {
            "address": "123 Example St",
            "affiliation": "Example Affiliation",
            "birthDate": "2000-01-01",
            "birthPlace": "Example City",
            "deathDate": "2070-01-01",
            "deathPlace": "Example City",
            "email": "johndoe@email.com",
            "familyName": "Doe",
            "gender": "Male",
            "givenName": "John",
            "jobTitle": "Developer",
            "nationality": "Example Nationality",
            "name": "John Doe",
            "node_uri": "node_uri"
        }
        self.assertEqual(person.__dict__(), expected_dict)

    def test_organization_dict(self):
        organization = Organization(
            name="Example Organization",
            address="123 Example St",
            publishingPrinciples="Example Principles",
            node_uri="node_uri"
        )
        expected_dict = {
            "name": "Example Organization",
            "address": "123 Example St",
            "publishingPrinciples": "Example Principles",
            "node_uri": "node_uri"
        }
        self.assertEqual(organization.__dict__(), expected_dict)

    def test_author_person_dict(self):
        author = Author(
            type="Person",
            name="John Doe",
            givenName="John",
            familyName="Doe",
            birthDate="2000-01-01",
            email="johndoe@email.com",
            node_uri = "node_uri"
        )
        expected_dict = {
            "type": "Person",
            "name": "John Doe",
            "givenName": "John",
            "familyName": "Doe",
            "birthDate": "2000-01-01",
            "email": "johndoe@email.com",
            "node_uri": "node_uri"
        }
        self.assertEqual(author.__dict__(), expected_dict)

    def test_author_organization_dict(self):
        author = Author(
            type="Organization",
            name="Example Organization",
            address="123 Example St",
            node_uri = "node_uri"
        )
        expected_dict = {
            "type": "Organization",
            "name": "Example Organization",
            "address": "123 Example St",
            "node_uri": "node_uri"
        }
        self.assertEqual(author.__dict__(), expected_dict)

    def test_editor_dict(self):
        editor = Editor(
            name="Jane Smith",
            givenName="Jane",
            familyName="Smith",
            email="janesmith@email.com",
            node_uri = "node_uri"
        )
        expected_dict = {
            "name": "Jane Smith",
            "givenName": "Jane",
            "familyName": "Smith",
            "email": "janesmith@email.com",
            "type": "Person",
            "node_uri": "node_uri"
        }
        self.assertEqual(editor.__dict__(), expected_dict)

    def test_publisher_organization_dict(self):
        publisher = Publisher(
            type="Organization",
            name="Example Organization",
            address="123 Example St",
            node_uri = "node_uri"
        )
        expected_dict = {
            "type": "Organization",
            "name": "Example Organization",
            "address": "123 Example St",
            "node_uri": "node_uri"
        }
        self.assertEqual(publisher.__dict__(), expected_dict)

    def test_publisher_person_dict(self):
        publisher = Publisher(
            type="Person",
            name="John Doe",
            givenName="John",
            familyName="Doe",
            birthDate="2000-01-01",
            email="johndoe@email.com",
            node_uri = "node_uri"
        )
        expected_dict = {
            "type": "Person",
            "name": "John Doe",
            "givenName": "John",
            "familyName": "Doe",
            "birthDate": "2000-01-01",
            "email": "johndoe@email.com",
            "node_uri": "node_uri"
        }
        self.assertEqual(publisher.__dict__(), expected_dict)

    def test_set_address(self):
        person = Person()
        person.set_address("123 Example St")
        self.assertEqual(person.address, "123 Example St")

    def test_set_affiliation(self):
        person = Person()
        person.set_affiliation("Example Affiliation")
        self.assertEqual(person.affiliation, "Example Affiliation")

    def test_set_birthDate(self):
        person = Person()
        person.set_birthDate("2000-01-01")
        self.assertEqual(person.birthDate, "2000-01-01")

    def test_set_birthPlace(self):
        person = Person()
        person.set_birthPlace("Example City")
        self.assertEqual(person.birthPlace, "Example City")

    def test_set_deathDate(self):
        person = Person()
        person.set_deathDate("2070-01-01")
        self.assertEqual(person.deathDate, "2070-01-01")

    def test_set_deathPlace(self):
        person = Person()
        person.set_deathPlace("Example City")
        self.assertEqual(person.deathPlace, "Example City")

    def test_set_email(self):
        person = Person()
        person.set_email("johndoe@email.com")
        self.assertEqual(person.email, "johndoe@email.com")

    def test_set_familyName(self):
        person = Person()
        person.set_familyName("Doe")
        self.assertEqual(person.familyName, "Doe")

    def test_set_gender(self):
        person = Person()
        person.set_gender("Male")
        self.assertEqual(person.gender, "Male")

    def test_set_givenName(self):
        person = Person()
        person.set_givenName("John")
        self.assertEqual(person.givenName, "John")

    def test_set_jobTitle(self):
        person = Person()
        person.set_jobTitle("Developer")
        self.assertEqual(person.jobTitle, "Developer")

    def test_set_nationality(self):
        person = Person()
        person.set_nationality("Example Nationality")
        self.assertEqual(person.nationality, "Example Nationality")

    def test_set_name(self):
        person = Person()
        person.set_name("John Doe")
        self.assertEqual(person.name, "John Doe")

    def test_set_person_node_uri(self):
        person = Person()
        person.set_node_uri("http://example.com/person")
        self.assertEqual(person.node_uri, "http://example.com/person")

    def test_set_organization_name(self):
        organization = Organization()
        organization.set_name("Example Organization")
        self.assertEqual(organization.name, "Example Organization")

    def test_set_organization_nod_uri(self):
        organization = Organization()
        organization.set_node_uri("http://example.com/organization")
        self.assertEqual(organization.node_uri, "http://example.com/organization")

    def test_set_organization_address(self):
        organization = Organization()
        organization.set_address("123 Example St")
        self.assertEqual(organization.address, "123 Example St")

    def test_set_publishingPrinciples(self):
        organization = Organization()
        organization.set_publishingPrinciples("Example Principles")
        self.assertEqual(organization.publishingPrinciples, "Example Principles")

if __name__ == '__main__':
    unittest.main()