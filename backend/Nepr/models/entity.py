class Person:
    def __init__(self, address=None, affiliation=None, birthDate=None, birthPlace=None, deathDate=None, deathPlace=None, email=None, familyName=None,gender=None, givenName=None, jobTitle=None, nationality=None, name=None, node_uri=None):
        self.address = address
        self.affiliation = affiliation
        self.birthDate = birthDate
        self.birthPlace = birthPlace
        self.deathDate = deathDate
        self.deathPlace = deathPlace
        self.email = email
        self.familyName = familyName
        self.gender = gender
        self.givenName = givenName
        self.jobTitle = jobTitle
        self.nationality = nationality
        self.name = name
        self.node_uri = node_uri

    def set_address(self, address):
        self.address = address

    def set_affiliation(self, affiliation):
        self.affiliation = affiliation

    def set_birthDate(self, birthDate):
        self.birthDate = birthDate

    def set_birthPlace(self, birthPlace):
        self.birthPlace = birthPlace

    def set_deathDate(self, deathDate):
        self.deathDate = deathDate

    def set_deathPlace(self, deathPlace):
        self.deathPlace = deathPlace

    def set_email(self, email):
        self.email = email

    def set_familyName(self, familyName):
        self.familyName = familyName

    def set_gender(self,gender):
        self.gender = gender

    def set_givenName(self, givenName):
        self.givenName = givenName

    def set_jobTitle(self, jobTitle):
        self.jobTitle = jobTitle

    def set_nationality(self, nationality):
        self.nationality = nationality

    def set_name(self, name):
        self.name = name

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri

    def __dict__(self):
        return {k: v for k, v in {
            "address": self.address,
            "affiliation": self.affiliation,
            "birthDate": self.birthDate,
            "birthPlace": self.birthPlace,
            "deathDate": self.deathDate,
            "deathPlace": self.deathPlace,
            "email": self.email,
            "familyName": self.familyName,
            "gender": self.gender,
            "givenName": self.givenName,
            "jobTitle": self.jobTitle,
            "nationality": self.nationality,
            "name": self.name,
            "node_uri": self.node_uri
        }.items() if v is not None}

class Organization:
    def __init__(self, name=None, address=None, publishingPrinciples=None, node_uri=None):
        self.address = address
        self.name = name
        self.publishingPrinciples = publishingPrinciples
        self.node_uri = node_uri

    def set_address(self, address):
        self.address = address

    def set_name(self, name):
        self.name = name

    def set_publishingPrinciples(self, publishingPrinciples):
        self.publishingPrinciples = publishingPrinciples

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri

    def __dict__(self):
        return {k: v for k, v in {
            "address": self.address,
            "name": self.name,
            "publishingPrinciples": self.publishingPrinciples,
            "node_uri": self.node_uri
        }.items() if v is not None}


class Author:
    def __init__(self, type, **kwargs):
        self.type = type
        if type == "Person":
            self.entity = Person(**kwargs)
        else:
            self.entity = Organization(**kwargs)

    def __dict__(self):
        def convert_to_dict(value):
            return value.__dict__()
        return {**convert_to_dict(self.entity), "type": self.type}


class Editor:
    def __init__(self, **kwargs):
        self.entity = Person(**kwargs)
        self.type = "Person"

    def __dict__(self):
        def convert_to_dict(value):
            return value.__dict__()
        return {**convert_to_dict(self.entity), "type": self.type}

class Publisher:
    def __init__(self, type, **kwargs):
        self.type = type
        if type == "Organization":
            self.entity = Organization(**kwargs)
        else:
            self.entity = Person(**kwargs)

    def __dict__(self):
        def convert_to_dict(value):
            return value.__dict__()
        return {**convert_to_dict(self.entity), "type": self.type}

# #Example usage
# # Create Person object
# person = Person(
#     name="John Doe",
#     givenName="John",
#     familyName="Doe",
#     birthDate="2000-01-01",
#     email="johndoe@email.com")
# # Create Author of type Person
# author = Author("Person", **person.__dict__())
# print(author.__dict__())
# print(author.entity.givenName)
# # Create Organization object
# organization = Organization(
#     name="Example Organization",
#     address="123 Example St, Example City, EX")
# # Create Publisher of type Organization
# publisher = Publisher("Organization", **organization.__dict__())
# print(publisher.__dict__())
