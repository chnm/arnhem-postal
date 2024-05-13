from django.core.management.base import BaseCommand
from django.db.models import Q

from postcards.models import Person


class Command(BaseCommand):
    help = "Update the names in the Person model from the Object model."

    def handle(slef, *args, **options):
        people = Person.objects.filter(
            Q(first_name="None") | Q(last_name="None") | Q(title="None")
        )

        for person in people:
            if person.first_name == "None":
                person.first_name_unknown = True
                person.first_name = ""
            if person.last_name == "None":
                person.last_name_unknown = True
                person.last_name = ""
            if person.title == "None":
                person.title = ""
            if person.entity_name == "None":
                person.entity_name = ""
            person.save()
        print("Names updated")
